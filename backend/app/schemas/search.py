from pydantic import BaseModel

class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    page_number: int | None = None
    text: str
    score: float
    highlights: list[str] = []
    