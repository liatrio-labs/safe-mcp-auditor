# 01 Questions Round 1 - SAFE-MCP Auditor

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Scope for This Spec

The PRD describes a fairly large MVP (CLI + SAFE-MCP knowledge lifecycle + audit pipeline + report rendering + offline test strategy). To keep work incremental, what should **this single spec** cover?

- [ ] (A) Full PRD MVP in one spec (end-to-end audit + SAFE-MCP knowledge lifecycle + reporting)
- [x] (B) Reporting foundation only (JSON schema + deterministic Markdown renderer + stable IDs)
- [ ] (C) SAFE-MCP knowledge lifecycle only (`safe-mcp status|fetch|build-pack|build-index|verify` + staleness checks)
- [ ] (D) Target ingest/index only (directory + Repomix parsing, file indexing, inventory extraction)
- [ ] (E) Other (describe)

## 2. Primary User and Usage Context

Who is the primary user for the first deliverable, and where will it run most often?

- [x] (A) MCP engineers running locally during development
- [ ] (B) CI pipelines gating PRs/releases
- [ ] (C) Security engineers running point-in-time reviews
- [ ] (D) OSS maintainers auditing internet repos
- [ ] (E) Other (describe)

## 3. Input Types for the First Deliverable

Which input types must be supported in the first deliverable defined by this spec?

- [ ] (A) Directory input only (`--path`)
- [ ] (B) Repomix XML input only (`--repomix`)
- [x] (C) Both directory and Repomix, with identical report formats
- [ ] (D) Directory first; Repomix in a follow-up spec
- [ ] (E) Other (describe)

## 4. SAFE-MCP Reference Source and Network Expectations

The PRD recommends fetching SAFE-MCP via `gh` at a pinned ref, but some environments may be offline. What do you want as the MVP behavior?

- [x] (A) Online-friendly: `gh` fetch required (tests mock it); audit hard-fails if index missing/stale
- [ ] (B) Offline-friendly: allow building from a local SAFE-MCP checkout path (no network required)
- [ ] (C) Hybrid: support both (prefer pinned `gh` fetch, but allow `--safe-mcp-src-path` override)
- [ ] (D) Development-only: use `docs/references/repomix-output-SAFE-MCP-safe-mcp.xml` as the initial source
- [ ] (E) Other (describe)

## 5. Report Output and Overwrite Behavior

How strict should the tool be about output paths and overwriting?

- [x] (A) Always write to `reports/` and never overwrite existing reports
- [ ] (B) Default no-overwrite, but add `--overwrite` to allow replacing an existing report
- [ ] (C) Default no-overwrite, but add `--output-dir` to place reports elsewhere
- [ ] (D) Both `--overwrite` and `--output-dir`
- [ ] (E) Other (describe)

## 6. “Unknowns” Gate and Exit Codes

Unknowns are a hard non-pass in the PRD. What exit code semantics do you want?

- [ ] (A) `0` pass, `1` needs_review (unknowns present), `2` fail
- [ ] (B) `0` pass, `2` needs_review, `1` fail
- [ ] (C) `0` pass, any non-zero for needs_review or fail (don’t distinguish)
- [ ] (D) Match an existing internal/organizational convention (describe)
- [ ] (E) Other (describe): whatever you recommend

## 7. Evidence Detail Level in Findings

What evidence fidelity do you want to require in the first version of findings?

- [x] (A) File path + line range + excerpt (as in the PRD)
- [ ] (B) File path + line range only (no excerpts by default)
- [ ] (C) Excerpts only for high/critical findings (or when short)
- [ ] (D) Excerpts are optional and controlled by a CLI flag (e.g., `--include-excerpts`)
- [ ] (E) Other (describe)
