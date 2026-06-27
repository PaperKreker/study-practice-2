import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.api import history


def test_parse_uuid_accepts_valid_value() -> None:
    value = uuid4()

    assert history._parse_uuid(str(value)) == value


def test_parse_uuid_rejects_invalid_value() -> None:
    with pytest.raises(HTTPException) as exc_info:
        history._parse_uuid("not-a-uuid")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_get_history_returns_validated_response(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = str(uuid4())
    expected_item = SimpleNamespace(
        id=uuid4(),
        query="elastic",
        results_count=3,
        created_at=datetime.now(timezone.utc),
        document_id=None,
    )
    fake_db = object()

    async def fake_get_user_history(db, requested_user_id, limit: int, offset: int):
        assert db is fake_db
        assert requested_user_id == user_id
        assert (limit, offset) == (10, 20)
        return [expected_item], 1

    monkeypatch.setattr(history, "get_user_history", fake_get_user_history)

    result = asyncio.run(
        history.get_history(user_id, limit=10, offset=20, db=fake_db)
    )

    assert result.total == 1
    assert result.items[0].query == "elastic"
    assert result.items[0].results_count == 3


def test_get_history_rejects_invalid_uuid_before_database_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def unexpected_call(*args, **kwargs):
        pytest.fail("database must not be queried for an invalid UUID")

    monkeypatch.setattr(history, "get_user_history", unexpected_call)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(history.get_history("invalid", limit=10, offset=0, db=object()))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_history_returns_service_result(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = str(uuid4())
    fake_db = object()

    async def fake_delete_user_history(db, requested_user_id: str):
        assert db is fake_db
        assert requested_user_id == user_id
        return 6

    monkeypatch.setattr(history, "delete_user_history", fake_delete_user_history)

    result = asyncio.run(history.delete_history(user_id, db=fake_db))

    assert result.deleted == 6
    assert "6" in result.message


def test_delete_history_rejects_invalid_uuid() -> None:
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(history.delete_history("invalid", db=object()))

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
