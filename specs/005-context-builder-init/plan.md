# Implementation Plan: ContextBuilder Initialization Node

**Branch**: `005-context-builder-init` | **Date**: 2026-02-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-context-builder-init/spec.md`

## Summary

The `ContextBuilder` node is the entry point (Layer 0) of the Digital Courtroom's `StateGraph`. Its primary responsibility is to bootstrap the execution state by validating the input `repo_url` and `pdf_path`, loading the machine-readable evaluation rubric (dimensions and synthesis rules), and initializing the parallel-safe state collections (`evidences`, `opinions`, `criterion_results`). This node ensures a "fast-fail" experience by identifying configuration errors before any LLM detective nodes are invoked.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `langgraph`, `pydantic`, `python-json-logger` (via `src.utils.logger.StructuredLogger`)  
**Storage**: In-memory `AgentState`  
**Testing**: `pytest`  
**Target Platform**: Python Runtime / CLI  
**Project Type**: AI Agent Orchestration Node  
**Performance Goals**: Input validation and rubric loading < 500ms  
**Constraints**: Strict regex validation for GitHub URLs; no shell metacharacters; no `localhost` or `file://` schemes.  
**Scale/Scope**: Single node implementation; dynamic rubric loading supporting 10+ dimensions.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

1. **Deterministic Logic (Const. III)**: The node uses standard Python libraries (`re`, `json`, `os`) for validation and loading. No LLM calls. (PASS)
2. **Schema-First (Const. IV)**: The node initializes the `AgentState` using Pydantic-backed structures (`Evidence`, `JudicialOpinion`). (PASS)
3. **Parallel-Safe Reducers (Const. VI)**: Initialization of empty collections ensures reducers (`operator.add`, `operator.ior`) have valid base types to operate on. (PASS)
4. **Isolated Error Handling (Const. VII)**: FR-007 follows the "fail gracefully" principle by appending to `state.errors` instead of crashing, allowing the graph to route to a terminal node. (PASS)
5. **Structured Logging (Const. XXII)**: Mandatory usage of `StructuredLogger` for entry/exit events. (PASS)
6. **Package Management (Const. XXIII)**: Implementation and testing will use `uv`. (PASS)

## Project Structure

### Documentation (this feature)

```text
specs/005-context-builder-init/
├── plan.md              # This file
├── research.md          # Decisions on validation & initialization
├── data-model.md        # State initialization schema
├── quickstart.md        # Execution guide
└── tasks.md             # Implementation tasks (Phase 2)
```

### Source Code (repository root)

```text
src/
├── nodes/
│   └── context_builder.py  # MAIN IMPLEMENTATION
├── utils/
│   └── logger.py           # Used for structured logging
├── exceptions.py           # Custom exception hierarchy
└── state.py                # AgentState definition
```

**Structure Decision**: The implementation will follow the modular architecture defined in **Constitution XX**, placing the node logic in `src/nodes/context_builder.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A       | N/A        | N/A                                  |
