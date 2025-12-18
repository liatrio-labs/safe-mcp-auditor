import json
from pathlib import Path

import pytest

from safe_mcp_auditor.report.models import Report


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_fixture_report_is_valid() -> None:
    report_path = FIXTURES_DIR / "report.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))

    report = Report.model_validate(data)
    assert report.schema_version == "1.0.0"


def test_unknowns_require_needs_review_status() -> None:
    report_path = FIXTURES_DIR / "report.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))

    data["status"] = "pass"
    data["unknowns"] = [
        {
            "id": "U-000000000000",
            "question": "Is auth enabled?",
            "why_it_matters": "Unauthenticated access is dangerous.",
            "how_to_verify": "Check server config.",
            "related_techniques": ["SAFE-T0001"],
            "evidence": [
                {
                    "path": "server.py",
                    "line_start": 1,
                    "line_end": 1,
                    "excerpt": "print('hi')",
                    "notes": "Placeholder",
                }
            ],
        }
    ]

    with pytest.raises(ValueError, match="needs_review"):
        Report.model_validate(data)
