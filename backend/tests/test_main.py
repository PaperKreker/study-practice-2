import asyncio

import pytest
from fastapi import Request, Response

from app import main


def _make_request(path: str, method: str = "GET") -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [],
            "client": ("test-client", 50000),
            "server": ("test-server", 80),
            "root_path": "",
        }
    )


def _sample_value(collector, sample_name: str, labels: dict[str, str]) -> float:
    for metric in collector.collect():
        for sample in metric.samples:
            if sample.name == sample_name and sample.labels == labels:
                return sample.value
    return 0.0


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
    assert "/api/v1/search/history" in paths
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


def test_metrics_route_is_registered() -> None:
    assert "/metrics" in {
        route.path for route in main.app.routes if hasattr(route, "path")
    }


def test_prometheus_middleware_records_normalized_endpoint() -> None:
    endpoint = "/api/v1/documents/{id}"
    request_labels = {"method": "GET", "endpoint": endpoint, "status": "204"}
    duration_labels = {"method": "GET", "endpoint": endpoint}
    requests_before = _sample_value(
        main.REQUESTS, "http_requests_total", request_labels
    )
    durations_before = _sample_value(
        main.DURATION, "http_request_duration_seconds_count", duration_labels
    )

    async def call_next(request: Request) -> Response:
        return Response(status_code=204)

    request = _make_request(
        "/api/v1/documents/123e4567-e89b-12d3-a456-426614174000"
    )
    response = asyncio.run(
        main.PrometheusMiddleware(main.app).dispatch(request, call_next)
    )

    assert response.status_code == 204
    requests_after = _sample_value(
        main.REQUESTS, "http_requests_total", request_labels
    )
    durations_after = _sample_value(
        main.DURATION,
        "http_request_duration_seconds_count",
        duration_labels,
    )

    assert requests_after == requests_before + 1
    assert durations_after == durations_before + 1


def test_prometheus_middleware_records_server_errors() -> None:
    labels = {
        "method": "POST",
        "endpoint": "/api/v1/documents/{id}",
        "status": "500",
    }
    requests_before = _sample_value(main.REQUESTS, "http_requests_total", labels)

    async def call_next(request: Request) -> Response:
        raise RuntimeError("request failed")

    request = _make_request("/api/v1/documents/42", method="POST")
    with pytest.raises(RuntimeError, match="request failed"):
        asyncio.run(main.PrometheusMiddleware(main.app).dispatch(request, call_next))

    requests_after = _sample_value(main.REQUESTS, "http_requests_total", labels)

    assert requests_after == requests_before + 1
