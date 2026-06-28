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


class DummyResult:
    def __init__(self, items) -> None:
        self.items = items

    def scalars(self):
        return self

    def all(self):
        return self.items


class DummyDatabase:
    def __init__(self, execute_results=None) -> None:
        self.added = []
        self.commit_count = 0
        self.execute_results = list(execute_results or [])
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return self.execute_results.pop(0)

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
    user_id = uuid4()

    monkeypatch.setattr(search_service, "get_es_client", lambda: client)
    monkeypatch.setattr(search_service.settings, "elasticsearch_index", "documents")

    results = asyncio.run(
        search_service.search_documents(
            db=db,
            query="elastic",
            user_id=user_id,
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
    assert db.added[0].user_id == user_id
    assert str(db.added[0].document_id) == document_id


def test_search_documents_omits_filter_without_document_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DummyElasticsearchClient({"hits": {"hits": []}})
    db = DummyDatabase()
    user_id = uuid4()

    monkeypatch.setattr(search_service, "get_es_client", lambda: client)

    assert asyncio.run(
        search_service.search_documents(db=db, query="elastic", user_id=user_id)
    ) == {
        "total": 0,
        "items": [],
    }
    assert "filter" not in client.calls[0]["body"]["query"]["bool"]
    assert db.commit_count == 1
    assert db.added[0].document_id is None
    assert db.added[0].user_id == user_id


def test_search_documents_filters_by_users_document_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = uuid4()
    document_ids = [uuid4(), uuid4()]
    db = DummyDatabase([DummyResult(document_ids)])
    client = DummyElasticsearchClient({"hits": {"hits": []}})
    monkeypatch.setattr(search_service, "get_es_client", lambda: client)

    result = asyncio.run(
        search_service.search_documents(
            db=db,
            query="private",
            user_id=user_id,
            filter_by_user=True,
        )
    )

    assert result == {"total": 0, "items": []}
    assert client.calls[0]["body"]["query"]["bool"]["filter"] == [
        {"terms": {"document_id": [str(value) for value in document_ids]}}
    ]
    assert len(db.statements) == 1
    assert db.added[0].user_id == user_id


def test_search_documents_returns_empty_when_user_has_no_documents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DummyElasticsearchClient({"hits": {"hits": []}})
    db = DummyDatabase([DummyResult([])])
    monkeypatch.setattr(search_service, "get_es_client", lambda: client)

    result = asyncio.run(
        search_service.search_documents(
            db=db,
            query="private",
            user_id=uuid4(),
            filter_by_user=True,
        )
    )

    assert result == {"total": 0, "items": []}
    assert client.calls == []
    assert db.commit_count == 0


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
            search_service.search_documents(
                db=DummyDatabase(), query="elastic", user_id=uuid4()
            )
        )
