import csv
import importlib.util
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[2]
PRECISION_SCRIPT = PROJECT_ROOT / "qa" / "precision" / "evaluate_precision_at_3.py"
PRECISION_QUERIES = PROJECT_ROOT / "qa" / "precision" / "queries.csv"
LOCUST_CONFIG = PROJECT_ROOT / "qa" / "load" / "locust.conf"
LOCUST_SCRIPT = PROJECT_ROOT / "qa" / "load" / "locustfile.py"
LOCUST_REPORT = PROJECT_ROOT / "qa" / "load" / "report.csv"
PRECISION_REPORT = PROJECT_ROOT / "qa" / "precision" / "report.csv"


def _load_precision_module():
    spec = importlib.util.spec_from_file_location("qa_precision", PRECISION_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_precision_dataset_contains_ten_reference_queries() -> None:
    precision = _load_precision_module()

    rows = precision.load_queries(PRECISION_QUERIES)

    assert len(rows) == 10
    assert len({row["expected_file"] for row in rows}) == 10
    assert all(row["content"] for row in rows)


def test_precision_evaluator_detects_top_three_hit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    precision = _load_precision_module()

    monkeypatch.setattr(
        precision,
        "request_json",
        lambda *args, **kwargs: {
            "items": [
                {"file_name": "other.pdf"},
                {"file_name": "expected.pdf"},
                {"file_name": "third.pdf"},
            ]
        },
    )

    results = precision.evaluate(
        "http://localhost:8000",
        "token",
        [{"query": "reference", "expected_file": "expected.pdf"}],
    )

    assert results[0]["hit"] is True
    assert results[0]["top_3"] == "other.pdf | expected.pdf | third.pdf"


def test_load_scenario_is_configured_for_fifty_users() -> None:
    config = LOCUST_CONFIG.read_text(encoding="utf-8")
    scenario = LOCUST_SCRIPT.read_text(encoding="utf-8")

    assert "users = 50" in config
    assert "headless = true" in config
    assert '"/api/v1/search"' in scenario
    assert "Authorization" in scenario


def test_qa_reports_contain_successful_control_runs() -> None:
    with PRECISION_REPORT.open(encoding="utf-8", newline="") as source:
        precision_rows = list(csv.DictReader(source))
    with LOCUST_REPORT.open(encoding="utf-8", newline="") as source:
        load_rows = list(csv.DictReader(source))

    assert len(precision_rows) == 10
    assert all(row["hit"] == "True" for row in precision_rows)
    assert len(load_rows) == 1
    assert load_rows[0]["users"] == "50"
    assert load_rows[0]["failures"] == "0"
