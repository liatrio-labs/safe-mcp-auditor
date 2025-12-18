<!-- markdownlint-disable MD013 -->

# PRD: SAFE-MCP Auditor (CrewAI)

## Summary

Build a read-only auditing application that analyzes a Model Context Protocol (MCP) server codebase and produces a standardized security audit report mapped to the SAFE-MCP framework.

The primary output is an engineer-friendly backlog of actionable findings, paired with an appendix that shows SAFE-MCP technique coverage.

Deliverables per run:

- `reports/<target-name>-<input-hash>-safe-mcp-audit.md`
- `reports/<target-name>-<input-hash>-safe-mcp-audit.json`

Where:

- `<target-name>` is derived automatically (with override).
- `<input-hash>` is a short, stable fingerprint of the analyzed input to avoid overwriting and to support comparisons over time.

## Architecture diagrams

### System overview

```mermaid
flowchart TD
    Dir[Directory Input<br/>MCP Source Tree] --> Ingest[Ingest & Normalize]
    Repomix[Repomix Input<br/>Packed Repo XML] --> Ingest

    Ingest --> Index[Index Files & Entry Points]
    Index --> CrewAI[CrewAI Audit Pipeline]

    SAFE[SAFE-MCP Knowledge<br/>Techniques + Mitigations] -. retrieval .-> CrewAI

    CrewAI --> ReportJSON[JSON Report<br/>Source of Truth]
    CrewAI --> ReportMD[Markdown Report<br/>Rendered View]

    ReportJSON --> ReportsDir[(reports/)]
    ReportMD --> ReportsDir

    classDef input fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef knowledge fill:#f5f5f5,stroke:#424242,stroke-width:2px
    classDef output fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px

    class Dir,Repomix input
    class Ingest,Index,CrewAI process
    class SAFE knowledge
    class ReportJSON,ReportMD,ReportsDir output
```

### Audit pipeline (internal stages)

```mermaid
flowchart LR
    A[Ingest & Normalize] --> B[Index Repo]
    B --> C[Extract Inventory]
    C --> D[Detect Risk Signals]
    D --> E[Map to SAFE Techniques]
    E --> F[Consolidate Findings]
    F --> G[Enrich w/ SAFE Mitigations<br/>and Detection Ideas]
    G --> H[Write JSON]
    H --> I[Render Markdown]

    C --> U[Unknowns Bucket]
    D --> U
    E --> U
    F --> U
    U --> Gate{Unknowns Present?}
    Gate -->|Yes| NR[Status: needs_review<br/>Non-zero exit]
    Gate -->|No| OK[Status: pass<br/>Exit 0]

    classDef stage fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef output fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef warn fill:#ffcdd2,stroke:#c62828,stroke-width:2px

    class A,B,C,D,E,F,G,H,I stage
    class Gate decision
    class NR warn
    class OK output
    class U stage
```

### Run sequence (CLI → audit → reports)

```mermaid
sequenceDiagram
    autonumber
    participant User as User / CI
    participant CLI as safe-mcp-auditor CLI
    participant Ingest as Ingest & Index
    participant Crew as CrewAI Crew
    participant KB as SAFE-MCP Knowledge
    participant FS as reports/ directory

    User->>CLI: Invoke audit (path or repomix)
    CLI->>Ingest: Load input + build file index
    Ingest-->>CLI: Normalized repo index

    CLI->>Crew: Kickoff audit pipeline
    rect rgb(255, 243, 224)
        Crew->>Crew: Extract inventory
        Crew->>Crew: Detect risk signals
        Crew->>KB: Retrieve SAFE-T/SAFE-M guidance
        KB-->>Crew: Relevant excerpts
        Crew->>Crew: Consolidate findings + unknowns
    end

    Crew-->>CLI: Structured results (JSON model)
    CLI->>FS: Write JSON report
    CLI->>FS: Render + write Markdown report
    CLI-->>User: Exit code (0 pass, non-zero needs_review)
```

## Background

MCP servers can expose powerful tools (filesystem, network, credentials, package managers, CI/CD systems). SAFE-MCP provides a MITRE ATT&CK-style catalog of tactics, techniques, and mitigations tailored to MCP ecosystems.

Security reviewers and engineers need a repeatable way to:

- Inventory what an MCP server can do.
- Identify security risks and map them to SAFE-MCP techniques.
- Recommend mitigations and detections grounded in SAFE-MCP.
- Produce a consistent report artifact suitable for CI and diffing.

## Goals

- Accept MCP code as either:
  - a local directory containing the MCP server source, or
  - a Repomix “packed repo” file (XML).
- Perform read-only static analysis (no code execution).
- Produce a standardized, engineer-first report:
  - prioritized findings with evidence and excerpts,
  - explicit unknowns that block confidence,
  - SAFE-MCP technique coverage appendix.
- Output a machine-readable JSON report suitable for CI automation.
- Make audit runs reproducible and debuggable.

## MVP scope

The auditor’s long-term goal is broad MCP ecosystem support, but the MVP defines an explicit minimum supported set to keep extraction heuristics and testing tractable.

MVP supported target ecosystems:

- Python MCP servers
- Node.js / TypeScript MCP servers

Best-effort (future enhancement): other languages and frameworks.

MVP requirements per ecosystem:

- Python:
  - detect common dependency manifests (`pyproject.toml`, `requirements.txt`, `poetry.lock`, `uv.lock`)
  - detect MCP server entrypoints and tool registrations using common patterns
- Node/TypeScript:
  - detect dependency manifests (`package.json`, lockfiles)
  - detect MCP server entrypoints and tool registrations using common patterns

## Non-goals

- Dynamic testing, fuzzing, or running the MCP server.
- Verifying runtime environment, infrastructure, or deployment configuration not present in the repository.
- Connecting to external MCP servers to “probe” tool behavior.
- Remediation PR generation (may be a future enhancement).

## Users and personas

- Software engineers maintaining an MCP server.
- Security engineers reviewing an MCP server.
- OSS maintainers auditing MCP servers from the internet.

Primary persona: engineers who need actionable fixes.

## User stories

- As an engineer, I can run the auditor against a repo directory and get a prioritized list of findings with file/line evidence and excerpts.
- As an engineer, I can run the auditor against a Repomix XML and get the same report format.
- As an engineer, I can diff JSON reports over time to track regressions.
- As an engineer, I see an explicit “needs review” status when the auditor cannot prove key properties.

## Key decisions (locked)

- Outputs: Markdown + JSON.
- Include raw excerpts in reports.
- Stable finding IDs.
- Unknowns are a non-passing gate.
- Engineer-first report ordering.

## Technology choices

### Python dependency management (uv)

This project uses `uv` for all Python dependency and environment management.

- Dependencies are declared in `pyproject.toml`.
- The project uses a committed `uv.lock` to ensure reproducible installs.
- `uv` manages the project virtual environment under `.venv`.
- Developer workflows should prefer `uv run ...` to guarantee commands run in a locked environment (keeps `pyproject.toml`, `uv.lock`, and `.venv` in sync).

Common workflows (illustrative):

- Initialize project: `uv init`
- Add/remove dependencies: `uv add ...`, `uv remove ...`
- Update lockfile: `uv lock`
- Sync environment from lockfile: `uv sync`

References:

- `https://docs.astral.sh/uv/`
- `https://docs.astral.sh/uv/guides/projects/`

### CLI framework (Typer)

The auditor CLI is implemented with Typer to provide strong UX defaults and type-driven argument validation.

- Command groups and subcommands (e.g., `audit`, `version`, `schema`) map naturally to Typer apps.
- Automatic `--help` and optional shell completion improve discoverability.
- Type hints (e.g., `Path`, `Enum`) provide built-in validation and better error messages.

References:

- `https://typer.tiangolo.com/`
- `https://typer.tiangolo.com/tutorial/`

### Packaging and installation

The auditor is distributed as a Python package that installs a `safe-mcp-auditor` CLI entrypoint.

- The package must define a console script entrypoint in `pyproject.toml`.
- Supported platforms: Linux and macOS (Windows best-effort).
- Minimum Python version: 3.10.

Recommended installation methods:

- User install (isolated): `uv tool install safe-mcp-auditor`
- Dev install: `uv sync` then `uv run safe-mcp-auditor ...`

## Inputs

### Input types

1. Directory input
   - Path to a local folder containing the MCP server code.

2. Repomix input
   - Path to a Repomix XML file containing a packed repository.
   - The Repomix file is treated as read-only; any remediation would happen in the original source, not the packed file.

### Target naming

Target name is derived deterministically in this order:

1. CLI override: `--target-name` (slugified)
2. Directory input: directory basename (slugified)
3. Repomix input:
   - repo name or URL from Repomix metadata, if present (slugified)
   - otherwise Repomix filename basename (slugified)
4. Fallback: `unknown-target`

### Input fingerprint (hash)

Each run generates an `<input-hash>` used in the output filename.

Recommended approach:

- Directory mode: compute a stable hash of relative file paths included in scope plus file content hashes, ignoring excluded paths.
- Repomix mode: hash the Repomix file contents.

Use an 8- to 12-character prefix of a cryptographic hash.

## Output artifacts

### Output location

- All output is written under `reports/`.
- Reports are never overwritten unless explicitly requested.

### Output files

- `reports/<target-name>-<input-hash>-safe-mcp-audit.json`
- `reports/<target-name>-<input-hash>-safe-mcp-audit.md`

### Exit status

The CLI returns:

- `0` for `pass`
- non-zero for `needs_review` or `fail`

Unknowns always force a non-pass:

- If `unknowns[]` is non-empty: `status = needs_review` and exit non-zero.

## Report philosophy

- JSON is the canonical data model.
- Markdown is a deterministic rendering of JSON.
- Every claim in a finding must be supported by evidence.
- If the agent cannot prove applicability with evidence, it must record an “unknown” rather than guessing.

## SAFE-MCP alignment

### Reference artifacts in this repo

This repository includes local reference artifacts under `docs/references/` to support development and offline analysis:

- `docs/references/repomix-output-SAFE-MCP-safe-mcp.xml`
  - Repomix-packed snapshot of the upstream SAFE-MCP repository.
  - Purpose: provides an offline, single-file representation of SAFE-MCP techniques/mitigations/templates so the team (and the auditor design) can reliably reference SAFE-MCP fields and structure even when network access is restricted.
  - Design implication: the auditor’s report schema and coverage matrix should align to the technique/mitigation templates contained in this snapshot.

- `docs/references/crewai-safe-mcp-knowledge-outline.md`
  - Design notes describing how to build a minimal CrewAI agent with SAFE-MCP embedded as a Knowledge source.
  - Purpose: captures the initial “how we got here” and helps future contributors understand CrewAI Knowledge choices.

Runtime note: the production auditor fetches SAFE-MCP from GitHub at a pinned ref and builds a curated knowledge pack for CrewAI Knowledge. The Repomix snapshot is for development reference only. The report schema must remain aligned to SAFE-MCP’s technique/mitigation structure.

### Technique template alignment

SAFE-MCP technique template expectations (used to shape auditor outputs):

- Overview fields: Tactic, Technique ID, Severity, First Observed, Last Updated
- Attack vectors, prerequisites, and attack flow
- Impact assessment (CIA triad + scope)
- Detection methods (IoCs, Sigma rules, behavioral indicators)
- Mitigation strategies (preventive, detective, response)

The auditor will not replicate the entire technique template verbatim. Instead, it will:

- map findings to technique IDs,
- include CIA/scope summaries in findings,
- recommend SAFE-M mitigations,
- optionally reference SAFE-MCP detection rules.

## Core workflow

### High-level stages

1. Ingest and normalize input
2. Build a repo index (paths, languages, key entrypoints)
3. Extract MCP inventory (tools, resources, auth, transport, storage, egress)
4. Identify risk signals from inventory
5. Map risk signals to SAFE-MCP techniques
6. Consolidate into engineer-friendly findings
7. Enrich findings with SAFE-M mitigations and detection ideas
8. Write JSON and Markdown report

### Risk signals (MVP taxonomy)

A risk signal is a deterministic, evidence-backed observation about the target MCP that can be mapped to one or more SAFE-MCP techniques.

Risk signals must be represented in a structured form (for testing and repeatability):

- `id` (string)
- `type` (enum)
- `summary` (string)
- `evidence[]` (citations)
- `recommended_safe_techniques[]` (initial mapping candidates)

Initial MVP risk signal types:

- `filesystem_read` (tool can read arbitrary paths)
- `filesystem_write` (tool can write arbitrary paths)
- `command_exec` (tool can execute shell/commands)
- `network_egress_unrestricted` (outbound HTTP requests without allowlist)
- `network_egress_allowlisted` (outbound requests, allowlist present)
- `auth_missing` (no authn/authz for exposed transport)
- `oauth_flow_present` (OAuth integration present)
- `token_persistence` (tokens stored on disk/db)
- `tool_output_injection_risk` (tool output or external content passed to LLM without strict delimiters)
- `tool_description_injection_risk` (tool descriptions loaded from untrusted sources or not integrity-verified)
- `overprivileged_tool_schema` (broad schemas, wildcards, or missing constraints)
- `supply_chain_weakness` (missing lockfiles, unsigned releases, no SBOM)
- `logging_insufficient` (missing audit logs for tool loads/tool calls)
- `vector_store_usage` (vector store used for memory/knowledge in target MCP)

### Applicability rubric (techniques)

When populating `coverage[]`:

- `applicable`
  - Requires at least one direct evidence item showing a relevant capability or control gap in code/config/tool schema.
- `unknown`
  - Used when the technique might apply but cannot be proven with available evidence.
  - Unknowns must be mirrored into `unknowns[]` with explicit verification steps.
- `not_applicable`
  - Used only when there is explicit negating evidence (rare), not merely “not observed.”

### Read-only constraint

The auditing agent must not:

- execute code,
- run shell commands within the target repo,
- connect to MCP servers,
- mutate the target repo.

The only write action allowed is writing the report artifacts.

### Threat model and safety requirements

The auditor analyzes untrusted, internet-hosted MCP repositories. Treat the target repository as adversarial input.

Threats to explicitly design for:

- Prompt injection embedded in docs/comments/tool descriptions intended to steer the auditor.
- Malicious “instruction-like” strings embedded in tool schemas, error messages, or sample outputs.
- Denial-of-service via extremely large files, generated code, or pathological nesting.

Required safety controls:

- Evidence-first rule: every finding must cite evidence; no evidence means `unknown`.
- Goal integrity: target content must not be allowed to change the audit’s goals, tool allowlists, or output schema.
- Context isolation: when target text is passed to an LLM prompt, wrap it in explicit delimiters (e.g., `<mcp-code>...</mcp-code>`) and instruct the model that content inside delimiters is untrusted data.
- Tool restrictions: agents must only have read/search tools for the target repo; no network access to the target, no execution tools.
- Output validation: all CrewAI tasks must use `output_pydantic`/`output_json` with function guardrails to prevent prompt injection from breaking schema.
- Size limits: enforce max file size, max excerpt size, and max total tokens passed from repo content per task; overflow becomes `unknown` with instructions.

## CrewAI design

### Crew structure

Use a multi-task crew with strict tool allowlists per task.

Recommended roles:

- Inventory Extractor
  - Produces a normalized inventory model.
- Risk Signal Detector
  - Converts inventory into structured “risk signals.”
- SAFE-MCP Mapper
  - Maps risk signals to SAFE-MCP techniques.
- Finding Consolidator
  - Merges technique mappings into a smaller actionable backlog.
- Mitigation and Detection Enricher
  - Uses SAFE-MCP Knowledge to attach SAFE-M mitigations and detections.
- Report Writer
  - Produces JSON and renders Markdown.

### SAFE-MCP Knowledge usage

SAFE-MCP is incorporated into the auditor as CrewAI Knowledge so the crew can reliably retrieve canonical technique and mitigation definitions during mapping and enrichment.

Key design intent: `docs/references/repomix-output-SAFE-MCP-safe-mcp.xml` is excellent as an offline reference artifact, but it is not the preferred shape for Knowledge retrieval (it is a single, very large file and tends to produce noisier/less targeted retrieval).

#### SAFE-MCP Knowledge corpus (curated)

The Knowledge corpus must be built from SAFE-MCP source material as many small, topic-scoped documents (one technique/mitigation per file), rather than a monolithic packed file.

Minimum required sources (from SAFE-MCP repo):

- Framework overview:
  - `README.md`
  - `MITIGATIONS.md`
- Techniques:
  - `techniques/**/README.md`
- Mitigations:
  - `mitigations/**/README.md`

Optional sources (recommended for better engineering guidance):

- Detection rules (to support the report’s detection recommendations):
  - `techniques/**/detection-rule*.yml` and `techniques/**/detection-rule*.yaml`
- Technique/mitigation templates (to keep schema alignment with upstream conventions):
  - `techniques/TEMPLATE.md`, `techniques/TEMPLATE-CHECKLIST.md`
  - `mitigations/TEMPLATE.md`, `mitigations/TEMPLATE-CHECKLIST.md`

Explicit exclusions (not useful for Knowledge and adds noise):

- `**/test-logs.json`, `**/test_detection_rule.py`, `**/validate.sh`
- `techniques/**/examples/**` (code examples can be very verbose; include only if we later find it materially improves retrieval)
- Legal/community files (`LICENSE*`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, etc.)

#### Knowledge pack format (recommended)

To improve retrieval precision, build a normalized “knowledge pack” on disk where each SAFE-MCP entity becomes one file:

- Techniques: `SAFE-T####.md` (e.g., `SAFE-T1102.md`)
- Mitigations: `SAFE-M-#.md` (e.g., `SAFE-M-1.md`)

Each file should start with a short, consistent header block (frontmatter or a fixed markdown section) capturing:

- `id` (SAFE-T/SAFE-M)
- `title`
- `tactic` (for techniques)
- `severity` (for techniques)
- `category` / `effectiveness` / `complexity` (for mitigations)
- `source_path` (original SAFE-MCP path)
- `safe_mcp_reference` (tag/commit)

Follow the header with the original markdown body (or a lightly normalized version that preserves headings and links).

Also include a small index file to support broad lookups:

- `SAFE-MCP-INDEX.md` listing all techniques and mitigations (IDs + titles) and the pinned `safe_mcp_reference`.

#### Source of truth and pinning

The auditor must pin SAFE-MCP content to a specific tag or commit for reproducibility.

- Source of truth: a git ref (`safe_mcp_reference`) stored in application configuration and recorded in every report as `metadata.safe_mcp_reference`.
- SAFE-MCP sources are fetched from GitHub at the pinned ref and transformed into the curated knowledge pack format.

Recommended fetch mechanism:

- Use the GitHub CLI (`gh`) to fetch a specific commit/tag into a local cache (e.g., `data/safe-mcp-src/<safe_mcp_reference>/`).
- The app may optionally support a Python GitHub client in the future, but `gh` is sufficient for the MVP.

`docs/references/repomix-output-SAFE-MCP-safe-mcp.xml` remains a development reference artifact, not a required runtime source.

#### Knowledge index lifecycle (build vs run)

SAFE-MCP Knowledge is treated as a build artifact with its own lifecycle. Building/updating the SAFE-MCP knowledge index is intentionally separated from running an audit.

Lifecycle phases:

1. Fetch sources
   - Fetch SAFE-MCP repo at `safe_mcp_reference` into `data/safe-mcp-src/<ref>/`.
2. Build knowledge pack
   - Apply the curated include/exclude rules and write normalized, per-entity files into `knowledge/safe-mcp/<ref>/`.
   - Write a build manifest (e.g., `knowledge/safe-mcp/manifest.json`) including: `safe_mcp_reference`, embedder config, chunk settings, and a content hash over the knowledge pack.
3. Build embeddings index
   - Initialize CrewAI Knowledge sources pointing at the knowledge pack files and embed them into the CrewAI knowledge store.
4. Verify
   - Run a small retrieval smoke test (e.g., query `SAFE-T1102` and confirm expected title/sections are retrieved) to catch broken builds.

#### CLI commands for SAFE-MCP index management

Add a dedicated command group for SAFE-MCP knowledge lifecycle operations:

- `safe-mcp-auditor safe-mcp status` (shows configured ref, whether pack/index exist, and current manifest)
- `safe-mcp-auditor safe-mcp fetch --ref <tag|sha>` (download SAFE-MCP sources via `gh`)
- `safe-mcp-auditor safe-mcp build-pack --ref <tag|sha>` (generate `knowledge/safe-mcp/<ref>/` + manifest)
- `safe-mcp-auditor safe-mcp build-index --ref <tag|sha> [--force]` (embed into CrewAI storage)
- `safe-mcp-auditor safe-mcp verify --ref <tag|sha>` (retrieval smoke tests)

#### SAFE-MCP index artifact contract

The SAFE-MCP index lifecycle produces several on-disk artifacts. These artifacts define whether the SAFE-MCP index is present and valid.

Required artifacts (by purpose):

- Source checkout:
  - `data/safe-mcp-src/<ref>/` (required after `safe-mcp fetch`)
- Curated knowledge pack:
  - `knowledge/safe-mcp/<ref>/SAFE-T*.md`
  - `knowledge/safe-mcp/<ref>/SAFE-M-*.md`
  - `knowledge/safe-mcp/<ref>/SAFE-MCP-INDEX.md`
  - `knowledge/safe-mcp/<ref>/manifest.json`
- CrewAI embedding storage:
  - `.crewai_storage/knowledge/` (location controlled by `CREWAI_STORAGE_DIR`)
  - A SAFE-MCP-specific collection must exist (see collection naming below)

`manifest.json` is the source of truth for determining whether pack/index artifacts are current.

Minimum required `manifest.json` fields:

- `safe_mcp_reference` (tag/sha)
- `built_at` (ISO8601)
- `curation_rules_version` (string; bump whenever include/exclude rules change)
- `knowledge_pack_hash` (hash over normalized pack contents)
- `embedder` (provider + model/config)
- `chunking` (chunk size and overlap)
- `counts` (technique count, mitigation count, optional detection-rule count)

Collection naming:

- Crew-level SAFE-MCP knowledge must use a stable, explicit collection name (do not rely on a role name).
- Recommended: `collection_name = "safe-mcp"` (or `safe-mcp-<ref>` if you want multiple versions to coexist).

#### SAFE-MCP index staleness checks

The auditor must treat the SAFE-MCP index as stale if any of the following is true:

- Configured `safe_mcp_reference` differs from `manifest.safe_mcp_reference`.
- The knowledge pack hash computed from `knowledge/safe-mcp/<ref>/` differs from `manifest.knowledge_pack_hash`.
- The embedder config differs from `manifest.embedder` (prevents embedding dimension mismatch).
- Chunking parameters differ from `manifest.chunking`.
- The CrewAI storage directory does not contain the SAFE-MCP collection, or it is empty.
- `safe-mcp verify` has not been successfully run for the current ref (optional but recommended; can be captured as a `verified_at` field).

#### External tool requirements for SAFE-MCP fetch

- `gh` is required for `safe-mcp fetch`.
- If `gh` is missing or not authenticated appropriately, the command must fail with a clear error message and remediation steps.

#### CrewAI Knowledge storage and reset mechanics

- SAFE-MCP knowledge sources are attached at crew level (`Crew(..., knowledge_sources=[...])`) so all roles share the same canonical framework context.
- Store the vector DB inside the project (e.g., set `CREWAI_STORAGE_DIR=./.crewai_storage`) to support repeat runs and easy CI cleanup.
- Rebuild triggers:
  - `safe_mcp_reference` changed
  - knowledge pack content hash changed
  - embedder config changed (common cause of embedding-dimension mismatch)
  - chunking parameters changed
- When a rebuild trigger occurs, the app must clear and rebuild the knowledge store for SAFE-MCP.
  - Preferred: call `crew.reset_memories(command_type='knowledge')` before re-embedding.
  - Operational fallback: `crewai reset-memories --knowledge`.

#### Audit runtime behavior (hard-fail)

The `audit` command must not implicitly rebuild SAFE-MCP Knowledge.

- If the SAFE-MCP index is missing or stale relative to the configured `safe_mcp_reference` and manifest, `audit` must hard-fail with a clear error and instructions to run `safe-mcp-auditor safe-mcp build-index --ref <ref>`.

#### Target MCP code handling

- Target MCP code is not persisted in a long-lived vector store by default.
  - Preferred: direct read/search + structured extraction.
  - Optional future enhancement: ephemeral, per-run indexing for very large repos.

### Reliability mechanisms

- Deterministic model settings (temperature 0).
- Structured outputs (Pydantic/JSON) for each stage.
- Guardrails to validate and repair structured outputs.
- Explicit confidence ratings.

### CrewAI framework features relevant to this app

These CrewAI capabilities are particularly relevant for building a safe, reproducible, read-only auditor:

- Flows: event-driven orchestration and state for multi-step audits, resumability, and chunking large repos into deterministic stages. See `https://docs.crewai.com/en/concepts/flows`.
- Processes: define orchestration semantics (sequential for deterministic pipelines; hierarchical for manager-led validation/delegation). See `https://docs.crewai.com/en/concepts/processes`, `https://docs.crewai.com/en/learn/sequential-process`, and `https://docs.crewai.com/en/learn/hierarchical-process`.
- Planning and reasoning: allow consistent pre-planning before tasks, which improves repeatability on complex audits. See `https://docs.crewai.com/en/concepts/planning` and `https://docs.crewai.com/en/concepts/reasoning`.
- Collaboration and delegation controls: restrict delegation to a coordinator/manager role to prevent tool sprawl and uncontrolled exploration. See `https://docs.crewai.com/en/concepts/collaboration` and `https://docs.crewai.com/en/concepts/agents`.
- Tool hooks and LLM hooks: enforce read-only behavior as a hard policy by blocking unsafe tools (writes, exec, outbound network) and optionally transforming/redacting what is sent to models. See `https://docs.crewai.com/en/learn/tool-hooks` and `https://docs.crewai.com/en/learn/llm-hooks`.
- Event listeners: capture an audit trail and metrics for tool calls/task transitions; useful for debugging and for generating “evidence-first” reports. See `https://docs.crewai.com/en/concepts/event-listener`.
- Observability and telemetry: tracing/telemetry are helpful for debugging, but should be treated as potential data exfil paths (disable or minimize in sensitive environments). See `https://docs.crewai.com/en/observability/overview` and `https://docs.crewai.com/en/telemetry`.
- Caching: improve performance, but cache invalidation must be keyed to the input fingerprint to avoid stale audit results. See `https://docs.crewai.com/en/concepts/tools`, `https://docs.crewai.com/en/concepts/agents`, and `https://docs.crewai.com/en/concepts/crews`.
- CLI and testing: use the CrewAI CLI for standardized project scaffolding and `crewai test` for regression testing (schema stability, stable IDs, and unknowns gating). See `https://docs.crewai.com/en/concepts/cli` and `https://docs.crewai.com/en/concepts/testing`.
- MCP integration security: assume tool metadata injection is a real threat; only connect to trusted MCP servers and aggressively filter tool exposure. See `https://docs.crewai.com/en/mcp/security`.

## Evidence model

Every finding and unknown must include evidence entries.

Evidence entry fields:

- `path`: relative file path
- `line_start`: 1-based line number
- `line_end`: 1-based line number
- `excerpt`: raw excerpt (bounded in length)
- `notes`: why this is relevant evidence

Repomix mode:

- `path` references the `<file path="...">` in the Repomix.
- `line_start`/`line_end` refer to line numbers within that file’s embedded content.

## Findings model

### Severity

Two distinct concepts may be stored:

- SAFE-MCP technique severity (baseline from the framework)
- Environment severity (how severe it is for this implementation)

Engineer-facing severity should represent environment severity.

Severity levels:

- `critical`, `high`, `medium`, `low`

### Confidence

Confidence levels:

- `high`: direct evidence in code/config
- `medium`: strong inference with partial evidence
- `low`: weak inference (should likely be captured as unknown)

### Stable finding IDs

Findings should have stable IDs to support diffing across runs.

Recommended ID derivation:

- Normalize inputs:
  - sorted SAFE technique IDs
  - primary evidence path
  - primary evidence line_start
  - a “finding type key” (short string)

- Compute ID:
  - `finding_id = "F-" + sha256(normalized_string)[0:12]`

Do not include excerpts in the hash.

## Unknowns model (non-pass gate)

Unknowns represent questions the auditor could not answer with evidence.

Each unknown must include:

- what is unknown
- why it matters
- how to verify (what file/config/log to check)
- related SAFE-MCP techniques

Unknowns are always reported and cause `status = needs_review`.

## JSON report schema (v1)

The JSON report is the canonical output. Markdown is rendered from this JSON.

### Top-level fields

- `schema_version` (string, required): semantic schema version (e.g., `1.0.0`).
- `status` (enum, required): `pass|needs_review|fail`.
  - `needs_review` is required when `unknowns[]` is non-empty.
- `metadata` (object, required)
- `inventory` (object, required)
- `findings` (array, required)
- `unknowns` (array, required)
- `coverage` (array, required)

### Metadata model

`metadata` (required fields):

- `target_name` (string)
- `input_type` (enum): `directory|repomix`
- `input_path` (string): user-supplied path (for traceability)
- `input_hash` (string): hash used in report filenames
- `analyzed_at` (string): ISO8601 timestamp
- `app_version` (string): auditor version
- `safe_mcp_reference` (string): pinned SAFE-MCP tag/sha
- `safe_mcp_manifest_path` (string): path to the knowledge pack manifest
- `safe_mcp_knowledge_pack_hash` (string)
- `models` (object):
  - `llm` (object): provider/model/temperature
  - `embedder` (object): provider/model
- `run_id` (string): UUID for correlating logs
- `scope` (object):
  - `included_paths` (array[string])
  - `excluded_paths` (array[string])

### Inventory model

`inventory` captures evidence-backed facts about the target MCP.

Recommended fields:

- `languages` (array[string])
- `entrypoints` (array[object]): `{ path, kind, evidence[] }`
- `mcp_transport` (enum|string): `stdio|http|sse|streamable_http|unknown`
- `auth` (object): `{ present, mechanism, evidence[] }`
- `tools` (array[object]):
  - `name` (string)
  - `description` (string)
  - `capabilities` (array[string])
  - `schema` (object|null)
  - `evidence` (array[evidence])
- `resources` (array[object]): `{ name, description, evidence[] }`
- `storage` (array[object]): `{ kind, details, evidence[] }`
- `network_egress` (object): `{ present, allowlist, evidence[] }`
- `dependencies` (object): `{ manifests[], lockfiles[], evidence[] }`

### Evidence object

Evidence is a list of citations supporting a claim.

- `path` (string)
- `line_start` (int)
- `line_end` (int)
- `excerpt` (string)
- `notes` (string)

### Finding object

`findings[]` is the primary engineer-facing backlog.

Required fields:

- `id` (string): stable finding ID (e.g., `F-<hash>`)
- `title` (string)
- `severity` (enum): `critical|high|medium|low`
- `confidence` (enum): `high|medium|low`
- `safe_mcp` (object):
  - `techniques` (array[string])
  - `tactics` (array[string])
  - `recommended_mitigations` (array[string])
  - `detection_rule_paths` (array[string])
- `what_is_happening` (string)
- `why_it_matters` (object):
  - `cia` (object): `{ confidentiality, integrity, availability }`
  - `scope` (string)
- `recommendation` (string)
- `evidence` (array[evidence])

### Unknowns model

`unknowns[]` are non-passing gate items.

Required fields:

- `id` (string): stable unknown ID (e.g., `U-<hash>`)
- `question` (string)
- `why_it_matters` (string)
- `how_to_verify` (string)
- `related_techniques` (array[string])
- `evidence` (array[evidence])

### Coverage model

`coverage[]` describes SAFE-MCP technique coverage and links back to findings.

Required fields:

- `technique_id` (string)
- `tactic` (string)
- `safe_mcp_severity` (enum|string)
- `applicability` (enum): `applicable|not_applicable|unknown`
- `confidence` (enum): `high|medium|low`
- `linked_finding_ids` (array[string])

### Determinism requirements

To support diffing and strict TDD:

- JSON object keys are written in deterministic order.
- Arrays are sorted deterministically:
  - `findings` by severity desc, then `id`
  - `coverage` by `technique_id`
  - `tools` by `name`
- Timestamps are recorded only in `metadata.analyzed_at` and `manifest.built_at`.

## Markdown report template

### Sections

1. Summary
   - Status
   - Counts by severity
   - Top findings
   - Unknowns summary
2. Findings (Prioritized)
   - For each:
     - Title, severity, confidence
     - SAFE technique mappings
     - Evidence table with file/line links and excerpt
     - Recommendation
     - Suggested SAFE-M controls
3. Quick hardening checklist
4. Unknowns / Needs manual review
5. Appendix A: Inventory
6. Appendix B: SAFE-MCP technique coverage matrix

## CLI requirements

This application provides a Typer-based CLI.

- When installed as a package, users run `safe-mcp-auditor ...` directly.
- During local development, prefer `uv run safe-mcp-auditor ...` to ensure a consistent, locked environment.

### Example commands

- Directory:

  ```bash
  safe-mcp-auditor audit --path ./path/to/mcp

  # Dev workflow
  uv run safe-mcp-auditor audit --path ./path/to/mcp
  ```

- Repomix:

  ```bash
  safe-mcp-auditor audit --repomix ./path/to/repomix.xml

  # Dev workflow
  uv run safe-mcp-auditor audit --repomix ./path/to/repomix.xml
  ```

- Override target name:

  ```bash
  safe-mcp-auditor audit --path ./repo --target-name github-mcp-server

  # Dev workflow
  uv run safe-mcp-auditor audit --path ./repo --target-name github-mcp-server
  ```

### CLI outputs

- Print report paths.
- Print status and exit code semantics.

## Logging and audit trail

This tool is a security auditor; logs must be sufficient to reproduce and debug results.

Logging requirements:

- Default behavior: log high-level progress to stderr (human readable).
- Optional structured logs: `--log-json <path>` writes newline-delimited JSON events.
- Optional debug mode: `--verbose` increases detail (file discovery counts, which analyzers ran).

Minimum events to log (structured or human-readable):

- Run metadata: `run_id`, `target_name`, `input_hash`, `safe_mcp_reference`.
- SAFE-MCP lifecycle actions: fetch/build-pack/build-index/verify start and end.
- Audit phases: ingest/index/inventory/risk-signal/mapping/report-writing start and end.
- Hard-fail reasons: missing/stale SAFE-MCP index checks and which check failed.

Privacy note: because the auditor includes code excerpts in reports, logs should avoid echoing large excerpts by default. Logs should refer to paths/line numbers, not full snippets.

## Testing requirements

This project follows a strict TDD workflow and requires fully offline test execution in CI.

### Testing strategy (TDD-first)

Core principle: keep deterministic logic outside the LLM loop. Use CrewAI features like `output_pydantic` and function-based guardrails to make behavior testable and repeatable.

References:

- CrewAI testing: `https://docs.crewai.com/en/concepts/testing`
- Task structured outputs and guardrails: `https://docs.crewai.com/en/concepts/tasks`
- Knowledge storage, events, and reset: `https://docs.crewai.com/en/concepts/knowledge`

### Offline-only constraint

All CI tests must run without network access. Any integration points that normally use network must be mocked:

- `gh` calls used by `safe-mcp-auditor safe-mcp fetch` must be mocked (subprocess stub or similar).
- Any LLM calls (including any judge/evaluator LLM) must be mocked or replaced with deterministic fixtures.

### Test fixtures and golden files

To support strict offline TDD, the repo must include a small suite of fixtures:

- MCP fixtures (directory mode): small sample MCP repos with known properties and expected findings.
- MCP fixtures (repomix mode): repomix-packed versions of the same fixtures to validate parity.
- SAFE-MCP fixtures: a tiny SAFE-MCP knowledge pack subset used for retrieval tests (a few techniques + mitigations).
- Golden outputs:
  - golden JSON reports for fixture runs (used for snapshot tests)
  - golden Markdown reports rendered from the golden JSON

Golden outputs must be regenerated only when the report schema or rendering rules intentionally change.

### Mocking strategy

All offline tests must mock external boundaries:

- `gh` fetch
  - mock subprocess calls and provide a local SAFE-MCP repo fixture as the “downloaded” output.
- LLM calls
  - inject a fake LLM implementation that maps deterministic prompt keys to fixture responses.
  - prefer stable prompt keys (task name + stage + input hash) rather than exact prompt string matching, to reduce brittleness.
- CrewAI storage
  - set `CREWAI_STORAGE_DIR` to a temp directory per test run to prevent cross-test contamination.

### Unit tests (no CrewAI, no LLM)

These are the primary red/green tests and must be fully deterministic:

- Directory indexing and Repomix parsing.
- SAFE-MCP knowledge pack generation (curation rules, file generation, manifest hashing).
- Input fingerprinting and stable finding ID hashing.
- JSON report model validation (Pydantic/schema) and Markdown rendering as a pure function of JSON.
- Index staleness detection logic (missing index, ref mismatch, embedder mismatch, hash mismatch).

### CLI tests (Typer)

Test the CLI contract and exit codes using Typer/Click’s testing utilities:

- `safe-mcp-auditor safe-mcp status|fetch|build-pack|build-index|verify`.
- `safe-mcp-auditor audit ...` hard-fails when SAFE-MCP index is missing or stale.

All CLI tests must be offline and use mocked subprocess/file fixtures.

### CrewAI integration tests (no network)

Verify the crew wiring and task contracts without relying on a real model:

- Inject a fake LLM with fixed prompt→response fixtures.
- Use `Task(output_pydantic=...)` / `Task(output_json=...)` to assert structured outputs.
- Use function-based guardrails to enforce schema, stable IDs, ordering, and required fields.

### Knowledge/retrieval tests (no network)

Test SAFE-MCP retrieval behavior using a small local fixture knowledge pack:

- Set `CREWAI_STORAGE_DIR` to a per-test temp directory.
- Build the knowledge store from fixture files.
- Assert that retrieval returns expected chunks for known queries (e.g., `SAFE-T1102`).
- Optionally attach an event listener to assert that knowledge retrieval events occurred and capture retrieved chunk counts.

### Optional quality evaluation (non-gating)

CrewAI’s `crewai test` runs an LLM-judged scoring loop and is not deterministic enough for strict TDD gating.

- If used, it should run only as a non-blocking, manual, or nightly quality check.
- It must not be required for PR correctness in a fully offline CI environment.

## Acceptance criteria (MVP)

- The auditor accepts both input types.
- The auditor generates both report files under `reports/`.
- The JSON report validates against a published schema version.
- The Markdown report includes evidence pointers and excerpts.
- Unknowns cause non-passing status and non-zero exit.
- Findings include SAFE technique mappings and recommended SAFE mitigations.
- The project uses `uv` for dependency management and includes a committed `uv.lock`.
- The CLI is implemented with Typer and provides `--help` for all commands.

## Future enhancements

- Optional per-run ephemeral code indexing for very large repos.
- Optional “fetch by URL” mode to clone public MCP repos.
- Optional SBOM generation and dependency vulnerability integration.
- Optional GitHub Actions integration (publish report artifact).
