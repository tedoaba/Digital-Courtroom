# Digital-Courtroom Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-24

## Active Technologies
- Python 3.11+ + `langgraph`, `pydantic`, `langchain` (for tracing), `python-json-logger` or standard `logging` with JSON formatter, `uv` (mandatory). (002-observability-error-handling)
- N/A (Standard Output stream) (002-observability-error-handling)
- Python 3.12+ + Pydantic v2, LangGraph, typing_extensions (003-pydantic-state-schema)
- N/A (Internal state management) (003-pydantic-state-schema)
- Python 3.12+ (Requires Generic Type hints and Pydantic v2) + `pydantic>=2.6.0`, `langgraph`, `typing_extensions` (003-pydantic-state-schema)
- Python 3.12 + `docling`, `pydantic`, `git` (CLI) (004-forensic-tools-sandbox)
- Transient files in `tempfile.TemporaryDirectory` (004-forensic-tools-sandbox)
- Python 3.12 + `langgraph`, `pydantic`, `python-json-logger` (via `src.utils.logger.StructuredLogger`) (005-context-builder-init)
- In-memory `AgentState` (005-context-builder-init)
- Python 3.11+ + `langgraph`, `pydantic`, `docling`, `git`, `gitingest`, Multimodal LLM (Gemini/OpenAI) (006-parallel-detectives)
- Transient state in `AgentState`, temporary isolated directories for Git clones. (006-parallel-detectives)
- Python 3.12 + LangGraph, Pydantic, `operator.ior` reducer (007-evidence-aggregator)
- LangGraph `AgentState` (In-memory dict-based state) (007-evidence-aggregator)
- Python 3.12 + LangGraph, Pydantic, LangChain (for LLM orchestration), `config.py` (internal configuration system) (008-judicial-nodes)
- N/A (Transient state resides in LangGraph `AgentState`) (008-judicial-nodes)
- Python 3.12 + LangGraph, Pydantic, operator (for reducers) (009-deterministic-synthesis)
- N/A (State-managed in LangGraph) (009-deterministic-synthesis)
- Python 3.12 + `jinja2`, `pathlib`, `pydantic` (010-report-generation)
- Local filesystem (`audit/reports/{repo_name}/`) (010-report-generation)
- Python 3.12 (standard for project) + `langgraph`, `pydantic`, `uv` (011-e2e-langgraph-wiring)
- Filesystem (Markdown reports in `audit/reports/`) (011-e2e-langgraph-wiring)
- Python 3.12 + `langgraph`, `pydantic`, `asyncio`, `uv` (012-bounded-agent-eval)
- Python 3.12+ + `langgraph`, `pydantic`, `langsmith`, `rich`, `cryptography` (013-ironclad-hardening)
- `.env` for standard config, AES-256 encrypted local store for secrets, SHA-256 hash chains for evidence integrity. (013-ironclad-hardening)
- Python 3.12 + `uv`, `docker`, `github-actions`, `ruff`, `hadolint`, `pip-audit` (014-devops-hardening)
- Local file system (volume mapped for `/audit` and `/reports`) (014-devops-hardening)

- Python 3.12+ (latest stable for optimal `uv` and Pydantic v2 support) + `langgraph`, `langchain`, `pydantic`, `python-dotenv`, `pytest`, `ruff` (001-foundational-scaffolding)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.12+ (latest stable for optimal `uv` and Pydantic v2 support): Follow standard conventions

## Recent Changes
- 014-devops-hardening: Added Python 3.12 + `uv`, `docker`, `github-actions`, `ruff`, `hadolint`, `pip-audit`
- 013-ironclad-hardening: Added Python 3.12+ + `langgraph`, `pydantic`, `langsmith`, `rich`, `cryptography`
- 012-bounded-agent-eval: Added Python 3.12 + `langgraph`, `pydantic`, `asyncio`, `uv`


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
