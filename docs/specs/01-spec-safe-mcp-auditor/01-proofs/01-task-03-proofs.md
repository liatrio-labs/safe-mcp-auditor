# Spec 01 — Task 03 Proofs (3.0 Implement deterministic report normalization)

## CLI Output

### `safe-mcp-auditor report normalize --input fixtures/report.json --output reports/normalized.json`

```text
reports/normalized.json
```

### `diff fixtures/expected-normalized.json reports/normalized.json`

```text
# no output
```

Exit code:

```text
0
```

## Test Results

### `uv run pytest -q`

```text
......                                                                   [100%]
6 passed in 0.14s
```
