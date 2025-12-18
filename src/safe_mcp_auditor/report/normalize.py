from __future__ import annotations

import json

from safe_mcp_auditor.report.models import Report, Severity


_SEVERITY_RANK: dict[Severity, int] = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
}


def normalize_report(report: Report) -> Report:
    """Return a normalized copy of `report`.

    Normalization rules (deterministic ordering):

    - `findings`: severity desc, then `id` asc
    - `coverage`: `technique_id` asc
    - `inventory.tools`: `name` asc
    """

    normalized_inventory = report.inventory.model_copy(
        update={
            "tools": sorted(report.inventory.tools, key=lambda tool: tool.name),
        }
    )

    normalized_findings = sorted(
        report.findings,
        key=lambda finding: (_SEVERITY_RANK[finding.severity], finding.id),
    )

    normalized_coverage = sorted(report.coverage, key=lambda entry: entry.technique_id)

    return report.model_copy(
        update={
            "inventory": normalized_inventory,
            "findings": normalized_findings,
            "coverage": normalized_coverage,
        }
    )


def serialize_report_json(report: Report) -> str:
    """Serialize a report as deterministic JSON (canonical formatting)."""

    data = report.model_dump(by_alias=True, mode="json")
    return json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
