import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.schemas.user import UserCreate, UserLogin
from app.services import user_service


class FakeResult:
    def __init__(self, value) -> None:
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeDatabase:
    def __init__(self, values) -> None:
        self.values = list(values)
        self.added = []
        self.commit_count = 0
        self.refreshed = []

    async def execute(self, statement):
        return FakeResult(self.values.pop(0))

    def add(self, value) -> None:
        self.added.append(value)

    async def commit(self) -> None:
        self.commit_count += 1

    async def refresh(self, value) -> None:
        self.refreshed.append(value)


def test_create_user_persists_user_and_returns_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = FakeDatabase([None])
    monkeypatch.setattr(user_service, "hash_password", lambda value: "hashed")
    monkeypatch.setattr(user_service, "create_access_token", lambda value: f"token:{value}")

    result = asyncio.run(
        user_service.create_user(
            db, UserCreate(username="student", password="secret1")
        )
    )

    assert db.added[0].username == "student"
    assert db.added[0].hashed_password == "hashed"
    assert db.commit_count == 1
    assert db.refreshed == db.added
    assert result["access_token"].startswith("token:")
    assert result["token_type"] == "bearer"
    assert result["user"] is db.added[0]


def test_create_user_rejects_duplicate_username() -> None:
    db = FakeDatabase([object()])

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            user_service.create_user(
                db, UserCreate(username="student", password="secret1")
            )
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert db.added == []


def test_authenticate_user_returns_token(monkeypatch: pytest.MonkeyPatch) -> None:
    user = SimpleNamespace(
        id=uuid4(), hashed_password="hashed", is_active=True, username="student"
    )
    db = FakeDatabase([user])
    monkeypatch.setattr(user_service, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(user_service, "create_access_token", lambda value: "token")

    result = asyncio.run(
        user_service.authenticate_user(
            db, UserLogin(username="student", password="secret1")
        )
    )

    assert result == {"access_token": "token", "token_type": "bearer", "user": user}


@pytest.mark.parametrize(
    ("user", "password_matches", "expected_status"),
    [
        (None, False, status.HTTP_401_UNAUTHORIZED),
        (
            SimpleNamespace(hashed_password="hashed", is_active=True),
            False,
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            SimpleNamespace(hashed_password="hashed", is_active=False),
            True,
            status.HTTP_403_FORBIDDEN,
        ),
    ],
)
def test_authenticate_user_rejects_invalid_or_inactive_user(
    monkeypatch: pytest.MonkeyPatch,
    user,
    password_matches: bool,
    expected_status: int,
) -> None:
    db = FakeDatabase([user])
    monkeypatch.setattr(
        user_service, "verify_password", lambda plain, hashed: password_matches
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            user_service.authenticate_user(
                db, UserLogin(username="student", password="secret1")
            )
        )

    assert exc_info.value.status_code == expected_status


def test_get_user_by_id_returns_database_result() -> None:
    user = object()
    db = FakeDatabase([user])

    assert asyncio.run(user_service.get_user_by_id(db, str(uuid4()))) is user
