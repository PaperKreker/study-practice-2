from functools import partial
import logging
import os
import uuid
import anyio

from fastapi import HTTPException, UploadFile, status

from app.services.parsing_service import TextChunk, parse_document

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


async def validate_file(file: UploadFile) -> dict:
    filename = file.filename
    _, ext = os.path.splitext(filename.lower())

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допустимы только PDF и DOCX",
        )

    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла превышает 20 МБ",
        )

    document_id = str(uuid.uuid4())

    metadata = {
        "document_id": document_id,
        "file_name": filename,
        "size_bytes": file_size,
        "message": "Файл успешно загружен",
    }

    return metadata, contents


async def process_document(
    document_id: str,
    file_name: str,
    file_bytes: bytes,
    extension: str,
) -> list[TextChunk]:

    logger.info(
        "Начинаю обработку документа '%s' (id=%s, ext=%s, %d байт)",
        file_name,
        document_id,
        extension,
        len(file_bytes),
    )

    try:
        chunks = await anyio.to_thread.run_sync(
            partial(parse_document, file_bytes, extension, document_id)
        )
    except Exception as exc:
        logger.exception("Ошибка при парсинге документа '%s': %s", file_name, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось обработать файл: {exc}",
        )

    logger.info(
        "Документ '%s' успешно разбит на %d чанков.",
        file_name,
        len(chunks),
    )
    return chunks


async def create_document_metadata(
    db: AsyncSession, metadata: dict, chunk_count: int, user_id: uuid.UUID
) -> Document:
    db_document = Document(
        id=uuid.UUID(metadata["document_id"]),
        file_name=metadata["file_name"],
        size_bytes=metadata["size_bytes"],
        chunk_count=chunk_count,
        user_id=user_id,
    )
    db.add(db_document)
    await db.commit()
    return db_document


async def get_all_documents(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    user_id: uuid.UUID | None = None,  # Новый параметр
) -> tuple[list[Document], int]:

    query = select(Document)
    count_query = select(func.count()).select_from(Document)

    if user_id:
        query = query.where(Document.user_id == user_id)
        count_query = count_query.where(Document.user_id == user_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.order_by(Document.uploaded_at.desc()).limit(limit).offset(offset)
    )
    items = list(result.scalars().all())

    return items, total


async def get_document_by_id(db: AsyncSession, document_id: str) -> Document | None:
    try:
        uid = uuid.UUID(document_id)
    except ValueError:
        return None

    result = await db.execute(select(Document).where(Document.id == uid))
    return result.scalar_one_or_none()


async def delete_document_from_db(db: AsyncSession, document_id: str) -> bool:
    doc = await get_document_by_id(db, document_id)
    if not doc:
        return False
    await db.delete(doc)
    await db.commit()
    return True
