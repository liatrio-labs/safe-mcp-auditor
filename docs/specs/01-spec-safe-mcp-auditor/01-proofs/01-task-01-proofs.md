# Spec 01 — Task 01 Proofs (1.0 Scaffold `uv` project and Typer CLI)

## CLI Output

### `safe-mcp-auditor --help`

```text
Usage: safe-mcp-auditor [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Print version and exit.
  --help     Show this message and exit.

Commands:
  report
```

### `safe-mcp-auditor report --help`

```text
Usage: safe-mcp-auditor report [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  validate
  normalize
  render
```

## Test Results

### `uv run pytest -q`

```text
..                                                                       [100%]
2 passed in 0.07s
```
