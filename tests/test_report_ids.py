import copy
import json
from pathlib import Path

import pytest

from safe_mcp_auditor.report.ids import finding_hash_input, unknown_hash_input
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


def test_hash_inputs_escape_pipe_delimiters_and_backslashes() -> None:
    finding = Report.model_validate(
        {
            "schema_version": "1.0.0",
            "status": "needs_review",
            "metadata": {
                "target_name": "example",
                "input_type": "directory",
                "input_path": ".",
                "input_hash": "deadbeef",
                "analyzed_at": "2025-01-01T00:00:00Z",
                "app_version": "0.1.0",
                "safe_mcp_reference": "SAFE-MCP@dev",
                "safe_mcp_manifest_path": "knowledge/safe-mcp/manifest.json",
                "safe_mcp_knowledge_pack_hash": "abc123",
                "models": {
                    "llm": {"provider": "offline", "model": "stub", "temperature": 0},
                    "embedder": {"provider": "offline", "model": "stub"},
                },
                "run_id": "00000000-0000-0000-0000-000000000000",
                "scope": {"included_paths": ["."], "excluded_paths": []},
            },
            "inventory": {
                "languages": [],
                "entrypoints": [],
                "mcp_transport": "unknown",
                "auth": {"present": False, "mechanism": None, "evidence": []},
                "tools": [],
                "resources": [],
                "storage": [],
                "network_egress": {"present": False, "allowlist": [], "evidence": []},
                "dependencies": {"manifests": [], "lockfiles": [], "evidence": []},
            },
            "findings": [
                {
                    "id": None,
                    "title": "title\\with|pipe",
                    "severity": "high",
                    "confidence": "high",
                    "safe_mcp": {
                        "techniques": ["SAFE-T0002\\B", "SAFE-T0001|A"],
                        "tactics": [],
                        "recommended_mitigations": [],
                        "detection_rule_paths": [],
                    },
                    "what_is_happening": "x",
                    "why_it_matters": {
                        "cia": {
                            "confidentiality": "low",
                            "integrity": "low",
                            "availability": "low",
                        },
                        "scope": "x",
                    },
                    "recommendation": "x",
                    "evidence": [
                        {
                            "path": "path\\with|pipe",
                            "line_start": 10,
                            "line_end": 10,
                            "excerpt": "x",
                            "notes": "x",
                        }
                    ],
                }
            ],
            "unknowns": [
                {
                    "id": None,
                    "question": "question\\with|pipe",
                    "why_it_matters": "x",
                    "how_to_verify": "x",
                    "related_techniques": ["SAFE-T0001|A"],
                    "evidence": [
                        {
                            "path": "path\\with|pipe",
                            "line_start": 10,
                            "line_end": 10,
                            "excerpt": "x",
                            "notes": "x",
                        }
                    ],
                }
            ],
            "coverage": [],
        }
    )

    finding_input = finding_hash_input(finding.findings[0])
    unknown_input = unknown_hash_input(finding.unknowns[0])

    assert (
        finding_input
        == "finding|title\\\\with\\|pipe|SAFE-T0001\\|A,SAFE-T0002\\\\B|path\\\\with\\|pipe|10"
    )
    assert (
        unknown_input
        == "unknown|question\\\\with\\|pipe|SAFE-T0001\\|A|path\\\\with\\|pipe|10"
    )
