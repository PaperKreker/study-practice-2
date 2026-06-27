from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: UUID
    query: str
    results_count: int
    created_at: datetime
    document_id: UUID | None = None

    model_config = {"from_attributes": True}


class HistoryListResponse(BaseModel):
    total: int
    items: list[HistoryItem]


class DeleteHistoryResponse(BaseModel):
    deleted: int
    message: str
