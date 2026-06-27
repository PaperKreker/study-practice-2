import asyncio

import pytest

from app.core import elastic


class DummyElasticsearchClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_index_mapping_uses_russian_text_analyzer() -> None:
    text_mapping = elastic.INDEX_MAPPINGS["properties"]["text"]

    assert text_mapping["type"] == "text"
    assert text_mapping["analyzer"] == "russian"


def test_get_es_client_raises_when_not_initialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(elastic, "es_client", None)

    with pytest.raises(RuntimeError, match="не инициализирован"):
        elastic.get_es_client()


def test_get_es_client_returns_initialized_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DummyElasticsearchClient()
    monkeypatch.setattr(elastic, "es_client", client)

    assert elastic.get_es_client() is client


def test_close_elasticsearch_closes_and_clears_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = DummyElasticsearchClient()
    monkeypatch.setattr(elastic, "es_client", client)

    asyncio.run(elastic.close_elasticsearch())

    assert client.closed is True
    assert elastic.es_client is None


def test_close_elasticsearch_is_noop_without_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(elastic, "es_client", None)

    asyncio.run(elastic.close_elasticsearch())

    assert elastic.es_client is None
