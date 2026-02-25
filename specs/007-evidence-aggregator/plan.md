# Implementation Plan: Evidence Aggregation Sync Node (Layer 1.5)

**Branch**: `007-evidence-aggregator` | **Date**: 2026-02-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-evidence-aggregator/spec.md`

## Summary

The `EvidenceAggregator` acts as the mandatory fan-in synchronization point between the parallel Detective Layer (Layer 1) and the parallel Judicial Layer (Layer 2). Its primary technical responsibilities are consolidating evidence from multiple sources (`repo`, `docs`, `vision`), deduplicating findings via `evidence_id`, and performing cross-reference validation to detect documentation hallucinations (claimed file paths that do not exist in the repository).

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: LangGraph, Pydantic, `operator.ior` reducer
**Storage**: LangGraph `AgentState` (In-memory dict-based state)
**Testing**: pytest (Unit tests for logic, Integration for graph wiring)
**Target Platform**: Any system with Python 3.12+ and `uv`
**Project Type**: LangGraph Internal Synchronization Node
**Performance Goals**: <50ms overhead for aggregation logic (SC-002)
**Constraints**:

- MUST enforce path sanitization (C-XV, FR-008)
- MUST fail if critical sources (`repo`, `docs`) are missing (Clarification Q1)
- MUST use `operator.ior` for memory-safe merging (C-VI)
  **Scale/Scope**: Handles O(100s) of evidence items and file paths per run.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| ID     | Principle                  | Compliance Status | Rationale                                                   |
| ------ | -------------------------- | ----------------- | ----------------------------------------------------------- |
| III.1  | Typed State                | YES               | Uses `AgentState` with Pydantic `Evidence` models.          |
| VI.1   | Parallel-Safe Reducers     | YES               | Explicitly uses `operator.ior` for `evidences` field.       |
| VIII.3 | Evidence Precedes Judgment | YES               | This node is the mandatory gate before judicial nodes fire. |
| XII.2  | Hallucination Flagging     | YES               | Implements "Hallucinated Path" detection for doc claims.    |
| XIV.3  | Fan-In Sync                | YES               | Serves as the synchronization point for Layer 1.            |
| XV.5   | Static Analysis Only       | YES               | Only checks existence of paths/content; never executes.     |
| XVI.1  | Immutable Evidence         | YES               | Consolidates but does not modify existing evidence content. |
| XX.1   | Modular Architecture       | YES               | Located in `src/nodes/evidence_aggregator.py`.              |

## Project Structure

### Documentation (this feature)

```text
specs/007-evidence-aggregator/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Research on path sanitization & deduplication logic
├── data-model.md        # State structure & cross-reference evidence schema
└── quickstart.md        # How to test the aggregator in isolation
```

### Source Code

```text
src/
├── nodes/
│   └── evidence_aggregator.py  # The fan-in node implementation
└── state.py                    # Ensures AgentState supports this node's requirements

tests/
├── unit/
│   └── test_evidence_aggregator.py # Logic tests for merging & cross-referencing
└── integration/
    └── test_graph_sync.py          # Verifies fan-in behavior in the StateGraph
```

**Structure Decision**: Standard single-project structure with specialized node and test files to maintain modularity.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

_No violations detected._
