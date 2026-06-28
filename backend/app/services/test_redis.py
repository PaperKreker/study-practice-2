from types import SimpleNamespace
from uuid import uuid4

from app.core.redis import search_cache_key_builder
from tests.test_redis import search_handler


def test_search_cache_key_handles_nested_kwargs_from_fastapi_cache() -> None:
    current_user = SimpleNamespace(id=uuid4())
    endpoint_params = {
        "q": "elastic",
        "page": 1,
        "size": 10,
        "document_id": "doc-1",
        "my_docs": False,
        "current_user": current_user,
    }

    direct_key = search_cache_key_builder(
        search_handler, namespace="search", **endpoint_params
    )

    nested_key = search_cache_key_builder(
        search_handler, namespace="search", kwargs=endpoint_params
    )

    assert direct_key == nested_key

    changed_params = endpoint_params.copy()
    changed_params["q"] = "postgres"

    changed_nested_key = search_cache_key_builder(
        search_handler, namespace="search", kwargs=changed_params
    )

    assert nested_key != changed_nested_key
