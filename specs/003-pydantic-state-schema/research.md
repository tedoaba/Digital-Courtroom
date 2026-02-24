# Research: LangGraph Custom Reducers and Pydantic Validation

## Decision: Custom Reducer Implementation for Evidence and Criterion Results

### Rationale:

LangGraph's default `operator.add` just appends lists, which can lead to duplicate `Evidence` items in parallel branches. Our spec requires deduplication based on `source_ref` and `content`. Similarly, for `CriterionResult`, we need to resolve collisions using `relevance_confidence` rather than just "last writer wins".

### Findings:

#### 1. Evidence List Reducer (Deduplicating)

A custom reducer in LangGraph is just a function that takes `(existing, new)` and returns the updated state.

```python
def merge_evidence(left: list[Evidence], right: list[Evidence]) -> list[Evidence]:
    if not isinstance(left, list) or not isinstance(right, list):
        raise TypeError("merge_evidence expects lists for left and right operands")

    # Use a dictionary to deduplicate by (source_ref, content_hash)
    merged = { (e.source_ref, hash(e.content)): e for e in left }
    for e in right:
        merged[(e.source_ref, hash(e.content))] = e
    return list(merged.values())
```

_Correction_: Pydantic models are not hashable by default unless `frozen=True`. Since we want immutability (Constitution XVI), we should use `frozen=True`.
_Fatal Exception_: Added a type check to raise `TypeError` if non-list data is passed, per Session 2026-02-24.

#### 2. Criterion Result Reducer (Confidence-based)

```python
def merge_criterion_results(left: dict[str, CriterionResult], right: dict[str, CriterionResult]) -> dict[str, CriterionResult]:
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise TypeError("merge_criterion_results expects dicts for left and right operands")

    merged = left.copy()
    for k, v in right.items():
        if k not in merged or v.relevance_confidence > merged[k].relevance_confidence:
            merged[k] = v
    return merged
```

## Decision: Strict Pydantic Validation

### Rationale:

To ensure the highest data integrity, we will configure all models to forbid extra fields and enforce strict type checking (no coercion). This prevents LLMs from passing "blind" data or incorrect types.

### Implementation Pattern:

```python
class StrictModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra='forbid',
        strict=True
    )

class CriterionResult(StrictModel):
    criterion_id: str
    numeric_score: int = Field(ge=1, le=5)
    reasoning: str
    relevance_confidence: float = Field(ge=0, le=1)
    security_violation_found: bool = False
```

## Decision: Weighted Audit Score

### Rationale:

Per Constitution XI, the `global_score` must follow a precedence hierarchy.

1. **Security Override**: If any `CriterionResult.security_violation_found` is `True`, the score for that criterion is capped at 3.
2. **Fact Supremacy**: Facts overrule opinions.
3. **Weights**: Architecture criteria are weighted higher by the Tech Lead lens.

### Calculation Strategy:

The `AuditReport` generator will apply these rules before averaging.

- `capped_score = min(result.numeric_score, 3) if result.security_violation_found else result.numeric_score`
- Final score = `round(sum(capped_scores * weights) / sum(weights), 1)`
