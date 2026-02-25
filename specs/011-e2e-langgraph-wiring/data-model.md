# Data Model: E2E LangGraph Orchestration & Edge Wiring

## Root State

### AgentState (TypedDict)

The central state object flowing through the LangGraph.

| Field               | Type                        | Reducer        | Description                   |
| ------------------- | --------------------------- | -------------- | ----------------------------- |
| `repo_url`          | `str`                       | N/A            | Target Git URL                |
| `pdf_path`          | `str`                       | N/A            | Target Specification PDF path |
| `rubric_dimensions` | `List[Dict]`                | N/A            | Loaded from `rubric.json`     |
| `evidences`         | `Dict[str, List[Evidence]]` | `operator.ior` | Merged detective evidence     |
| `opinions`          | `List[JudicialOpinion]`     | `operator.add` | Appended judge opinions       |
| `final_report`      | `AuditReport`               | N/A            | Final synthesis output        |
| `re_eval_needed`    | `bool`                      | N/A            | Toggle for high-variance loop |
| `errors`            | `List[str]`                 | `operator.add` | Global error log              |
| `metadata`          | `Dict[str, Any]`            | `operator.ior` | Run manifest data             |

## Core Entities

### Evidence (BaseModel)

Forensic artifact captured by Layer 1.

- `id`: `source_class_index`
- `found`: `bool`
- `content`: `Optional[str]`
- `rationale`: `str`
- `confidence`: `float` (0.0 - 1.0)

### JudicialOpinion (BaseModel)

Opinion rendered by Layer 2.

- `judge`: `Prosecutor | Defense | TechLead`
- `score`: `int` (1 - 5)
- `argument`: `str`
- `cited_evidence`: `List[str]` (evidence IDs)

### AuditReport (BaseModel)

Serialized as Markdown for final deliverable.

- `overall_score`: `float`
- `executive_summary`: `str`
- `criteria_results`: `List[CriterionResult]`
- `remediation_plan`: `str`

## State Transitions

1. **START** -> `ContextBuilder` (Populates `rubric_dimensions`)
2. `ContextBuilder` -> `[RepoInvestigator, DocAnalyst, VisionInspector]` (Fan-Out)
3. `[Extractors]` -> `EvidenceAggregator` (Fan-In Sync)
4. `EvidenceAggregator` -> `[Prosecutor, Defense, TechLead]` (Fan-Out)
5. `[Judges]` -> `ChiefJustice` (Fan-In Sync)
6. `ChiefJustice` -> **LOOP CHECK**:
   - If variance > 2 AND re_eval_count < 1: `[Judges]`
   - Else: `ReportGenerator`
7. `ReportGenerator` -> **END**

## Error Transitions

- Any node failure -> `ErrorHandler` -> `ReportGenerator` (Partial Report)
