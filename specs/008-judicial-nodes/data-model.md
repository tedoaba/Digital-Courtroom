# Data Model: Dialectical Judicial Agents (Layer 2)

## Entities

### JudicialOpinion (Pydantic BaseModel)

Represents the structured verdict from a single judge for a single criterion.

| Field            | Type                                           | Constraint        | Description                                                |
| ---------------- | ---------------------------------------------- | ----------------- | ---------------------------------------------------------- |
| `opinion_id`     | `str`                                          | Mandatory         | Unique ID: `{judge}_{criterion_id}_{timestamp}`            |
| `judge`          | `Literal["Prosecutor", "Defense", "TechLead"]` | Mandatory         | The persona that generated this opinion.                   |
| `criterion_id`   | `str`                                          | Mandatory         | Reference to the rubric dimension ID.                      |
| `score`          | `int`                                          | `1 <= score <= 5` | Judicial score assigned.                                   |
| `argument`       | `str`                                          | `min_length=20`   | Detailed reasoning justifying the score.                   |
| `cited_evidence` | `List[str]`                                    | Mandatory         | List of `evidence_id` values from Layer 1.                 |
| `mitigations`    | `Optional[List[str]]`                          | Optional          | Defense-specific: factors that excuse poor implementation. |
| `charges`        | `Optional[List[str]]`                          | Optional          | Prosecutor-specific: formal allegations of negligence.     |
| `remediation`    | `Optional[str]`                                | Optional          | TechLead-specific: actionable technical fix.               |

### JudicialTask (TypedDict)

Internal state wrapper used for the LangGraph `Send` pattern to distribute work.

| Field       | Type                                           | Description                                  |
| ----------- | ---------------------------------------------- | -------------------------------------------- |
| `persona`   | `Literal["Prosecutor", "Defense", "TechLead"]` | The judge type for this task.                |
| `criterion` | `Dict[str, Any]`                               | The specific rubric dimension to evaluate.   |
| `evidences` | `List[Evidence]`                               | Filtered evidence relevant to the criterion. |

## State Transitions

### Layer 1.5 -> Layer 2 (Fan-Out)

- **Node**: `EvidenceAggregator` (or dispatcher)
- **Action**: Iterates over `AgentState["rubric_dimensions"]` and generates 3 `Send("evaluate_criterion", JudicialTask)` objects per dimension.

### Layer 2 Execution

- **Node**: `evaluate_criterion`
- **Result**: Appends a `JudicialOpinion` to the global `opinions` list via `operator.add`.

### State Management Constraints

- `opinions`: `Annotated[List[JudicialOpinion], operator.add]` (Parallel-safe list append).
- Identical `Evidence` is provided to all three personas for the same criterion to ensure "fair trial" conditions.
