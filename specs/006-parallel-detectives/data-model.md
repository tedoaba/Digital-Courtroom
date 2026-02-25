# Data Model: Parallel Detective Agents (Layer 1)

## Entities

### Evidence

Immutable forensic evidence collected by detective agents.

| Field            | Type                                | Validation                         | Description                                                |
| ---------------- | ----------------------------------- | ---------------------------------- | ---------------------------------------------------------- |
| `evidence_id`    | `str`                               | Format: `{source}_{class}_{index}` | Unique identifier for traceability.                        |
| `source`         | `Literal["repo", "docs", "vision"]` | Required                           | The detective that produced this.                          |
| `evidence_class` | `str`                               | Required                           | Type of forensic analysis performed.                       |
| `goal`           | `str`                               | Required                           | What the detective was searching for.                      |
| `found`          | `bool`                              | Required                           | Whether the target artifact exists.                        |
| `content`        | `Optional[str]`                     | N/A                                | Extracted code/text snippet or classification description. |
| `location`       | `str`                               | Required                           | File path, commit hash, or PDF page number.                |
| `rationale`      | `str`                               | Required                           | Confidence justification.                                  |
| `confidence`     | `float`                             | `0.0 <= v <= 1.0`                  | Probability of the finding being accurate.                 |
| `timestamp`      | `datetime`                          | Default: `now`                     | When the evidence was captured.                            |

### AgentState (Relevant Slice)

TypedDict state shared across the LangGraph.

| Field           | Type                        | Reducer        | Description                               |
| --------------- | --------------------------- | -------------- | ----------------------------------------- |
| `evidences`     | `Dict[str, List[Evidence]]` | `operator.ior` | Merges outputs from parallel detectives.  |
| `errors`        | `List[str]`                 | `operator.add` | Appends error messages from failed nodes. |
| `execution_log` | `List[str]`                 | `operator.add` | Appends audit trail entries.              |

## State Transitions

### Layer 1 Flow

1. **Input**: `repo_url`, `pdf_path`, `rubric_dimensions`.
2. **Execution**: Detectives execute in parallel.
3. **Output**: Each detective returns a dictionary to be merged into `AgentState.evidences`.
   - `RepoInvestigator` -> `{"repo": List[Evidence]}`
   - `DocAnalyst` -> `{"docs": List[Evidence]}`
   - `VisionInspector` -> `{"vision": List[Evidence]}`
