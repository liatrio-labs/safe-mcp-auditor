# Architecture

## Overview

SAFE-MCP Auditor is an offline-first CLI that produces deterministic SAFE-MCP audit reports.

## Major Components

- CLI (`src/safe_mcp_auditor/cli.py`): Typer entrypoint and command wiring.
- Report pipeline (`src/safe_mcp_auditor/report/*`): schema validation, normalization, and Markdown rendering.
- Fixtures (`fixtures/`): example inputs and golden outputs for deterministic tests.

## Safety Model

- Audited repositories are treated as untrusted input.
- The auditor must be read-only with respect to target code and must not execute it.
- Tests must be fully offline; mock any LLM calls and `gh` interactions.
