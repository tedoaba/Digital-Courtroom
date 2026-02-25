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
- 007-evidence-aggregator: Added Python 3.12 + LangGraph, Pydantic, `operator.ior` reducer
- 006-parallel-detectives: Added Python 3.11+ + `langgraph`, `pydantic`, `docling`, `git`, `gitingest`, Multimodal LLM (Gemini/OpenAI)
- 005-context-builder-init: Added Python 3.12 + `langgraph`, `pydantic`, `python-json-logger` (via `src.utils.logger.StructuredLogger`)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
