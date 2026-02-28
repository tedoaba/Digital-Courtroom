# Implementation Plan: Bounded-Concurrency Multi-Agent Evaluation

**Branch**: `012-bounded-agent-eval` | **Date**: 2026-02-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-bounded-agent-eval/spec.md`

## Summary

This feature refactors the multi-agent evaluation architecture to eliminate uncontrolled fan-out (3 agents x 10 dimensions = 30 parallel calls) and replace it with a production-safe, bounded concurrency model using `asyncio.Semaphore`. It ensures system stability by limiting total in-flight LLM calls across all agents and implementing robust error recovery with exponential backoff.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `langgraph`, `pydantic`, `asyncio`, `uv`  
**Storage**: N/A  
**Testing**: `pytest`  
**Target Platform**: Linux/Windows/macOS (Python environment)
**Project Type**: Agent Orchestration Logic  
**Performance Goals**: Explicitly bounded N parallel LLM calls (configurable via `.env`)  
**Constraints**: Global concurrency limit across all parallel agents; Exponential backoff (1s initial, 60s max)  
**Scale/Scope**: 3 agents, 10 dimensions each (30 total tasks) throttled by a shared semaphore.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle                    | Status | How satisfied                                                 |
| ---------------------------- | ------ | ------------------------------------------------------------- |
| I. Spec-Driven Development   | PASS   | Formal spec exists at `specs/012-bounded-agent-eval/spec.md`. |
| II. Test-Driven Development  | PASS   | Tasks will require tests before implementation.               |
| IV. Schema-First Design      | PASS   | Configuration will use Pydantic models.                       |
| VI. Parallel-Safe Reducers   | PASS   | Existing LangGraph state merging will be preserved/enhanced.  |
| VII. Explicit Error Handling | PASS   | exponential backoff (1s-60s) for 429/503 errors.              |
| XIV. Parallel Fan-Out/Fan-In | PASS   | Design respects fan-out but adds a throttling layer.          |
| XXIII. uv manager            | PASS   | All commands and environment management via `uv`.             |

## Project Structure

### Documentation (this feature)

```text
specs/012-bounded-agent-eval/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (if needed)
└── tasks.md             # Phase 2 output (generated separately)
```

### Source Code (repository root)

```text
src/
├── state.py             # Update state if needed for batching
├── graph.py             # Wiring of the throttled evaluation logic
├── nodes/
│   └── judicial_nodes.py # Implementation of bounded concurrency
└── tools/
    └── llm_bridge.py    # Potential new bridge for throttled LLM calls

tests/
├── integration/
│   └── test_bounded_eval.py
└── unit/
    └── test_concurrency_controller.py
```

**Structure Decision**: Single project structure follows the existing repository layout in `src/`. No structural changes but logic refactoring in `src/nodes/` and addition of a helper/bridge if necessary.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
