# Data Model: Report & Manifest

This document outlines the data structures used by the `ReportGenerator` to produce the final audit artifacts.

## Entities

### AuditReport (Input/Intermediate)

The primary data object produced by Layer 3 (`ChiefJustice`) and consumed by Layer 4 (`ReportGenerator`).

| Field               | Type                    | Description                             |
| ------------------- | ----------------------- | --------------------------------------- |
| `repo_url`          | `str`                   | URL of the audited repository.          |
| `executive_summary` | `str`                   | High-level synthesis of findings.       |
| `overall_score`     | `float`                 | Weighted average score [1.0, 5.0].      |
| `criteria`          | `List[CriterionResult]` | List of results per rubric dimension.   |
| `remediation_plan`  | `str`                   | Aggregated file-level fix instructions. |

### CriterionResult

Detailed result for a single rubric dimension.

| Field             | Type                    | Description                                            |
| ----------------- | ----------------------- | ------------------------------------------------------ |
| `dimension_id`    | `str`                   | Unique ID from rubric (e.g., `git_forensic_analysis`). |
| `dimension_name`  | `str`                   | Human-readable name.                                   |
| `final_score`     | `int`                   | Synthesized score [1, 5].                              |
| `judge_opinions`  | `List[JudicialOpinion]` | The 3 personas' raw thoughts.                          |
| `dissent_summary` | `Optional[str]`         | Explanation of conflict (if variance > 2).             |
| `remediation`     | `str`                   | Specific fix for this dimension.                       |

### Evidence (Forensic Artifact)

Immutable fact item used for citations.

| Field         | Type                                | Description                             |
| ------------- | ----------------------------------- | --------------------------------------- |
| `evidence_id` | `str`                               | `{source}_{class}_{index}`              |
| `source`      | `Literal["repo", "docs", "vision"]` | Source detective.                       |
| `location`    | `str`                               | File path, commit hash, or page number. |
| `rationale`   | `str`                               | Why this evidence was captured.         |
| `content`     | `Optional[str]`                     | Code snippet or text extract.           |

## Relationships

1. **Many-to-One**: Multiple `JudicialOpinion` objects reference a single `Evidence` object via `evidence_id`.
2. **One-to-Many**: `AuditReport` contains a list of `CriterionResult`.
3. **One-to-Many**: `CriterionResult` contains a list of `JudicialOpinion`.

## Validation Rules

- **ID Integrity**: Every `cited_evidence` ID in an opinion MUST exist in the `evidences` collection.
- **Score Bounds**: All scores must be within [1, 5].
- **Dissent Requirement**: If `max(scores) - min(scores) > 2`, `dissent_summary` MUST NOT be null.
