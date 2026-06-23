from pydantic import BaseModel
from uuid import UUID

class UploadResponse(BaseModel):
    document_id: UUID
    file_name: str
    size_bytes: int
    message: str
