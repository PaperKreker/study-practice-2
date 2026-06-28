from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.history import DeleteHistoryResponse, HistoryItem, HistoryListResponse
from app.services.history_service import delete_user_history, get_user_history
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter(prefix="/search/history", tags=["search history"])

@router.get(
    "",
    response_model=HistoryListResponse,
    summary="История поисковых запросов пользователя",
)
async def get_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await get_user_history(db, str(current_user.id), limit=limit, offset=offset)
    return HistoryListResponse(
        total=total,
        items=[HistoryItem.model_validate(item) for item in items],
    )

@router.delete(
    "",
    response_model=DeleteHistoryResponse,
    summary="Очистить историю запросов пользователя",
)
async def delete_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await delete_user_history(db, str(current_user.id))
    return DeleteHistoryResponse(
        deleted=deleted,
        message=f"Удалено {deleted} записей из вашей истории",
    )
