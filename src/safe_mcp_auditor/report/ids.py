from __future__ import annotations

import hashlib

from safe_mcp_auditor.report.models import Evidence, Finding, Unknown


def _escape_hash_field(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|")


def _primary_evidence(evidence: list[Evidence]) -> Evidence:
    if not evidence:
        raise ValueError("evidence is required to compute a stable ID")

    return sorted(evidence, key=lambda e: (e.path, e.line_start))[0]


def finding_hash_input(finding: Finding) -> str:
    """Build the normalized hash input string for a finding.

    Format (do not include excerpts):

    - prefix: `finding`
    - `type_key`: the finding title
    - `techniques`: sorted SAFE technique IDs joined by `,`
    - `primary_path`: from primary evidence
    - `primary_line_start`: from primary evidence

    Serialized as pipe-delimited fields:

    `finding|<type_key>|<techniques>|<primary_path>|<primary_line_start>`
    """

    if not finding.title:
        raise ValueError("title is required to compute a stable finding ID")

    techniques = sorted(finding.safe_mcp.techniques)
    if not techniques:
        raise ValueError(
            "safe_mcp.techniques is required to compute a stable finding ID"
        )

    primary = _primary_evidence(finding.evidence)

    escaped_techniques = [_escape_hash_field(t) for t in techniques]

    return "|".join(
        [
            "finding",
            _escape_hash_field(finding.title),
            ",".join(escaped_techniques),
            _escape_hash_field(primary.path),
            str(primary.line_start),
        ]
    )


def unknown_hash_input(unknown: Unknown) -> str:
    """Build the normalized hash input string for an unknown.

    Format (do not include excerpts):

    - prefix: `unknown`
    - `question`: unknown question text
    - `techniques`: sorted SAFE technique IDs joined by `,`
    - `primary_path`: from primary evidence
    - `primary_line_start`: from primary evidence

    Serialized as pipe-delimited fields:

    `unknown|<question>|<techniques>|<primary_path>|<primary_line_start>`
    """

    if not unknown.question:
        raise ValueError("question is required to compute a stable unknown ID")

    techniques = sorted(unknown.related_techniques)
    if not techniques:
        raise ValueError(
            "related_techniques is required to compute a stable unknown ID"
        )

    primary = _primary_evidence(unknown.evidence)

    escaped_techniques = [_escape_hash_field(t) for t in techniques]

    return "|".join(
        [
            "unknown",
            _escape_hash_field(unknown.question),
            ",".join(escaped_techniques),
            _escape_hash_field(primary.path),
            str(primary.line_start),
        ]
    )


def stable_finding_id(finding: Finding) -> str:
    digest = hashlib.sha256(finding_hash_input(finding).encode("utf-8")).hexdigest()[
        :12
    ]
    return f"F-{digest}"


def stable_unknown_id(unknown: Unknown) -> str:
    digest = hashlib.sha256(unknown_hash_input(unknown).encode("utf-8")).hexdigest()[
        :12
    ]
    return f"U-{digest}"
