# Feature Specification: E2E LangGraph Orchestration & Edge Wiring

**Feature Branch**: `011-e2e-langgraph-wiring`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "E2E LangGraph Orchestration & Edge Wiring"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Full Audit Pipeline Execution (Priority: P1)

As an auditor, I want to run a single command that orchestrates the entire swarm (ContextBuilder -> Detectives -> Aggregator -> Judges -> Justice -> Report) so that I can receive a complete Audit Report for a submitted repository and PDF specification.

**Why this priority**: This is the core functionality that integrates all previous work into a functioning system. Without E2E wiring, the individual nodes remain disconnected components.

**Independent Test**: Can be fully tested by invoking the system via `uv` with a valid repo URL and PDF path, and verifying that a `Report.md` file is generated containing all required sections.

**Acceptance Scenarios**:

1. **Given** a valid GitHub URL and a local path to a PDF report, **When** the orchestrator is executed, **Then** all detective and judge nodes are invoked in their respective parallel blocks.
2. **Given** the successful completion of all nodes, **When** the pipeline reaches the final stage, **Then** a structured Markdown file is generated following the Executive Summary -> Criterion Breakdown -> Remediation Plan format.

---

### User Story 2 - Fault-Tolerant Forensic Routing (Priority: P2)

As a system, I want to handle failures in individual detective or judge nodes gracefully by routing through an ErrorHandler so that the audit doesn't crash and still yields a partial/degraded report where possible.

**Why this priority**: Critical for production robustness. Forensic tools or LLMs may fail due to network or parsing issues; the system must not be a "all or nothing" pipeline.

**Independent Test**: Mock a failure in one detective node (e.g., `VisionInspector`) and verify that the graph continues to `EvidenceAggregator` and eventually produces a report with a disclaimer about missing vision evidence.

**Acceptance Scenarios**:

1. **Given** a catastrophic failure in the `ContextBuilder` (e.g., invalid URL), **When** the graph executes, **Then** it must shortcut directly to a failure logging node/report generator that notes the input error.
2. **Given** a failure in a non-critical detective agent, **When** the fan-out synchronization occurs, **Then** the system must log the warning and proceed with the remaining evidence.

---

### User Story 3 - Deterministic Parallel Synchronization (Priority: P3)

As a developer, I want to ensure that the graph's fan-in/fan-out behavior is deterministic and respects the `run_manifest.json` configuration so that I can verify the architecture matches the design specification.

**Why this priority**: Ensures that the implementation matches the architectural diagrams and that parallelism is actually happening as designed.

**Independent Test**: Use a diagnostic run or trace (e.g., LangSmith) to verify that all 3 detectives start simultaneously and wait for the Aggregator before judges begin.

**Acceptance Scenarios**:

1. **Given** the graph definition, **When** inspected via topology analysis, **Then** the edges must strictly follow the `ContextBuilder -> [Extractors] -> Aggregator` pattern.
2. **Given** a `run_manifest.json` defining the execution rules, **When** the graph runs, **Then** the internal routing logic must apply the specific Constitution restrictions (e.g., Security Overrides) defined therein.

---

### Edge Cases

- **Empty Repository**: Repository is cloned successfully but contains zero code files. System should report "No Code Evidence Found" gracefully.
- **Malformed PDF**: PDF is corrupt. `DocAnalyst` should return a "found=False" evidence item rather than crashing the whole graph.
- **Judge Disagreement**: Judges return wildly different scores (variance > 2). `ChiefJustice` must recognize this and generate a "Dissent Summary" as per the Constitution.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST implement a state-driven orchestrator that manages the transition between analysis and evaluation phases.
- **FR-002**: System MUST support parallel execution of forensic investigation agents (investigating code, documents, and visual artifacts).
- **FR-003**: System MUST include a synchronization mechanism to aggregate forensic findings before initiating the judicial phase.
- **FR-004**: System MUST support parallel execution of multiple distinct judicial personas evaluating the same evidence.
- **FR-005**: System MUST implement a deterministic synthesis process that resolves judicial conflicts according to predefined rules (the project "Constitution").
- **FR-006**: System MUST implement a global error management system that prevents process hangs and ensures report generation even after non-fatal failures.
- **FR-007**: System MUST provide a unified command-line interface for initiating audits and specifying input artifacts.
- **FR-008**: System MUST enforce synchronization at layer boundaries to ensure all parallel sub-tasks complete before dependent tasks begin.
- **FR-009**: System MUST output a finalized audit report in a human-readable structured document format.

### Key Entities _(include if feature involves data)_

- **StateGraph**: The central orchestrator object defining nodes, edges, and state transitions.
- **AgentState**: The typed schema (Pydantic/TypedDict) that flows between nodes, used by reducers to merge parallel outputs.
- **Edge Wiring**: The configuration of logical connections (`add_edge`, `add_conditional_edges`) that define the system's "wiring."

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Successfully complete a full audit run (ContextBuilder to Report) in under 5 minutes for a standard repository (<100 files).
- **SC-002**: 100% of graph runs against valid inputs must produce an `AuditReport` Markdown file.
- **SC-003**: Topographical tests confirm that exactly 3 nodes are branched during the Detective phase and exactly 3 during the Judicial phase.
- **SC-004**: System recovers from single-node timeouts by continuing with partial state after a logged retry failure.
- **SC-005**: Final report strictly respects "Constitution" override rules (e.g., Security flaws override Defense scores) with 100% deterministic accuracy.
