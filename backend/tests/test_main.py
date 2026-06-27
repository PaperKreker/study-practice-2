import asyncio

from app import main


def test_app_metadata() -> None:
    expected_title = (
        "Интеллектуальная поисковая система по внутренней базе знаний университета"
    )
    assert main.app.title == expected_title
    assert main.app.docs_url == "/docs"
    assert main.app.openapi_url == "/openapi.json"


def test_document_router_is_registered() -> None:
    paths = set(main.app.openapi()["paths"])

    assert "/api/v1/documents/upload" in paths
    assert "/api/v1/documents" in paths
    assert "/api/v1/documents/{document_id}" in paths
    assert "/api/v1/search" in paths
    assert "/api/v1/search/history/{user_id}" in paths
    assert "/api/v1/users/register" in paths
    assert "/api/v1/users/login" in paths
    assert "/api/v1/users/me" in paths
    assert "/api/v1/documents/search" not in paths


def test_root_response() -> None:
    assert asyncio.run(main.root()) == {
        "message": "API поисковой системы успешно запущено"
    }


def test_health_check_response() -> None:
    assert asyncio.run(main.health_check()) == {"status": "ok"}
