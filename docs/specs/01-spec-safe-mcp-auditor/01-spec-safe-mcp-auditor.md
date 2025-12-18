# 01-spec-safe-mcp-auditor.md

## Introduction/Overview

SAFE-MCP Auditor produces standardized security audit reports for MCP server codebases mapped to the SAFE-MCP framework. This spec defines the **reporting foundation**: a canonical JSON report model with deterministic ordering, stable IDs, and a deterministic Markdown renderer.

This spec intentionally does **not** implement code ingestion (directory/Repomix) or the CrewAI-based audit pipeline yet; it establishes the report contract those future components will produce.

## Goals

- Define a canonical JSON report data model (Pydantic) aligned to the PRD schema v1.
- Validate JSON reports deterministically (stable ordering, strict field validation).
- Render Markdown deterministically from JSON as a pure function.
- Implement stable IDs for findings and unknowns.
- Provide a developer-friendly CLI workflow to validate/render a report.

## User Stories

- **As an MCP engineer**, I want to validate a JSON audit report so that I can trust it conforms to the expected schema before sharing or diffing it.
- **As an MCP engineer**, I want a deterministic Markdown report rendered from JSON so that I can review findings in a human-friendly format.
- **As an MCP engineer**, I want stable finding/unknown IDs so that report diffs are meaningful across runs.

## Demoable Units of Work

### Unit 1: Canonical JSON Report Model

**Purpose:** Establish a stable, testable report contract that future audit stages will populate.

**Functional Requirements:**

- The system shall define Pydantic models for the JSON report schema v1, including `metadata`, `inventory`, `findings`, `unknowns`, and `coverage`.
- The system shall validate a JSON document against the Pydantic models and produce clear, user-friendly validation errors.
- The system shall serialize validated reports with deterministic JSON key ordering.
- The system shall enforce deterministic array ordering rules:
  - The system shall sort `findings` by severity descending, then `id` ascending.
  - The system shall sort `coverage` by `technique_id` ascending.
  - The system shall sort `inventory.tools` by `name` ascending.

**Proof Artifacts:**

- Test: a unit test validating a fixture JSON passes demonstrates schema contract.
- CLI: `safe-mcp-auditor report validate --input <file>` succeeds demonstrates validation workflow.

### Unit 2: Stable ID Generation

**Purpose:** Ensure findings and unknowns can be diffed across runs without brittle ordering or content hashing.

**Functional Requirements:**

- The system shall generate stable finding IDs using `"F-" + sha256(normalized_string)[0:12]`.
- The system shall generate stable unknown IDs using `"U-" + sha256(normalized_string)[0:12]`.
- The system shall not include excerpts in the ID hash inputs.
- The system shall define the “primary evidence” deterministically as the first evidence item after sorting by `path` ascending then `line_start` ascending.
- The system shall error if a finding/unknown cannot compute an ID due to missing required hash inputs.

**Proof Artifacts:**

- Test: snapshot test showing stable IDs unchanged across reordering demonstrates determinism.
- CLI: `safe-mcp-auditor report normalize --input <file> --output <file>` produces stable IDs demonstrates normalization.

### Unit 3: Deterministic Markdown Renderer

**Purpose:** Produce a consistent, human-readable report view for engineers with reliable diffs.

**Functional Requirements:**

- The system shall render Markdown from the canonical JSON report as a pure function (no I/O in renderer).
- The system shall produce Markdown with a fixed section order aligned to the PRD template:
  - Summary
  - Findings (Prioritized)
  - Quick hardening checklist
  - Unknowns / Needs manual review
  - Appendix A: Inventory
  - Appendix B: SAFE-MCP technique coverage matrix
- The system shall render evidence entries with `path`, `line_start`, `line_end`, and `excerpt`.
- The system shall keep formatting deterministic (consistent headings, lists, tables, and whitespace).

**Proof Artifacts:**

- Test: golden Markdown output comparison against a fixture JSON demonstrates deterministic rendering.
- CLI: `safe-mcp-auditor report render --input <file>` writes the Markdown report demonstrates end-to-end render.

### Unit 4: CLI Workflow for Reporting

**Purpose:** Provide a developer-first interface to validate, normalize, and render reports.

**Functional Requirements:**

- The system shall provide a Typer-based command group `report`.
- The system shall implement `safe-mcp-auditor report validate --input <path>` that validates a JSON report.
- The system shall implement `safe-mcp-auditor report normalize --input <path> --output <path>` that:
  - validates the report,
  - computes stable IDs where missing,
  - applies deterministic sorting,
  - writes deterministic JSON.
- The system shall implement `safe-mcp-auditor report render --input <path>` that:
  - validates and normalizes the report,
  - writes Markdown under `reports/`,
  - never overwrites an existing file.
- The system shall return exit codes as:
  - `0` for `pass`
  - `1` for `needs_review`
  - `2` for `fail`

**Proof Artifacts:**

- Screenshot: `safe-mcp-auditor report --help` output demonstrates CLI entrypoints.
- CLI: `safe-mcp-auditor report render --input fixtures/report.json` prints generated paths demonstrates outputs.

## Non-Goals (Out of Scope)

1. **Directory ingestion**: reading a target MCP repo from `--path`, hashing inputs, or extracting evidence from source files.
2. **Repomix ingestion**: parsing Repomix XML inputs to build evidence and inventory.
3. **Audit pipeline**: CrewAI tasks (inventory extraction, risk detection, SAFE mapping), SAFE-MCP knowledge indexing, or network calls (`gh`).

## Design Considerations

No specific UI design requirements identified.

Markdown output should prioritize readability for engineers while remaining strictly deterministic for diffing.

## Repository Standards

- Use Python with `uv` for dependency management.
- Implement CLI using Typer.
- Follow strict TDD (tests first).
- Tests must run fully offline; mock any LLM calls and any `gh` interactions (even if not used in this spec).
- Prefer deterministic outputs (stable sorting, stable IDs, fixed formatting) to support report diffing.

## Technical Considerations

- Use Pydantic models as the schema contract (no separate JSON Schema file in MVP).
- Treat Markdown rendering as a pure function of the validated report model.
- Ensure serialization and sorting rules are applied consistently in one “normalize” step used by both validation and rendering.
- Report output location is fixed to `reports/` and must not overwrite existing files.

## Security Considerations

- Reports may include code excerpts; the system shall avoid printing large excerpts to logs by default.
- The system shall avoid writing reports outside `reports/` in this spec to reduce accidental leakage.
- The system shall ensure report rendering does not execute or evaluate any report content (treat report input as untrusted data).

## Success Metrics

1. **Deterministic output**: re-rendering the same input JSON produces byte-identical Markdown.
2. **Schema stability**: fixture JSON validation remains stable across changes unless intentionally updated.
3. **UX reliability**: CLI commands return correct exit codes based on `status` and `unknowns[]`.

## Open Questions

1. No open questions at this time.
