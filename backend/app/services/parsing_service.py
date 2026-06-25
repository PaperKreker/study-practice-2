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
    chunk_id: str   # формат: "{document_id}_{порядковый_номер}"
    page_number: int
    text: str


def _split_into_chunks(
    text: str,
    page_number: int,
    chunk_id_offset: int,
    document_id: str,
) -> list[TextChunk]:
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
    chunks: list[TextChunk] = []
    chunk_id_offset = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            if not text:
                logger.debug("Страница %d пустая, пропускаем.", page_number)
                continue

            page_chunks = _split_into_chunks(text, page_number, chunk_id_offset, document_id)
            chunks.extend(page_chunks)
            chunk_id_offset += len(page_chunks)

    logger.info("PDF: извлечено %d чанков.", len(chunks))
    return chunks


def _extract_table_as_text(table) -> str:
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
        elif tag == "tbl":
            t_obj = Table(child, doc)
            table_text = _extract_table_as_text(t_obj)
            if table_text.strip():
                body_elements.append(table_text)

    full_text = "\n\n".join(body_elements)
    chunks = _split_into_chunks(full_text, page_number=1, chunk_id_offset=0, document_id=document_id)

    logger.info("DOCX: извлечено %d чанков (параграфов: %d, таблиц: %d).",
                len(chunks), para_index, table_index)
    return chunks


def parse_document(file_bytes: bytes, extension: str, document_id: str) -> list[TextChunk]:
    if extension == ".pdf":
        return parse_pdf(file_bytes, document_id)
    elif extension == ".docx":
        return parse_docx(file_bytes, document_id)
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {extension}")
