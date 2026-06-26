from functools import partial
import logging
import os
import uuid
import anyio
 
from fastapi import HTTPException, UploadFile, status
 
from app.services.parsing_service import TextChunk, parse_document

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
            detail="Допустимы только PDF и DOCX"
        )
        
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла превышает 20 МБ"
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
        file_name, document_id, extension, len(file_bytes),
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
        file_name, len(chunks),
    )
    return chunks

async def create_document_metadata(db: AsyncSession, metadata: dict, chunk_count: int) -> Document:
    db_document = Document(
        id=uuid.UUID(metadata["document_id"]),
        file_name=metadata["file_name"],
        size_bytes=metadata["size_bytes"],
        chunk_count=chunk_count,
        user_id=None,
    )
    db.add(db_document)
    await db.commit()
    return db_document
