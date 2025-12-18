from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Status(StrEnum):
    PASS = "pass"
    NEEDS_REVIEW = "needs_review"
    FAIL = "fail"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Applicability(StrEnum):
    APPLICABLE = "applicable"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class Evidence(BaseModel):
    path: str
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    excerpt: str
    notes: str


class LlmModel(BaseModel):
    provider: str
    model: str
    temperature: float | int


class EmbedderModel(BaseModel):
    provider: str
    model: str


class ModelConfigs(BaseModel):
    llm: LlmModel
    embedder: EmbedderModel


class Scope(BaseModel):
    included_paths: list[str]
    excluded_paths: list[str]


class Metadata(BaseModel):
    target_name: str
    input_type: str
    input_path: str
    input_hash: str
    analyzed_at: str
    app_version: str
    safe_mcp_reference: str
    safe_mcp_manifest_path: str
    safe_mcp_knowledge_pack_hash: str
    models: ModelConfigs
    run_id: str
    scope: Scope


class Auth(BaseModel):
    present: bool
    mechanism: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class InventoryTool(BaseModel):
    model_config = {"populate_by_name": True}

    name: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    evidence: list[Evidence] = Field(default_factory=list)


class NetworkEgress(BaseModel):
    present: bool
    allowlist: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class Dependencies(BaseModel):
    manifests: list[str] = Field(default_factory=list)
    lockfiles: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class Inventory(BaseModel):
    languages: list[str] = Field(default_factory=list)
    entrypoints: list[dict[str, Any]] = Field(default_factory=list)
    mcp_transport: str = "unknown"
    auth: Auth
    tools: list[InventoryTool] = Field(default_factory=list)
    resources: list[dict[str, Any]] = Field(default_factory=list)
    storage: list[dict[str, Any]] = Field(default_factory=list)
    network_egress: NetworkEgress
    dependencies: Dependencies


class SafeMcpFinding(BaseModel):
    techniques: list[str] = Field(default_factory=list)
    tactics: list[str] = Field(default_factory=list)
    recommended_mitigations: list[str] = Field(default_factory=list)
    detection_rule_paths: list[str] = Field(default_factory=list)


class CiaImpact(BaseModel):
    confidentiality: str
    integrity: str
    availability: str


class WhyItMatters(BaseModel):
    cia: CiaImpact
    scope: str


class Finding(BaseModel):
    id: str
    title: str
    severity: Severity
    confidence: Confidence
    safe_mcp: SafeMcpFinding
    what_is_happening: str
    why_it_matters: WhyItMatters
    recommendation: str
    evidence: list[Evidence]


class Unknown(BaseModel):
    id: str
    question: str
    why_it_matters: str
    how_to_verify: str
    related_techniques: list[str] = Field(default_factory=list)
    evidence: list[Evidence]


class CoverageEntry(BaseModel):
    technique_id: str
    tactic: str
    safe_mcp_severity: str
    applicability: Applicability
    confidence: Confidence
    linked_finding_ids: list[str] = Field(default_factory=list)


class Report(BaseModel):
    schema_version: str
    status: Status
    metadata: Metadata
    inventory: Inventory
    findings: list[Finding] = Field(default_factory=list)
    unknowns: list[Unknown] = Field(default_factory=list)
    coverage: list[CoverageEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _enforce_unknown_gate(self) -> "Report":
        if self.unknowns and self.status != Status.NEEDS_REVIEW:
            raise ValueError("status must be 'needs_review' when unknowns are present")
        if not self.unknowns and self.status == Status.NEEDS_REVIEW:
            raise ValueError(
                "status must not be 'needs_review' when unknowns are empty"
            )
        return self
