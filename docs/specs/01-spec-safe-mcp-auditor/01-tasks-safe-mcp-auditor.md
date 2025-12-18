# 01-tasks-safe-mcp-auditor.md

## Relevant Files

- `pyproject.toml` - Project metadata, dependencies, and console script entrypoint.
- `uv.lock` - Locked dependencies for reproducible installs.
- `.gitignore` - Ensure `reports/`, `.venv/`, and local caches are ignored.
- `src/safe_mcp_auditor/__init__.py` - Package entry.
- `src/safe_mcp_auditor/cli.py` - Root Typer app and command wiring.
- `src/safe_mcp_auditor/report/commands.py` - Typer `report` command group (`validate`, `normalize`, `render`).
- `src/safe_mcp_auditor/report/models.py` - Pydantic report schema models.
- `src/safe_mcp_auditor/report/normalize.py` - Deterministic sorting + canonical JSON serialization.
- `src/safe_mcp_auditor/report/ids.py` - Stable finding/unknown ID hashing utilities.
- `src/safe_mcp_auditor/report/render_md.py` - Pure Markdown renderer.
- `tests/test_cli_report.py` - CLI contract tests (help text, exit codes, file outputs).
- `tests/test_report_models.py` - Unit tests for Pydantic models + validation errors.
- `tests/test_report_normalize.py` - Normalization determinism tests.
- `tests/test_report_ids.py` - Stable ID rules tests.
- `tests/test_report_render_md.py` - Golden Markdown snapshot tests.
- `fixtures/report.json` - Minimal valid fixture report for tests.
- `fixtures/report-missing-ids.json` - Fixture missing `F-`/`U-` IDs to exercise generation.
- `fixtures/expected-normalized.json` - Golden normalized JSON output for determinism tests.
- `fixtures/expected-report.md` - Golden rendered Markdown output.

### Notes

- Use `uv` for all dependency management and execution (no direct `pip`).
- Follow strict TDD: write failing tests first, then implement.
- All tests must be fully offline.
- Prefer deterministic behavior: stable ordering, stable IDs, stable formatting.

## Tasks

### [ ] 1.0 Scaffold `uv` project and Typer CLI

#### 1.0 Proof Artifact(s)

- Screenshot: `safe-mcp-auditor --help` output demonstrates CLI entrypoint exists
- Screenshot: `safe-mcp-auditor report --help` output demonstrates `report` group exists
- Test: CLI smoke test passes demonstrates commands wire up

#### 1.0 Tasks

- [ ] 1.1 Initialize Python project with `uv` and add a minimal package layout under `src/`
- [ ] 1.2 Add Typer-based CLI entrypoint `safe-mcp-auditor` with `report` subcommand group
- [ ] 1.3 Add baseline test harness (pytest + Typer/Click runner) and a CLI smoke test
- [ ] 1.4 Update `.gitignore` to exclude local artifacts (`.venv/`, `reports/`, `.crewai_storage/`)

### [ ] 2.0 Define canonical JSON report model

#### 2.0 Proof Artifact(s)

- Test: unit tests for report Pydantic models pass demonstrates schema contract
- CLI: `safe-mcp-auditor report validate --input fixtures/report.json` succeeds demonstrates validation workflow

#### 2.0 Tasks

- [ ] 2.1 Create Pydantic models for report schema v1 (metadata, inventory, findings, unknowns, coverage)
- [ ] 2.2 Add enums and validation rules (status, severity, confidence, applicability)
- [ ] 2.3 Create a minimal valid fixture (`fixtures/report.json`) covering all required fields
- [ ] 2.4 Add model validation tests for valid/invalid inputs and readable error messages

### [ ] 3.0 Implement deterministic report normalization

#### 3.0 Proof Artifact(s)

- CLI: `safe-mcp-auditor report normalize --input fixtures/report.json --output reports/normalized.json` produces deterministic output demonstrates stable serialization
- Diff: `diff fixtures/expected-normalized.json reports/normalized.json` shows no differences demonstrates determinism

#### 3.0 Tasks

- [ ] 3.1 Implement a normalization function that sorts arrays per spec (findings, tools, coverage)
- [ ] 3.2 Implement canonical JSON serialization (deterministic key ordering + stable formatting)
- [ ] 3.3 Add golden normalized JSON fixture and tests proving idempotency and determinism

### [ ] 4.0 Add stable ID generation for findings and unknowns

#### 4.0 Proof Artifact(s)

- Test: snapshot test proving ID stability across reordered inputs demonstrates stable ID rules
- CLI: `safe-mcp-auditor report normalize --input fixtures/report-missing-ids.json --output reports/with-ids.json` produces `F-` and `U-` IDs demonstrates ID generation

#### 4.0 Tasks

- [ ] 4.1 Define the normalized hash input string format for findings and unknowns (documented in code)
- [ ] 4.2 Implement primary-evidence selection rule (sort evidence by `path`, then `line_start`)
- [ ] 4.3 Implement stable ID generation functions for findings (`F-`) and unknowns (`U-`)
- [ ] 4.4 Add fixtures/tests ensuring IDs are stable across reordering and error on missing inputs

### [ ] 5.0 Build deterministic Markdown renderer

#### 5.0 Proof Artifact(s)

- Test: golden Markdown comparison passes demonstrates deterministic rendering
- CLI: `safe-mcp-auditor report render --input fixtures/report.json` writes a Markdown report under `reports/` demonstrates end-to-end render

#### 5.0 Tasks

- [ ] 5.1 Implement a pure Markdown rendering function with fixed section ordering
- [ ] 5.2 Define deterministic formatting conventions (headings, lists, tables, whitespace)
- [ ] 5.3 Add golden Markdown fixture and tests verifying byte-identical output

### [ ] 6.0 Finalize `report` CLI UX and exit codes

#### 6.0 Proof Artifact(s)

- CLI: `safe-mcp-auditor report render --input fixtures/report.json; echo $?` returns expected exit code demonstrates status-to-exit-code mapping
- CLI: invalid JSON input prints validation errors and exits non-zero demonstrates user-friendly errors

#### 6.0 Tasks

- [ ] 6.1 Implement `report validate` to validate JSON input and map `status` to exit codes
- [ ] 6.2 Implement `report normalize` to validate, compute IDs, apply ordering, and write canonical JSON
- [ ] 6.3 Implement `report render` to validate/normalize and write Markdown to `reports/` without overwrite
- [ ] 6.4 Add CLI tests for exit codes (`pass`=0, `needs_review`=1, `fail`=2) and error cases
- [ ] 6.5 Ensure report filenames follow the PRD convention using JSON metadata (target + input hash)
