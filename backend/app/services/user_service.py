import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


async def create_user(db: AsyncSession, data: UserCreate) -> dict:
    """Регистрирует нового пользователя и выпускает для него токен доступа.

    Args:
        db (AsyncSession): Сессия подключения к базе данных.
        data (UserCreate): Данные регистрации (имя пользователя и пароль).

    Returns:
        dict: Словарь с ключами access_token, token_type и user (созданный пользователь).

    Raises:
        HTTPException: Если пользователь с таким именем уже существует (409).
    """
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким именем уже существует",
        )

    user = User(
        id=uuid.uuid4(),
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer", "user": user}


async def authenticate_user(db: AsyncSession, data: UserLogin) -> dict:
    """Проверяет логин и пароль пользователя и выпускает токен доступа при успехе.

    Args:
        db (AsyncSession): Сессия подключения к базе данных.
        data (UserLogin): Учетные данные пользователя (имя пользователя и пароль).

    Returns:
        dict: Словарь с ключами access_token, token_type и user (аутентифицированный пользователь).

    Raises:
        HTTPException: Если логин или пароль неверны (401), либо аккаунт деактивирован (403).
    """
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован",
        )

    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer", "user": user}


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Находит пользователя по его идентификатору.

    Args:
        db (AsyncSession): Сессия подключения к базе данных.
        user_id (str): Идентификатор пользователя в виде строки (UUID).

    Returns:
        User | None: Найденный пользователь, либо None, если пользователь не найден.
    """
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()
