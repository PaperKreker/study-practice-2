import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=False,  # True для отладки SQL-запросов
    pool_pre_ping=True,  # проверять соединение перед каждым использованием
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет асинхронную сессию базы данных как FastAPI-зависимость.

    Сессия автоматически закрывается по завершении обработки запроса
    благодаря контекстному менеджеру.

    Yields:
        AsyncSession: Активная сессия для выполнения запросов к БД.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Инициализирует схему базы данных, создавая все таблицы из метаданных моделей.

    Вызывается при старте приложения. Не удаляет и не изменяет существующие таблицы.
    """
    from app.models.base import Base

    logger.info("Инициализация схемы БД...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Схема БД готова.")


async def close_db() -> None:
    """Закрывает пул соединений с PostgreSQL.

    Вызывается при остановке приложения для корректного освобождения ресурсов.
    """
    await engine.dispose()
    logger.debug("Пул соединений с PostgreSQL закрыт.")
