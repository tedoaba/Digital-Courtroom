# Data Model: Digital Courtroom State

This document defines the Pydantic models and the LangGraph `AgentState` for the Digital Courtroom.

## Configuration Standards

All models MUST adhere to the following configuration for strictness:

- **`frozen=True`**: Standard immutability for processed evidence and results.
- **`extra='forbid'`**: No non-defined fields allowed.
- **`strict=True`**: No type coercion (e.g., `"5"` will not be coerced to `5`).

## Entities

### `Evidence`

Represents a factual claim extracted from a source.

- **`source_ref`** (`str`): Reference to the page, paragraph, or URL.
- **`content`** (`str`): The extracted text or logic.
- **`relevance_confidence`** (`float`): Pydantic constrained [0.0, 1.0].

### `JudicialOpinion`

A judge's evaluation of a specific set of evidence.

- **`case_id`** (`str`): Default "Unknown".
- **`court_name`** (`str`): Default "Unknown".
- **`text`** (`str`): The narrative opinion.
- **`metadata`** (`dict`): Flexible metadata storage.

### `CriterionResult`

The outcome for a single rubric criterion.

- **`criterion_id`** (`str`): The identifier from the rubric.
- **`numeric_score`** (`int`): Pydantic constrained [1, 5].
- **`reasoning`** (`str`): Explanation for the score.
- **`relevance_confidence`** (`float`): Confidence in the judgment [0.0, 1.0].
- **`security_violation_found`** (`bool`): Flag indicating constitutional score capping at 3.

### `AuditReport`

The final aggregated output.

- **`results`** (`dict[str, CriterionResult]`): Map of ID to result.
- **`summary`** (`str`): High-level analysis.
- **`global_score`** (`float`): Weighted average based on **Constitution XI**, rounded to 1 decimal place.

## Agent State (`TypedDict`)

| Field               | Type                         | Reducer                   | Description                                            |
| ------------------- | ---------------------------- | ------------------------- | ------------------------------------------------------ |
| `evidence`          | `list[Evidence]`             | `merge_evidence`          | Deduplicated list; Fatal on structural mismatch.       |
| `judicial_opinions` | `list[JudicialOpinion]`      | `operator.add`            | Collection of judge outputs.                           |
| `results`           | `dict[str, CriterionResult]` | `merge_criterion_results` | Best confidence results; Fatal on structural mismatch. |
| `errors`            | `list[str]`                  | `operator.add`            | Traceable execution errors.                            |
| `opinion_text`      | `str`                        | _None_                    | The raw source text of the opinion.                    |
