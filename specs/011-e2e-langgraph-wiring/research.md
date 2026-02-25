# Research: E2E LangGraph Orchestration & Edge Wiring

## Technical Decisions

### Decision 1: Parallel Fan-Out/Fan-In Implementation

**Decision**: Use the `StateGraph.add_node` with multiple edges pointing to the same synchronization node to achieve fan-in.
**Rationale**: In LangGraph, if multiple nodes have edges pointing to a single node, that target node acts as a synchronization point. It only executes after all incoming branches have completed correctly. This aligns with the "Strict Layer Synchronization" requirement.
**Alternatives considered**:

- `parallel` utility (less control over specific node behavior).
- Manual threading (violates the LangGraph architectural constraint).

### Decision 2: Error Handling and Fallback Routing

**Decision**: Implement a global `ErrorHandler` node and use `add_conditional_edges` from every node (or layer boundaries) to route to it.
**Rationale**: To ensure the "partial report" requirement, any catastrophic failure must capture the current state and jump to a finalization phase. Using conditional edges based on whether `state["errors"]` is populated or a node returns an `ErrorEvidence` object allows deterministic fallback.
**Alternatives considered**:

- Local try/except within each node (less centralized, harder to generate global partial reports).
- LangGraph built-in retry (handles transient errors, but doesn't solve the "partial report" routing logic).

### Decision 3: Deterministic Re-evaluation Loop

**Decision**: `ChiefJustice` returns a routing signal in the state. `add_conditional_edges` from `ChiefJustice` routes either to `END` (or `ReportGenerator`) or back to `JudicialLayer` entry.
**Rationale**: This preserves the directed graph structure while allowing a controlled cycle. The state must track the "re_evaluation_count" to prevent infinite loops (max 1 retry per Architecture Notes).
**Alternatives considered**:

- Linearizing the re-evaluation (adding a `ReEvalJudge` node) - Rejected because it duplicates node logic.
- Recursive function calls - Rejected as it bypasses the `StateGraph`.

### Decision 4: Layer-level Timeouts

**Decision**: Wrap parallel blocks or specific heavy nodes in a custom timeout handler that emits a `found=False` evidence on timeout.
**Rationale**: Ensures the 300s layer-level deadline. LangGraph doesn't have a native "layer timeout", so this must be enforced at the orchestration layer or via a wrapper around the node functions.
**Alternatives considered**:

- `asyncio.wait_for` (requires transition to async graph; the current project is largely synchronous).
- OS signals (unreliable for fine-grained LLM call control).

## Technology Best Practices

### LangGraph (Multi-Agent Swarms)

- Always use `Annotated` with reducers for parallel state.
- Keep nodes "atomic" and side-effect free (except for state updates).
- Trace all executions with LangSmith for metrical verification of SC-003 (Parallelism).

### Deterministic Synthesis (Rule Engine)

- Use pure Python functions for synthesis.
- Strictly follow the Priority Hierarchy: Security > Fact > Functionality.
- Logging must include _why_ a rule was applied (applied_rules list in the diagnostic trace).
