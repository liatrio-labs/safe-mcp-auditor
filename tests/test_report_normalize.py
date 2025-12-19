import json
from pathlib import Path

from safe_mcp_auditor.report.models import Report
from safe_mcp_auditor.report.normalize import normalize_report, serialize_report_json


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_normalized_json_matches_golden_fixture() -> None:
    report_path = FIXTURES_DIR / "report.json"
    expected_path = FIXTURES_DIR / "expected-normalized.json"

    report = Report.model_validate(json.loads(report_path.read_text(encoding="utf-8")))
    normalized = normalize_report(report)

    actual = serialize_report_json(normalized)
    expected = expected_path.read_text(encoding="utf-8")

    assert actual == expected


def test_normalization_is_idempotent() -> None:
    report_path = FIXTURES_DIR / "report.json"
    report = Report.model_validate(json.loads(report_path.read_text(encoding="utf-8")))

    once = normalize_report(report)
    twice = normalize_report(once)

    assert serialize_report_json(once) == serialize_report_json(twice)
