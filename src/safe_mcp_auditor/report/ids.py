from __future__ import annotations

import hashlib

from safe_mcp_auditor.report.models import Evidence, Finding, Unknown


class StableIdError(ValueError):
    """Raised when a stable ID cannot be computed."""


class MissingEvidenceError(StableIdError):
    def __init__(self) -> None:
        super().__init__("evidence is required to compute a stable ID")


class MissingFindingTitleError(StableIdError):
    def __init__(self) -> None:
        super().__init__("title is required to compute a stable finding ID")


class MissingFindingTechniquesError(StableIdError):
    def __init__(self) -> None:
        super().__init__(
            "safe_mcp.techniques is required to compute a stable finding ID"
        )


class MissingUnknownQuestionError(StableIdError):
    def __init__(self) -> None:
        super().__init__("question is required to compute a stable unknown ID")


class MissingUnknownTechniquesError(StableIdError):
    def __init__(self) -> None:
        super().__init__(
            "related_techniques is required to compute a stable unknown ID"
        )


def _escape_hash_field(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|")


def _primary_evidence(evidence: list[Evidence]) -> Evidence:
    if not evidence:
        raise MissingEvidenceError

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
        raise MissingFindingTitleError

    techniques = sorted(finding.safe_mcp.techniques)
    if not techniques:
        raise MissingFindingTechniquesError

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
        raise MissingUnknownQuestionError

    techniques = sorted(unknown.related_techniques)
    if not techniques:
        raise MissingUnknownTechniquesError

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
