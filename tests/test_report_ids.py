import copy
import json
from pathlib import Path

import pytest

from safe_mcp_auditor.report.models import Report
from safe_mcp_auditor.report.normalize import normalize_report


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_missing_finding_and_unknown_ids_are_generated() -> None:
    report_path = FIXTURES_DIR / "report-missing-ids.json"
    report = Report.model_validate(json.loads(report_path.read_text(encoding="utf-8")))

    normalized = normalize_report(report)

    assert normalized.findings[0].id is not None
    assert normalized.findings[0].id.startswith("F-")
    assert len(normalized.findings[0].id) == 14

    assert normalized.unknowns[0].id is not None
    assert normalized.unknowns[0].id.startswith("U-")
    assert len(normalized.unknowns[0].id) == 14


def test_ids_are_stable_across_reordering() -> None:
    report_path = FIXTURES_DIR / "report-missing-ids.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))

    reordered = copy.deepcopy(data)
    reordered["findings"] = list(reversed(reordered["findings"]))
    reordered["findings"][0]["safe_mcp"]["techniques"] = list(
        reversed(reordered["findings"][0]["safe_mcp"]["techniques"])
    )
    reordered["findings"][0]["evidence"] = list(
        reversed(reordered["findings"][0]["evidence"])
    )

    reordered["unknowns"][0]["related_techniques"] = list(
        reversed(reordered["unknowns"][0]["related_techniques"])
    )
    reordered["unknowns"][0]["evidence"] = list(
        reversed(reordered["unknowns"][0]["evidence"])
    )

    report_a = Report.model_validate(data)
    report_b = Report.model_validate(reordered)

    normalized_a = normalize_report(report_a)
    normalized_b = normalize_report(report_b)

    assert normalized_a.findings[0].id == normalized_b.findings[0].id
    assert normalized_a.unknowns[0].id == normalized_b.unknowns[0].id


def test_id_generation_errors_without_required_inputs() -> None:
    report_path = FIXTURES_DIR / "report.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))

    data["findings"][0]["id"] = None
    data["findings"][0]["evidence"] = []

    report = Report.model_validate(data)

    with pytest.raises(ValueError, match="evidence"):
        normalize_report(report)
