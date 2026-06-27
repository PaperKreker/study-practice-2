import asyncio

import pytest

from app.services import indexing_service
from app.services.parsing_service import TextChunk


class DummyElasticsearchClient:
    pass


def test_index_document_chunks_sends_bulk_actions(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}
    client = DummyElasticsearchClient()
    chunks = [
        TextChunk(chunk_id="doc_0", page_number=1, text="first"),
        TextChunk(chunk_id="doc_1", page_number=2, text="second"),
    ]

    async def fake_async_bulk(es, actions):
        captured["client"] = es
        captured["actions"] = list(actions)
        return len(captured["actions"]), []

    monkeypatch.setattr(indexing_service, "get_es_client", lambda: client)
    monkeypatch.setattr(indexing_service.helpers, "async_bulk", fake_async_bulk)
    monkeypatch.setattr(indexing_service.settings, "elasticsearch_index", "documents")

    indexed = asyncio.run(
        indexing_service.index_document_chunks(
            document_id="doc",
            file_name="lecture.pdf",
            chunks=chunks,
        )
    )

    assert indexed == 2
    assert captured["client"] is client
    assert captured["actions"] == [
        {
            "_index": "documents",
            "_id": "doc_0",
            "_source": {
                "chunk_id": "doc_0",
                "document_id": "doc",
                "file_name": "lecture.pdf",
                "page_number": 1,
                "text": "first",
            },
        },
        {
            "_index": "documents",
            "_id": "doc_1",
            "_source": {
                "chunk_id": "doc_1",
                "document_id": "doc",
                "file_name": "lecture.pdf",
                "page_number": 2,
                "text": "second",
            },
        },
    ]


def test_index_document_chunks_propagates_bulk_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_async_bulk(es, actions):
        raise RuntimeError("bulk failed")

    monkeypatch.setattr(indexing_service, "get_es_client", lambda: DummyElasticsearchClient())
    monkeypatch.setattr(indexing_service.helpers, "async_bulk", fake_async_bulk)

    with pytest.raises(RuntimeError, match="bulk failed"):
        asyncio.run(
            indexing_service.index_document_chunks(
                document_id="doc",
                file_name="lecture.pdf",
                chunks=[TextChunk(chunk_id="doc_0", page_number=1, text="first")],
            )
        )
