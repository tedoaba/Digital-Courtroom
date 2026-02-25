# Data Model: Chief Justice Synthesis

## Entity: CriterionResult (Enhanced)

**Description**: The final verdict for a specific rubric dimension, synthesized from multiple judicial opinions.
**Source**: Inherits from `StrictModel` in `src/state.py`.

| Field                      | Type                    | Description                               | Validation                  |
| -------------------------- | ----------------------- | ----------------------------------------- | --------------------------- |
| `criterion_id`             | `str`                   | Maps to rubric dimension ID               | Required                    |
| `numeric_score`            | `int`                   | Final synthesized score                   | 1-5                         |
| `reasoning`                | `str`                   | Consolidated reasoning or anchor argument | Min 50 chars                |
| `judge_opinions`           | `list[JudicialOpinion]` | The 3 opinions used for synthesis         | Exactly 3 (unless fallback) |
| `dissent_summary`          | `Optional[str]`         | Summary of conflict if variance > 2       | Required if variance > 2    |
| `remediation`              | `Optional[str]`         | Aggregated technical fix instructions     | Required for score < 5      |
| `applied_rules`            | `list[str]`             | Rules triggered (e.g., SECURITY_OVERRIDE) | Required                    |
| `execution_log`            | `list[str]`             | Narrative trace of calculation steps      | Required                    |
| `security_violation_found` | `bool`                  | Flag for global score override            | Default: False              |
| `re_evaluation_required`   | `bool`                  | Triggered if variance > 2                 | Default: False              |

## Entity: AuditReport (Final)

**Description**: The complete audit result delivered to the user.

| Field          | Type                         | Description                          | Validation             |
| -------------- | ---------------------------- | ------------------------------------ | ---------------------- |
| `results`      | `dict[str, CriterionResult]` | Map of dimension ID to result        | All dimensions present |
| `summary`      | `str`                        | Executive summary of the whole audit | Min 100 chars          |
| `global_score` | `float`                      | Weighted average score               | 1.0 - 5.0 (1 decimal)  |

## State Transitions

1. **Input**: `AgentState` containing `opinions` (list of all judge outputs) and `evidences`.
2. **Process**:
   - `ChiefJusticeNode` groups `opinions` by `criterion_id`.
   - Checks for missing judges (max 3 expected per criterion).
   - Calculates variance and applies deterministic rules.
   - Computes weighted score with "Round Half Up" logic.
3. **Output**: `AgentState` updated with `criterion_results` and `final_report`.

## Uniqueness & Constraints

- `criterion_id` must be unique within the `results` dictionary.
- `Numeric score` must be 1-5 integer, strictly capped at 3 if `applied_rules` contains `SECURITY_OVERRIDE`.
