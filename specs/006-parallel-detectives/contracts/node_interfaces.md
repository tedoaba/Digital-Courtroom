# Node Interface Contracts: Layer 1 Detectives

## Overview

All Layer 1 nodes are pure Python functions designed to be used as `nodes` in a LangGraph `StateGraph`. They must accept the `AgentState` as input and return a partial state update.

## Detective Node Contract

### Shared Interface

Each detective function must follow this signature:
`def detective_node(state: AgentState) -> Dict[str, Any]`

**Return Requirement**: To trigger the `merge_evidences` reducer in `AgentState`, nodes MUST return a dictionary in the following format:
`{"evidences": {<source_key>: List[Evidence]}}`

### RepoInvestigator

- **Input Dependencies**: `state["repo_url"]`, `state["rubric_dimensions"]`.
- **Output Key**: `evidences` (merges `{"repo": List[Evidence]}`).
- **Success Criteria**: Returns evidence for AST (structure), Git Log (history), and Tool Safety (lack of `os.system`, shell injection risks).

### DocAnalyst

- **Input Dependencies**: `state["pdf_path"]`, `state["rubric_dimensions"]`.
- **Output Key**: `evidences` (merges `{"docs": List[Evidence]}`).
- **Success Criteria**: Returns evidence for document claims and cited path verification.

### VisionInspector

- **Input Dependencies**: `state["pdf_path"]`, `state["rubric_dimensions"]`.
- **Output Key**: `evidences` (merges `{"vision": List[Evidence]}`).
- **Success Criteria**: Returns evidence for diagram classification (e.g., "Parallel Flow").

## Error Handling Contract

- **Class**: Catch `Exception`.
- **Action**:
  1. Log error with `StructuredLogger`.
  2. Add error string to `state["errors"]`.
  3. Return `{"evidences": {<source>: [Evidence(found=False, ...)]}}`.
