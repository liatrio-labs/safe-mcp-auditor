# CrewAI agent Knowledge store for SAFE-MCP

## Goal

Create a minimal CrewAI agent that can answer questions about the SAFE-MCP
framework by using CrewAI’s built-in **Knowledge** feature
(vector-store-backed retrieval) instead of hand-rolling a separate RAG pipeline.

Primary upstream references:

- CrewAI Knowledge concept docs: <https://docs.crewai.com/en/concepts/knowledge>
- SAFE-MCP repository: <https://github.com/SAFE-MCP/safe-mcp>
- SAFE-MCP site: <https://safemcp.org/>

## Tools and components you’ll use

### Runtime and packages

- Python 3.10+
- `crewai` (agents/crews/tasks + knowledge)
- A supported embedding provider for knowledge (commonly OpenAI embeddings)
- CrewAI’s default local knowledge storage (backed by a persistent vector DB,
  typically Chroma)

### Data source

- The SAFE-MCP markdown corpus, primarily:
  - `techniques/**/README.md`
  - `mitigations/**/README.md`
  - `README.md` and `MITIGATIONS.md`

## How CrewAI Knowledge works (key findings)

- Knowledge is defined via **knowledge sources** attached at either:
  1. **Crew level** (`Crew(..., knowledge_sources=[...])`) for shared knowledge.
  2. **Agent level** (`Agent(..., knowledge_sources=[...])`) for role-specific knowledge.
- Knowledge sources are embedded and stored in a persistent vector store. Conceptually:
  - each agent role becomes its own collection
  - the crew knowledge becomes a separate collection (commonly named `crew`)
- The knowledge store is initialized during `crew.kickoff()`.
- Storage location is under CrewAI’s storage directory (see `CREWAI_STORAGE_DIR`
  and `crewai.utilities.paths.db_storage_path()` in docs).
- You can reset the knowledge collections using:
  - `crew.reset_memories(command_type='agent_knowledge')`
  - `crew.reset_memories(command_type='knowledge')`

## Outline: build a simple SAFE-MCP-aware agent

### 1) Create a small project folder layout

Recommended (simple and local-first):

- `safe_mcp_agent/`
  - `pyproject.toml` (or `requirements.txt`)
  - `main.py`
  - `.env` (LLM + embedding provider credentials)
  - `data/`
    - `safe-mcp/` (cloned SAFE-MCP repo)
  - `.crewai_storage/` (optional, local knowledge persistence)

Tip: set `CREWAI_STORAGE_DIR=./.crewai_storage` so the vector DB stays inside
your repo/project (handy for demos and repeatability).

### 2) Acquire SAFE-MCP content

1. Clone the repository into `data/`:

   ```bash
   git clone https://github.com/SAFE-MCP/safe-mcp ./data/safe-mcp
   ```

2. Decide what you want embedded:

- Minimum viable corpus:
  - `./data/safe-mcp/README.md`
  - `./data/safe-mcp/MITIGATIONS.md`
- More complete corpus:
  - all technique READMEs under `./data/safe-mcp/techniques/**/README.md`
  - all mitigation docs under `./data/safe-mcp/mitigations/**/README.md`

### 3) Create KnowledgeSources pointing at SAFE-MCP files

CrewAI provides built-in knowledge sources like `TextFileKnowledgeSource`. It can
be used to load text-based documents, including markdown files (`.md`) as plain
text.

Example: collect SAFE-MCP markdown files and create a knowledge source.

```python
from pathlib import Path

from crewai.knowledge.source.text_file_knowledge_source import (
    TextFileKnowledgeSource,
)

SAFE_MCP_ROOT = Path("./data/safe-mcp")

file_paths = [
    str(SAFE_MCP_ROOT / "README.md"),
    str(SAFE_MCP_ROOT / "MITIGATIONS.md"),
]

file_paths += [str(p) for p in (SAFE_MCP_ROOT / "techniques").rglob("README.md")]
file_paths += [str(p) for p in (SAFE_MCP_ROOT / "mitigations").rglob("README.md")]

safe_mcp_source = TextFileKnowledgeSource(file_paths=file_paths)
```

Best-practice notes:

- Start with the minimal corpus first (faster embedding), then expand.
- If retrieval feels “noisy”, reduce the corpus or tweak chunking/overlap on a
  source that supports it.

### 4) Create an agent that uses SAFE-MCP knowledge

You can attach knowledge at the crew level (shared) or agent level (specialized).
For a single-agent demo, crew-level is easiest.

```python
import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

# Keep knowledge DB local to project
os.environ.setdefault("CREWAI_STORAGE_DIR", "./.crewai_storage")

# Build your knowledge source(s)
safe_mcp_source = TextFileKnowledgeSource(
    file_paths=[
        "./data/safe-mcp/README.md",
        "./data/safe-mcp/MITIGATIONS.md",
        # Optionally add techniques/**/README.md and mitigations/**/README.md
    ]
)

# Deterministic responses help when validating retrieval
llm = LLM(model="gpt-4o-mini", temperature=0)

agent = Agent(
    role="SAFE-MCP Security Analyst",
    goal="Answer questions about SAFE-MCP tactics, techniques, and mitigations.",
    backstory=(
        "You help developers and security teams understand threats "
        "in MCP ecosystems and map mitigations to specific SAFE-MCP techniques."
    ),
    llm=llm,
    verbose=True,
)

task = Task(
    description=(
        "Given the question: {question}, answer using SAFE-MCP content. "
        "Include technique IDs (e.g., SAFE-T1102) when relevant and summarize "
        "mitigations and detections from the knowledge base."
    ),
    expected_output="A concise, referenced answer grounded in SAFE-MCP.",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    knowledge_sources=[safe_mcp_source],
    verbose=True,
)

result = crew.kickoff(
    inputs={"question": "What is SAFE-T1102 and how can we mitigate it?"}
)
print(result)
```

### 5) Verify that Knowledge is actually being used

The CrewAI docs show simple “does retrieval return anything?” checks:

```python
# After kickoff
if hasattr(agent, "knowledge") and agent.knowledge:
    results = agent.knowledge.query(["SAFE-T1102"])  # a very specific probe
    print(f"Found {len(results)} chunks")
```

Also check your knowledge storage folder to confirm collections were created
(one for `crew`, and one per agent role if you used agent-level knowledge).

### 6) Iterate toward a useful “security helper” agent

Once the MVP works:

- Expand corpus to all `techniques/**/README.md` and `mitigations/**/README.md`.
- Add a second agent role if you want separation of concerns:
  - “Technique Mapper” (finds relevant SAFE-* techniques)
  - “Mitigation Writer” (summarizes mitigations/detections)
- Add output structure requirements (e.g., always return `Technique`, `Threat`,
  `Mitigations`, `Detections`, `Related ATT&CK mappings`).
- Consider using a higher-quality embedding model if retrieval quality is poor.

## Suggested prompts to validate retrieval

- "List the tactics SAFE-MCP covers and what they mean."
- "Explain a tool poisoning attack in MCP and cite the SAFE-* technique ID."
- "What are mitigations/detections for prompt injection in MCP?"
- "Which SAFE-* techniques relate to persistence via memory/vector-store poisoning?"

## Practical security notes (relevant to SAFE-MCP)

When you embed a security framework into a knowledge store, treat the knowledge
DB as an attack surface:

- If the knowledge corpus is updated from untrusted sources, it becomes a
  vector-store poisoning risk.
- Pin SAFE-MCP inputs to trusted commits/tags when embedding for production.
- Control who can write to the knowledge storage directory.
- Periodically reset and rebuild the knowledge store when the corpus changes.
