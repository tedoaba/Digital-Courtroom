# Implementation Plan: Parallel Detective Agents (Layer 1)

**Branch**: `006-parallel-detectives` | **Date**: 2026-02-25 | **Spec**: [specs/006-parallel-detectives/spec.md](spec.md)
**Input**: Feature specification from `/specs/006-parallel-detectives/spec.md`

## Summary

Implement the `RepoInvestigator`, `DocAnalyst`, and `VisionInspector` nodes within the `detectives.py` module. These nodes will leverage specialized tools (`repo_tools`, `doc_tools`, `vision_tools`) to gather factual evidence (cloned code, AST structures, PDF text, and diagram classifications) into immutable `Evidence` instances. The implementation will ensure parallel execution compatibility, strict 60-second timeouts, and graceful error handling as mandated by the project architecture.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `langgraph`, `pydantic`, `docling`, `git`, `gitingest`, **Gemini Pro (Multimodal)**  
**Storage**: Transient state in `AgentState`, temporary isolated directories for Git clones.  
**Testing**: `pytest` with `pytest-mock` for dependency isolation.  
**Observability**: **LangSmith** tracing configured for all node executions.  
**Target Platform**: Any environment supporting Python and `git`.  
**Project Type**: Multi-agent Orchestration System.  
**Performance Goals**: Each detective node must complete processing within 60 seconds (SC-005).  
**Constraints**: No `os.system()`, mandatory `tempfile` isolation, AST-based analysis only, **LLM temperature=0**.
**Scale/Scope**: Layer 1 of the Digital Courtroom architecture.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

1. **Principle III (Parallelism)**: Nodes are designed for fan-out execution.
2. **Principle IV & V (Schema/Typing)**: Uses `Evidence` Pydantic model and `AgentState` TypedDict.
3. **Principle VII (Error Handling)**: Implements graceful failure with `found=False` (FR-005).
4. **Principle IX (Fact vs Opinion)**: Detectives strictly collect facts without scoring (FR-002).
5. **Principle XIV (Fan-Out)**: Implementation supports the parallel fan-out pattern required by the Layer 1 architecture.
6. **Principle XV (Sandboxing)**: Mandatory use of `tempfile` and `subprocess` list-form with timeouts (FR-003, FR-008).
7. **Principle XXII (Logging)**: Mandatory structured metrics logging (FR-009) and LangSmith tracing (FR-013).
8. **Principle XXIV (Determinism)**: Mandatory LLM `temperature=0` (FR-011).

### Design Re-Evaluation (Post-Phase 1)

- [x] All detectives return immutable `Evidence` objects (Principle XVI).
- [x] State merges via `Annotated` reducers in `AgentState` (Principle VI).
- [x] AST analysis is static; no code execution (Principle XV).
- [x] Standardized timeouts (60s) integrated into node contracts (Principle XV, FR-008).

## Project Structure

### Documentation (this feature)

```text
specs/006-parallel-detectives/
├── plan.md              # [x] Resolved
├── research.md          # [x] Resolved (Decision on AST/Docling)
├── data-model.md        # [x] Resolved (Evidence/State schema)
├── quickstart.md        # [x] Resolved
├── contracts/           # [x] Resolved (Detective Node signatures)
└── tasks.md             # Phase 2 output (generated separately)
```

### Source Code (repository root)

```text
src/
├── nodes/
│   └── detectives.py   # Implementation of L1 nodes
├── tools/
│   ├── repo_tools.py   # Git & AST forensic utilities
│   ├── doc_tools.py    # PDF & text analysis utilities
│   └── vision_tools.py # Image extraction & classification utilities
│
tests/
├── unit/
│   ├── nodes/
│   │   └── test_detectives.py
│   └── tools/
│       ├── test_repo_tools.py
│       ├── test_doc_tools.py
│       └── test_vision_tools.py
```

**Structure Decision**: Single project modular structure as defined by the Constitution (Principle XX).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
