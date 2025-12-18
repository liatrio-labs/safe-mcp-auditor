# 01 Questions Round 2 - SAFE-MCP Auditor

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Resolve Scope vs Input-Type Expectations

You selected **Reporting foundation only** (schema + renderer + stable IDs) AND **both directory + Repomix** inputs. For this spec, what should we actually deliver?

- [ ] (A) Reporting-only: implement JSON schema/model + deterministic Markdown renderer; input types only affect metadata/evidence formatting (no `audit` command yet)
- [ ] (B) “Audit skeleton”: add a minimal `audit` command that supports both inputs but only produces stub/fixture-based data to exercise the report pipeline
- [ ] (C) Expand scope: include ingest/parsing for both inputs (directory hashing + Repomix parsing) just enough to create real metadata/evidence blocks, but no risk detection
- [x] (D) Change input requirement: for this spec, only support rendering/validation from an existing JSON report (no directory/Repomix yet)
- [ ] (E) Other (describe)

## 2. Exit Code Convention

You left exit codes as “whatever you recommend.” Which convention should we lock in for MVP (and keep consistent across commands)?

- [x] (A) `0` pass, `1` needs_review (unknowns), `2` fail (clear ordering: worse = higher)
- [ ] (B) `0` pass, `2` needs_review, `1` fail (Click/Typer sometimes uses `1` for generic errors)
- [ ] (C) `0` pass, `1` for any non-pass status (don’t differentiate)
- [ ] (D) Other (describe)

## 3. JSON Schema Publication

For the reporting foundation, do you want an explicit JSON Schema file checked into the repo (separate from Pydantic models)?

- [ ] (A) Yes: publish `schemas/safe-mcp-audit.schema.json` and ensure the report validates against it
- [x] (B) No: Pydantic model validation is sufficient for now
- [ ] (C) Other (describe)

## 4. Deterministic Rendering Details

What do you want the Markdown renderer to optimize for in MVP?

- [x] (A) Strict determinism for diffing (stable section order, stable sorting, consistent formatting)
- [ ] (B) Human readability first (determinism best-effort)
- [ ] (C) Balance: deterministic ordering, but allow some flexible formatting
- [ ] (D) Other (describe)

## 5. Finding/Unknown Stable ID Source Inputs

The PRD recommends stable IDs based on technique IDs + primary evidence path + primary evidence line + finding-type key. What should be considered the “primary evidence” when there are multiple citations?

- [x] (A) First evidence item after deterministic sort (path asc, line_start asc)
- [ ] (B) Highest-severity evidence chosen by the detector (explicitly marked)
- [ ] (C) Always the evidence item with the smallest (path, line_start)
- [ ] (D) Other (describe)
