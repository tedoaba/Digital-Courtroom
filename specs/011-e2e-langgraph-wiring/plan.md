# Implementation Plan: E2E LangGraph Orchestration & Edge Wiring

**Branch**: `011-e2e-langgraph-wiring` | **Date**: 2026-02-25 | **Spec**: [/specs/011-e2e-langgraph-wiring/spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-e2e-langgraph-wiring/spec.md`

## Summary

This feature involves the end-to-end orchestration of the Digital Courtroom swarm using LangGraph. It integrates all previously implemented nodes (`ContextBuilder`, `RepoInvestigator`, `DocAnalyst`, `VisionInspector`, `EvidenceAggregator`, `Prosecutor`, `Defense`, `TechLead`, `ChiefJustice`, and `ReportGenerator`) into a single, cohesive `StateGraph`. The implementation enforces hierarchical layer synchronization, parallel fan-out/fan-in for detectives and judges, deterministic synthesis rules, and robust error handling with partial report generation capabilities.

## Technical Context

**Language/Version**: Python 3.12 (standard for project)
**Primary Dependencies**: `langgraph`, `pydantic`, `uv`
**Storage**: Filesystem (Markdown reports in `audit/reports/`)
**Testing**: `pytest`
**Target Platform**: CLI / Python Runtime
**Project Type**: CLI / AI Agent Orchestrator
**Performance Goals**: Complete audit in < 5 minutes (standard repo); < 300s timeout per layer
**Constraints**: Deterministic routing, parallel-safe state merging, sandboxed tool calls
**Scale/Scope**: Integration of 10+ distinct nodes into a single orchestrator

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle                                      | Status | Requirement                                                        |
| ---------------------------------------------- | ------ | ------------------------------------------------------------------ |
| III. Deterministic LangGraph State Transitions | ✅     | Graph wiring uses deterministic predicates; no LLM routing.        |
| IV. Schema-First Design                        | ✅     | `AgentState` uses `TypedDict` with `Annotated` reducers.           |
| VI. Parallel-Safe State Reducers               | ✅     | `evidences` (operator.ior) and `opinions` (operator.add) enforced. |
| VII. Explicit Error Handling Contracts         | ✅     | Fatal errors return partial results; `ErrorHandler` routing.       |
| XIII. Hierarchical StateGraph Only             | ✅     | Single `StateGraph` in `src/graph.py`.                             |
| XIV. Parallel Fan-Out / Fan-In Required        | ✅     | Distinct fan-out for detectives and judges.                        |
| XV. Tool Execution Isolated                    | ✅     | Subprocess calls in `src/tools/` are sandboxed with timeouts.      |
| XXII. Structured Logging Mandatory             | ✅     | `StructuredLogger` tracks node entries, exits, and verdicts.       |
| XXVI. Integration Tests Required               | ✅     | Full judicial workflow test (E2E) to be implemented.               |

## Project Structure

### Documentation (this feature)

```text
specs/011-e2e-langgraph-wiring/
├── plan.md              # This file
├── research.md          # Implementation decisions and best practices
├── data-model.md        # State schema and entity relationships
├── quickstart.md        # Feature bootstrap guide
├── contracts/           # CLI command schema and report format
└── tasks.md             # Generated tasks for execution
```

### Source Code (repository root)

```text
src/
├── nodes/               # Layer-specific node logic
│   ├── context_builder.py
│   ├── detectives.py
│   ├── aggregator.py
│   ├── judges.py
│   ├── justice.py
│   └── report_generator.py
├── tools/               # Sandboxed forensic tools
│   ├── repo_tools.py
│   ├── doc_tools.py
│   └── vision_tools.py
├── state.py             # AgentState and Pydantic schemas
└── graph.py             # LangGraph orchestrator definition

tests/
├── integration/         # Full workflow testing
│   └── test_full_workflow.py
└── unit/                # Individual node and wiring tests
    └── test_graph_wiring.py
```

**Structure Decision**: Option 1: Single project. All nodes and tools are core to the system's identity.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| N/A       |            |                                      |
