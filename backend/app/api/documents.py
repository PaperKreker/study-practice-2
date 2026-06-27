import os

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.schemas.document import DocumentListResponse, DocumentResponse, UploadResponse
from app.services.indexing_service import delete_document_chunks, index_document_chunks
from app.services.document_service import (
    create_document_metadata,
    delete_document_from_db,
    get_all_documents,
    get_document_by_id,
    process_document,
    validate_file,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse,
    summary="Загрузка документа (PDF или DOCX) и его разбиение на чанки",
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
            chunks=chunks,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении документа в поисковый индекс.",
        )

    await create_document_metadata(db=db, metadata=metadata, chunk_count=len(chunks))

    return {
        **metadata,
        "message": f"Файл успешно загружен, разбит на {len(chunks)} чанков и проиндексирован",
    }


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="Получить список документов",
)
async def list_documents(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_all_documents(db, limit=limit, offset=offset)
    return {"total": total, "items": items}


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Получить информацию о документе",
)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ {document_id} не найден",
        )
    return doc


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить документ и его чанки",
)
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ {document_id} не найден",
        )

    chunks_deleted = await delete_document_chunks(document_id)
    await delete_document_from_db(db, document_id)

    return {
        "document_id": document_id,
        "chunks_deleted": chunks_deleted,
        "message": f"Документ '{doc.file_name}' и его чанки удалены",
    }
