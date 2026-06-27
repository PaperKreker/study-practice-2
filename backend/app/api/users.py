from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.user_service import authenticate_user, create_user, get_user_by_id

router = APIRouter(prefix="/users", tags=["users"])

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenResponse,
    summary="Регистрация нового пользователя",
)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, body)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, body)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
