from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: UUID
    file_name: str
    size_bytes: int
    message: str


class DocumentResponse(BaseModel):
    id: UUID
    file_name: str
    size_bytes: int
    chunk_count: int
    uploaded_at: datetime
    user_id: UUID | None = None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total: int
    items: list[DocumentResponse]
