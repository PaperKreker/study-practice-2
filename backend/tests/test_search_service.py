import asyncio
from uuid import uuid4

import pytest

from app.services import search_service


class DummyElasticsearchClient:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls = []

    async def search(self, index: str, body: dict) -> dict:
        self.calls.append({"index": index, "body": body})
        return self.response


class DummyDatabase:
    def __init__(self) -> None:
        self.added = []
        self.commit_count = 0

    def add(self, value) -> None:
        self.added.append(value)

    async def commit(self) -> None:
        self.commit_count += 1


def test_search_documents_builds_query_and_maps_hits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = {
        "hits": {
            "total": {"value": 12},
            "hits": [
                {
                    "_score": 3.5,
                    "_source": {
                        "chunk_id": "doc_0",
                        "document_id": "doc",
                        "file_name": "lecture.pdf",
                        "page_number": 4,
                        "text": "Elasticsearch text",
                    },
                    "highlight": {"text": ["<mark>Elasticsearch</mark> text"]},
                }
            ],
        }
    }
    client = DummyElasticsearchClient(response)
    db = DummyDatabase()
    document_id = str(uuid4())

    monkeypatch.setattr(search_service, "get_es_client", lambda: client)
    monkeypatch.setattr(search_service.settings, "elasticsearch_index", "documents")

    results = asyncio.run(
        search_service.search_documents(
            db=db,
            query="elastic",
            page=3,
            size=5,
            document_id=document_id,
        )
    )

    assert client.calls == [
        {
            "index": "documents",
            "body": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": "elastic",
                                    "fields": ["text", "file_name^2"],
                                    "fuzziness": "AUTO",
                                }
                            }
                        ],
                        "filter": [{"term": {"document_id": document_id}}],
                    }
                },
                "size": 5,
                "from": 10,
                "highlight": {
                    "fields": {
                        "text": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]}
                    }
                },
            },
        }
    ]
    assert results == {
        "total": 12,
        "items": [
            {
                "chunk_id": "doc_0",
                "document_id": "doc",
                "file_name": "lecture.pdf",
                "page": 4,
                "text": "Elasticsearch text",
                "score": 3.5,
                "highlights": ["<mark>Elasticsearch</mark> text"],
            }
        ],
    }
    assert db.commit_count == 1
    assert len(db.added) == 1
    assert db.added[0].query == "elastic"
    assert db.added[0].results_count == 12
    assert str(db.added[0].document_id) == document_id


def test_search_documents_omits_filter_without_document_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DummyElasticsearchClient({"hits": {"hits": []}})
    db = DummyDatabase()

    monkeypatch.setattr(search_service, "get_es_client", lambda: client)

    assert asyncio.run(search_service.search_documents(db=db, query="elastic")) == {
        "total": 0,
        "items": [],
    }
    assert "filter" not in client.calls[0]["body"]["query"]["bool"]
    assert db.commit_count == 1
    assert db.added[0].document_id is None


def test_search_documents_propagates_client_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingElasticsearchClient:
        async def search(self, index: str, body: dict) -> dict:
            raise RuntimeError("search failed")

    monkeypatch.setattr(
        search_service, "get_es_client", lambda: FailingElasticsearchClient()
    )

    with pytest.raises(RuntimeError, match="search failed"):
        asyncio.run(
            search_service.search_documents(db=DummyDatabase(), query="elastic")
        )
