from types import SimpleNamespace
from uuid import uuid4

from app.core.redis import search_cache_key_builder


def search_handler() -> None:
    pass


def build_key(**overrides) -> str:
    values = {
        "q": "elastic",
        "page": 1,
        "size": 10,
        "document_id": None,
        "my_docs": False,
        "current_user": SimpleNamespace(id=uuid4()),
    }
    values.update(overrides)
    return search_cache_key_builder(search_handler, namespace="search", **values)


def test_global_search_cache_key_is_shared_between_users() -> None:
    first = build_key(current_user=SimpleNamespace(id=uuid4()))
    second = build_key(current_user=SimpleNamespace(id=uuid4()))

    assert first == second
    assert len(first) == 32


def test_private_search_cache_key_isolated_by_user() -> None:
    first = build_key(my_docs=True, current_user=SimpleNamespace(id=uuid4()))
    second = build_key(my_docs=True, current_user=SimpleNamespace(id=uuid4()))

    assert first != second


def test_search_cache_key_changes_with_search_parameters() -> None:
    baseline = build_key()

    assert build_key(q="postgres") != baseline
    assert build_key(page=2) != baseline
    assert build_key(size=20) != baseline
    assert build_key(document_id="document-id") != baseline
