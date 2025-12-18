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
