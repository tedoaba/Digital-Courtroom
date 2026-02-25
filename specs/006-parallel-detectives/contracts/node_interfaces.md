# Node Interface Contracts: Layer 1 Detectives

## Overview

All Layer 1 nodes are pure Python functions designed to be used as `nodes` in a LangGraph `StateGraph`. They must accept the `AgentState` as input and return a partial state update.

## Detective Node Contract

### Shared Interface

Each detective function must follow this signature:
`def detective_node(state: AgentState) -> Dict[str, Any]`

### RepoInvestigator

- **Input Dependencies**: `state["repo_url"]`, `state["rubric_dimensions"]`.
- **Output Key**: `evidences` (merges `{"repo": List[Evidence]}`).
- **Success Criteria**: Returns evidence for AST, Git Log, and Tool Safety.

### DocAnalyst

- **Input Dependencies**: `state["pdf_path"]`, `state["rubric_dimensions"]`.
- **Output Key**: `evidences` (merges `{"docs": List[Evidence]}`).
- **Success Criteria**: Returns evidence for theoretical depth and claimed path verification.

### VisionInspector

- **Input Dependencies**: `state["pdf_path"]`, `state["rubric_dimensions"]`.
- **Output Key**: `evidences` (merges `{"vision": List[Evidence]}`).
- **Success Criteria**: Returns evidence for diagram classification.

## Error Handling Contract

- **Class**: Catch `Exception`.
- **Action**:
  1. Log error with `StructuredLogger`.
  2. Add error string to `state["errors"]`.
  3. Return `{"evidences": {<source>: [Evidence(found=False, ...)]}}`.
