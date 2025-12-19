import json
from pathlib import Path

from safe_mcp_auditor.report.models import Report
from safe_mcp_auditor.report.normalize import normalize_report
from safe_mcp_auditor.report.render_md import render_report_md


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_markdown_render_matches_golden_fixture() -> None:
    report_path = FIXTURES_DIR / "report.json"
    expected_path = FIXTURES_DIR / "expected-report.md"

    report = Report.model_validate(json.loads(report_path.read_text(encoding="utf-8")))
    normalized = normalize_report(report)

    actual = render_report_md(normalized)
    expected = expected_path.read_text(encoding="utf-8")

    assert actual == expected


def test_markdown_tables_escape_pipes_and_newlines() -> None:
    data = json.loads((FIXTURES_DIR / "report.json").read_text(encoding="utf-8"))
    data["findings"][0]["evidence"][0]["notes"] = "note|with\nnewlines"
    data["coverage"] = [
        {
            "technique_id": "SAFE-T0001",
            "tactic": "initial_access",
            "safe_mcp_severity": "high",
            "applicability": "applicable",
            "confidence": "high",
            "linked_finding_ids": ["F-aaaaaaaaaaaa|x"],
        }
    ]

    report = Report.model_validate(data)
    normalized = normalize_report(report)

    rendered = render_report_md(normalized)

    assert "note\\|with newlines" in rendered
    assert "F-aaaaaaaaaaaa\\|x" in rendered
