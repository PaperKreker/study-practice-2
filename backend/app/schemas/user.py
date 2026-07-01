from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    """Данные, необходимые для регистрации нового пользователя.

    Attributes:
        username (str): Имя пользователя.
        password (str): Пароль в открытом виде.
    """

    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        """Проверяет, что имя пользователя не пустое после удаления пробелов.

        Args:
            v (str): Введенное имя пользователя.

        Returns:
            str: Имя пользователя без ведущих/конечных пробелов.

        Raises:
            ValueError: Если имя пользователя пустое.
        """
        v = v.strip()
        if not v:
            raise ValueError("Имя пользователя не может быть пустым")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        """Проверяет длину пароля с учетом ограничений bcrypt.

        Args:
            v (str): Введенный пароль.

        Returns:
            str: Пароль, прошедший проверку.

        Raises:
            ValueError: Если пароль короче 6 символов или длиннее 72 байт в UTF-8
                (ограничение алгоритма bcrypt).
        """
        if len(v) < 6:
            raise ValueError("Пароль должен содержать не менее 6 символов")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Пароль слишком длинный")
        return v


class UserLogin(BaseModel):
    """Учетные данные для входа в систему.

    Attributes:
        username (str): Имя пользователя.
        password (str): Пароль в открытом виде.
    """

    username: str
    password: str


class UserResponse(BaseModel):
    """Публичное представление пользователя, возвращаемое клиенту.

    Attributes:
        id (UUID): Идентификатор пользователя.
        username (str): Имя пользователя.
        is_active (bool): Признак активности аккаунта.
        created_at (datetime): Дата и время регистрации.
    """

    id: UUID
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Ответ с токеном доступа после успешной аутентификации.

    Attributes:
        access_token (str): JWT-токен доступа.
        token_type (str): Тип токена (по умолчанию "bearer").
        user (UserResponse): Данные аутентифицированного пользователя.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
