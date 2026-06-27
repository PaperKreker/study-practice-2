import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api import users
from app.schemas.user import UserCreate, UserLogin


def credentials(token: str = "token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_get_current_user_returns_active_user(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = SimpleNamespace(is_active=True)
    fake_db = object()
    monkeypatch.setattr(users, "decode_access_token", lambda token: "user-id")

    async def fake_get_user_by_id(db, user_id: str):
        assert db is fake_db
        assert user_id == "user-id"
        return expected

    monkeypatch.setattr(users, "get_user_by_id", fake_get_user_by_id)

    result = asyncio.run(users.get_current_user(credentials(), db=fake_db))

    assert result is expected


def test_get_current_user_rejects_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(users, "decode_access_token", lambda token: None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(users.get_current_user(credentials(), db=object()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.parametrize("found_user", [None, SimpleNamespace(is_active=False)])
def test_get_current_user_rejects_missing_or_inactive_user(
    monkeypatch: pytest.MonkeyPatch,
    found_user,
) -> None:
    monkeypatch.setattr(users, "decode_access_token", lambda token: "user-id")

    async def fake_get_user_by_id(db, user_id: str):
        return found_user

    monkeypatch.setattr(users, "get_user_by_id", fake_get_user_by_id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(users.get_current_user(credentials(), db=object()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_delegates_to_service(monkeypatch: pytest.MonkeyPatch) -> None:
    body = UserCreate(username="student", password="secret1")
    fake_db = object()
    expected = {"access_token": "token"}

    async def fake_create_user(db, data):
        assert db is fake_db
        assert data is body
        return expected

    monkeypatch.setattr(users, "create_user", fake_create_user)

    assert asyncio.run(users.register(body, db=fake_db)) == expected


def test_login_delegates_to_service(monkeypatch: pytest.MonkeyPatch) -> None:
    body = UserLogin(username="student", password="secret1")
    fake_db = object()
    expected = {"access_token": "token"}

    async def fake_authenticate_user(db, data):
        assert db is fake_db
        assert data is body
        return expected

    monkeypatch.setattr(users, "authenticate_user", fake_authenticate_user)

    assert asyncio.run(users.login(body, db=fake_db)) == expected


def test_me_returns_dependency_result() -> None:
    current_user = object()

    assert asyncio.run(users.me(current_user)) is current_user
