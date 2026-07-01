import io
import logging
from dataclasses import dataclass

import pdfplumber
from docx import Document as DocxDocument
from docx.text.paragraph import Paragraph
from docx.table import Table

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


@dataclass
class TextChunk:
    """Фрагмент текста, извлеченный из документа для дальнейшей индексации.

    Attributes:
        chunk_id (str): Уникальный идентификатор чанка в формате
            "{document_id}_{порядковый_номер}".
        page_number (int): Номер страницы (для PDF) или условный номер (для DOCX),
            с которой был извлечен текст.
        text (str): Содержимое текстового фрагмента.
    """

    chunk_id: str
    page_number: int
    text: str


def _split_into_chunks(
    text: str,
    page_number: int,
    chunk_id_offset: int,
    document_id: str,
) -> list[TextChunk]:
    """Разбивает сплошной массив текста на сегменты заданного размера с перекрытием.

    Args:
        text (str): Исходный текст, требующий разделения.
        page_number (int): Номер страницы, с которой был извлечен текст.
        chunk_id_offset (int): Числовое смещение для генерации уникального идентификатора чанка.
        document_id (str): Идентификатор родительского документа.

    Returns:
        list[TextChunk]: Итоговый список сформированных текстовых чанков.
    """
    chunks: list[TextChunk] = []
    start = 0
    local_id = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    chunk_id=f"{document_id}_{chunk_id_offset + local_id}",
                    page_number=page_number,
                    text=chunk_text,
                )
            )
            local_id += 1

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def parse_pdf(file_bytes: bytes, document_id: str) -> list[TextChunk]:
    """Извлекает текст из PDF-файла постранично и разбивает его на чанки.

    Пустые страницы пропускаются. Нумерация чанков внутри документа
    сквозная (продолжается от страницы к странице).

    Args:
        file_bytes (bytes): Содержимое PDF-файла в байтах.
        document_id (str): Идентификатор родительского документа.

    Returns:
        list[TextChunk]: Список текстовых чанков, извлеченных из всех страниц документа.
    """
    chunks: list[TextChunk] = []
    chunk_id_offset = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            if not text:
                logger.debug("Страница %d пустая, пропускаем.", page_number)
                continue

            page_chunks = _split_into_chunks(
                text, page_number, chunk_id_offset, document_id
            )
            chunks.extend(page_chunks)
            chunk_id_offset += len(page_chunks)

    logger.info("PDF: извлечено %d чанков.", len(chunks))
    return chunks


def _extract_table_as_text(table) -> str:
    """Преобразует таблицу DOCX в текстовое представление в виде строк с разделителями.

    Повторяющиеся подряд значения ячеек в строке схлопываются (убираются
    дубликаты, возникающие из-за объединенных ячеек). После первой строки
    (заголовка) добавляется визуальный разделитель.

    Args:
        table: Объект таблицы python-docx (docx.table.Table).

    Returns:
        str: Текстовое представление таблицы, где строки разделены переносами,
        а ячейки — символом "|".
    """
    rows: list[str] = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.strip() for cell in row.cells]
        deduped: list[str] = []
        for cell in cells:
            if not deduped or cell != deduped[-1]:
                deduped.append(cell)
        rows.append(" | ".join(deduped))
        if i == 0:
            rows.append("-" * 40)
    return "\n".join(rows)


def parse_docx(file_bytes: bytes, document_id: str) -> list[TextChunk]:
    """Извлекает текст из DOCX-файла (параграфы и таблицы) и разбивает его на чанки.

    Обходит тело документа в исходном порядке следования элементов, сохраняя
    как обычные параграфы, так и таблицы (преобразованные в текст). Пустые
    параграфы и таблицы без содержимого пропускаются. Весь извлеченный текст
    объединяется в единый блок и делится на чанки как одна условная страница.

    Args:
        file_bytes (bytes): Содержимое DOCX-файла в байтах.
        document_id (str): Идентификатор родительского документа.

    Returns:
        list[TextChunk]: Список текстовых чанков, извлеченных из документа.
    """
    doc = DocxDocument(io.BytesIO(file_bytes))

    body_elements: list[str] = []

    para_index = 0
    table_index = 0

    for child in doc.element.body:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

        if tag == "p":
            p_obj = Paragraph(child, doc)
            text = p_obj.text.strip()
            if text:
                body_elements.append(text)
                para_index += 1
        elif tag == "tbl":
            t_obj = Table(child, doc)
            table_text = _extract_table_as_text(t_obj)
            if table_text.strip():
                body_elements.append(table_text)
                table_index += 1

    full_text = "\n\n".join(body_elements)
    chunks = _split_into_chunks(
        full_text, page_number=1, chunk_id_offset=0, document_id=document_id
    )

    logger.info(
        "DOCX: извлечено %d чанков (параграфов: %d, таблиц: %d).",
        len(chunks),
        para_index,
        table_index,
    )
    return chunks


def parse_document(
    file_bytes: bytes, extension: str, document_id: str
) -> list[TextChunk]:
    """Определяет тип файла и вызывает соответствующий парсер для извлечения сырого текста.

    Args:
        file_bytes (bytes): Байт-код файла.
        extension (str): Расширение файла.
        document_id (str): Идентификатор родительского документа для привязки.

    Returns:
        list[TextChunk]: Список извлеченных текстовых фрагментов.

    Raises:
        ValueError: Если в функцию передан неподдерживаемый формат файла.
    """
    if extension == ".pdf":
        return parse_pdf(file_bytes, document_id)
    elif extension == ".docx":
        return parse_docx(file_bytes, document_id)
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {extension}")
