<!-- markdownlint-disable MD013 -->

# Spec 01 — Task 06 Proofs (6.0 Finalize `report` CLI UX and exit codes)

## CLI Output

### Exit code mapping (`pass` → `0`)

Command:

```bash
safe-mcp-auditor report render --input fixtures/report.json; echo $?
```

Output:

```text
reports/example-target-deadbeef-safe-mcp-audit.json
reports/example-target-deadbeef-safe-mcp-audit.md
0
```

### Invalid JSON input prints validation errors and exits non-zero

Command:

```bash
safe-mcp-auditor report validate --input reports/invalid.json; echo $?
```

Output:

```text
Usage: safe-mcp-auditor report validate [OPTIONS]
Try 'safe-mcp-auditor report validate --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value: Invalid JSON: Expecting property name enclosed in double      │
│ quotes: line 1 column 2 (char 1)                                             │
╰──────────────────────────────────────────────────────────────────────────────╯
2
```

## Test Results

### `uv run pytest -q`

```text
..............                                                           [100%]
14 passed in 0.17s
```
