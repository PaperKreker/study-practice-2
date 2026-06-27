import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.history import DeleteHistoryResponse, HistoryItem, HistoryListResponse
from app.services.history_service import delete_user_history, get_user_history

router = APIRouter(prefix="/search/history", tags=["search history"])


def _parse_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректный UUID: {value!r}",
        )


@router.get(
    "/{user_id}",
    response_model=HistoryListResponse,
    summary="История поисковых запросов пользователя",
)
async def get_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    _parse_uuid(user_id)
    items, total = await get_user_history(db, user_id, limit=limit, offset=offset)
    return HistoryListResponse(
        total=total,
        items=[HistoryItem.model_validate(item) for item in items],
    )


@router.delete(
    "/{user_id}",
    response_model=DeleteHistoryResponse,
    summary="Очистить историю запросов пользователя",
)
async def delete_history(user_id: str, db: AsyncSession = Depends(get_db)):
    _parse_uuid(user_id)
    deleted = await delete_user_history(db, user_id)
    return DeleteHistoryResponse(
        deleted=deleted,
        message=f"Удалено {deleted} записей из истории",
    )
