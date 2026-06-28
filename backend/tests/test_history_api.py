import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api import history


def test_get_history_returns_validated_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_user = SimpleNamespace(id=uuid4())
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
        assert requested_user_id == str(current_user.id)
        assert (limit, offset) == (10, 20)
        return [expected_item], 1

    monkeypatch.setattr(history, "get_user_history", fake_get_user_history)

    result = asyncio.run(
        history.get_history(
            limit=10,
            offset=20,
            db=fake_db,
            current_user=current_user,
        )
    )

    assert result.total == 1
    assert result.items[0].query == "elastic"
    assert result.items[0].results_count == 3


def test_delete_history_returns_service_result(monkeypatch: pytest.MonkeyPatch) -> None:
    current_user = SimpleNamespace(id=uuid4())
    fake_db = object()

    async def fake_delete_user_history(db, requested_user_id: str):
        assert db is fake_db
        assert requested_user_id == str(current_user.id)
        return 6

    monkeypatch.setattr(history, "delete_user_history", fake_delete_user_history)

    result = asyncio.run(history.delete_history(db=fake_db, current_user=current_user))

    assert result.deleted == 6
    assert "6" in result.message
