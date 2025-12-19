<!-- markdownlint-disable MD013 -->

# Spec 01 — Task 04 Proofs (4.0 Add stable ID generation for findings and unknowns)

## CLI Output

### `safe-mcp-auditor report normalize --input fixtures/report-missing-ids.json --output reports/with-ids.json`

```text
reports/with-ids.json
```

### Generated IDs (from `reports/with-ids.json`)

```text
F-9bac331dbf8c
U-e2d1f8a98499
```

## Test Results

### `uv run pytest -q`

```text
.........                                                                [100%]
9 passed in 0.16s
```
