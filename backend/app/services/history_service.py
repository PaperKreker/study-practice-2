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
    """Получает постраничную историю поисковых запросов конкретного пользователя.

    Args:
        db (AsyncSession): Сессия подключения к базе данных.
        user_id (str): Идентификатор пользователя в виде строки (UUID).
        limit (int, optional): Максимальное количество возвращаемых записей. По умолчанию 50.
        offset (int, optional): Смещение для пагинации. По умолчанию 0.

    Returns:
        tuple[list[SearchHistory], int]: Список записей истории текущей страницы
        (отсортированных по дате создания, от новых к старым) и общее количество
        записей пользователя.
    """
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
    """Удаляет всю историю поисковых запросов указанного пользователя.

    Args:
        db (AsyncSession): Сессия подключения к базе данных.
        user_id (str): Идентификатор пользователя в виде строки (UUID).

    Returns:
        int: Количество удаленных записей истории.
    """
    uid = uuid.UUID(user_id)
    result = await db.execute(delete(SearchHistory).where(SearchHistory.user_id == uid))
    await db.commit()
    return result.rowcount
