from pydantic import BaseModel

class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    page: int | None = None
    text: str
    score: float
    highlights: list[str] = []

class SearchResponse(BaseModel):
    total: int
    items: list[SearchResultItem]