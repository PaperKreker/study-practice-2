import os
 
from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException, Query
 
from app.schemas.document import UploadResponse
from app.services.document_service import process_document, validate_file
from app.services.indexing_service import index_document_chunks
from app.services.document_service import create_document_metadata
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db


router = APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload", 
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse
)
async def upload(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    metadata, file_bytes = await validate_file(file)
 
    _, ext = os.path.splitext((file.filename or "").lower())
    chunks = await process_document(
        document_id=metadata["document_id"],
        file_name=metadata["file_name"],
        file_bytes=file_bytes,
        extension=ext,
    )

    try:
        await index_document_chunks(
            document_id=metadata["document_id"],
            file_name=metadata["file_name"],
            chunks=chunks
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении документа в поисковый индекс."
        )
    
    await create_document_metadata(db=db, metadata=metadata, chunk_count=len(chunks))
 
    return {
        **metadata,
        "message": f"Файл успешно загружен, разбит на {len(chunks)} чанков и проиндексирован",
    }
