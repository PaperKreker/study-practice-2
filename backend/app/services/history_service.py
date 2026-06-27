import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_history import SearchHistory


async def get_user_history(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[SearchHistory], int]:
    uid = uuid.UUID(user_id)

    count_result = await db.execute(
        select(func.count()).where(SearchHistory.user_id == uid)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == uid)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    items = list(result.scalars().all())

    return items, total


async def delete_user_history(db: AsyncSession, user_id: str) -> int:
    uid = uuid.UUID(user_id)
    result = await db.execute(delete(SearchHistory).where(SearchHistory.user_id == uid))
    await db.commit()
    return result.rowcount
