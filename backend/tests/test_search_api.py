import asyncio

import pytest
from fastapi import HTTPException

from app.api import search


def test_search_uses_page_size_and_document_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}
    fake_db = object()

    async def fake_search_documents(
        db,
        query: str,
        page: int,
        size: int,
        document_id: str | None = None,
    ) -> dict:
        captured.update(
            db=db,
            query=query,
            page=page,
            size=size,
            document_id=document_id,
        )
        return {"total": 1, "items": []}

    monkeypatch.setattr(search, "search_documents", fake_search_documents)

    search_handler = search.search.__wrapped__
    assert asyncio.run(
        search_handler(
            q="elastic", page=3, size=10, document_id="doc-1", db=fake_db
        )
    ) == {
        "total": 1,
        "items": [],
    }
    assert captured == {
        "db": fake_db,
        "query": "elastic",
        "page": 3,
        "size": 10,
        "document_id": "doc-1",
    }


def test_search_wraps_service_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_search_documents(*args, **kwargs) -> list[dict]:
        raise RuntimeError("search failed")

    monkeypatch.setattr(search, "search_documents", fake_search_documents)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            search.search.__wrapped__(
                q="elastic", page=1, size=10, document_id=None, db=object()
            )
        )

    assert exc_info.value.status_code == 500
