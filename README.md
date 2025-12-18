# SAFE-MCP Auditor

A small, offline-first CLI that for auditing MCP codebases against the SAFE-MCP framework by producing SAFE-MCP audit reports. 

## What This App Does (Today)

- Validates audit report JSON against a Pydantic schema
- Normalizes reports for deterministic ordering and stable IDs
- Renders a deterministic Markdown report

## CLI (Current)

```bash
uv run safe-mcp-auditor --help
uv run safe-mcp-auditor report --help

uv run safe-mcp-auditor report validate --input fixtures/report.json
uv run safe-mcp-auditor report normalize --input fixtures/report.json --output /tmp/normalized.json
uv run safe-mcp-auditor report render --input fixtures/report.json
```

## Roadmap (From PRD)

This is a placeholder roadmap based on `docs/prd-safe-mcp-auditor.md`.

1. Implement the SAFE-MCP auditor workflow (CrewAI orchestration)
2. Add repo ingestion modes (local path, archive, GitHub repo)
3. Add SAFE-MCP knowledge pack handling and versioning
4. Produce a structured JSON output suitable for CI gating
5. Improve report rendering (sections, coverage matrix, links)
6. Add richer validation (cross-field consistency checks)
7. Add packaging/release flow for the CLI

## About SAFE-MCP (High Level)

SAFE-MCP is a security framework for auditing Model Context Protocol (MCP) servers. It defines:

- Techniques and tactics for common MCP security concerns
- Guidance on evidence collection and deterministic reporting
- A shared vocabulary for expressing findings, unknowns, and mitigations

This repo treats audited MCP repositories as untrusted input and aims to be read-only with respect to the target codebase.
