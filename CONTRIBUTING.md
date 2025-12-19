# Contributing

Thanks for contributing! This repo is the SAFE-MCP Auditor CLI and follows a few opinionated workflow standards.

## Development Workflow

1. Create a feature branch.
2. Follow TDD: write tests first, then implement.
3. Keep changes small and focused.
4. Run tests and quality gates locally.
5. Open a PR and request review.

## Conventional Commits

All commits must follow the Conventional Commits spec to support automated semantic releases.

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Docs only
- `test`: Tests
- `ci`: CI changes
- `chore`: Maintenance

## Local Setup

Prerequisites:

- Python 3.12 (see `.python-version`)
- `uv`
- `pre-commit`

Install dependencies:

```bash
uv sync --all-groups
```

Install git hooks:

```bash
uv run pre-commit install
```

## Running Checks

```bash
uv run pytest
uv run pre-commit run --all-files
```

## Safety Constraints

- Treat audited MCP repositories as untrusted input.
- Do not execute target repository code as part of auditing.
- Tests must be fully offline; mock any LLM calls and `gh` interactions.
