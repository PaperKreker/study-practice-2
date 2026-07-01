import bcrypt
from datetime import datetime, timedelta, timezone

import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt.

    Args:
        password (str): Пароль в открытом виде.

    Returns:
        str: Хеш пароля.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет соответствие пароля его хешу.

    Args:
        plain (str): Пароль в открытом виде, введенный пользователем.
        hashed (str): Ранее сохраненный хеш пароля.

    Returns:
        bool: True, если пароль верен, иначе False.
    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    """Создает подписанный JWT-токен доступа для указанного пользователя.

    Срок действия токена определяется настройкой access_token_expire_minutes.

    Args:
        user_id (str): Идентификатор пользователя, для которого выпускается токен.

    Returns:
        str: Закодированный JWT-токен.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str | None:
    """Декодирует и валидирует JWT-токен доступа.

    Args:
        token (str): JWT-токен, полученный от клиента.

    Returns:
        str | None: Идентификатор пользователя (sub) из токена, либо None,
        если токен недействителен, просрочен или подделан.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
