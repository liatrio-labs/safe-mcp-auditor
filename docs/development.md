# Development

## Prerequisites

- Python 3.12 (see `.python-version`)
- `uv`
- `pre-commit`

## Setup

```bash
uv sync --all-groups
uv run pre-commit install

# Optional (one-time): install git hooks to run on commit
uv run pre-commit install --install-hooks
```

## Test

```bash
uv run pytest
```

## Lint / Format

This repo uses `ruff` via pre-commit.

```bash
uv run pre-commit run --all-files
```

## Releases

Releases are automated via GitHub Actions + `python-semantic-release`.

- Merges to `main` using Conventional Commits trigger version bumps.
- The release workflow creates a tag like `vX.Y.Z` and updates `CHANGELOG.md`.
- Release commits include `[skip ci]` to avoid double-running CI.
