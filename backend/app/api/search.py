from fastapi import APIRouter, status, HTTPException, Query
 
from app.schemas.search import SearchResponse
from app.services.search_service import search_documents

router = APIRouter(tags=["search"])

@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=SearchResponse
)
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    document_id: str | None = Query(None)
):
    try:
        results = await search_documents(query=q, page=page, size=size, document_id=document_id)
        return results
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при выполнении поиска."
        )
