from fastapi import APIRouter, Depends, status, HTTPException, Query

from app.schemas.search import SearchResponse
from app.services.search_service import search_documents
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from fastapi_cache.decorator import cache
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter(tags=["search"])


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=SearchResponse,
    summary="Поиск по документам",
)
@cache(expire=300)
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    document_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        response_data = await search_documents(
            db=db, query=q, user_id=current_user.id, page=page, size=size, document_id=document_id
        )
        return response_data
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при выполнении поиска.",
        )
