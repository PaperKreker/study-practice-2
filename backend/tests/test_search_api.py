import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api import search


def test_search_uses_page_size_and_document_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}
    fake_db = object()
    current_user = SimpleNamespace(id=uuid4())

    async def fake_search_documents(
        db,
        query: str,
        user_id,
        page: int,
        size: int,
        document_id: str | None = None,
        filter_by_user: bool = False,
    ) -> dict:
        captured.update(
            db=db,
            query=query,
            user_id=user_id,
            page=page,
            size=size,
            document_id=document_id,
            filter_by_user=filter_by_user,
        )
        return {"total": 1, "items": []}

    monkeypatch.setattr(search, "search_documents", fake_search_documents)

    search_handler = search.search.__wrapped__
    assert asyncio.run(
        search_handler(
            q="elastic",
            page=3,
            size=10,
            document_id="doc-1",
            my_docs=True,
            db=fake_db,
            current_user=current_user,
        )
    ) == {
        "total": 1,
        "items": [],
    }
    assert captured == {
        "db": fake_db,
        "query": "elastic",
        "user_id": current_user.id,
        "page": 3,
        "size": 10,
        "document_id": "doc-1",
        "filter_by_user": True,
    }


def test_search_wraps_service_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_search_documents(*args, **kwargs) -> list[dict]:
        raise RuntimeError("search failed")

    monkeypatch.setattr(search, "search_documents", fake_search_documents)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            search.search.__wrapped__(
                q="elastic",
                page=1,
                size=10,
                document_id=None,
                my_docs=False,
                db=object(),
                current_user=SimpleNamespace(id=uuid4()),
            )
        )

    assert exc_info.value.status_code == 500
