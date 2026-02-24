# Research: LangGraph Custom Reducers and Pydantic Validation

## Decision: Custom Reducer Implementation for Evidence and Criterion Results

### Rationale:

LangGraph's default `operator.add` just appends lists, which can lead to duplicate `Evidence` items in parallel branches. Our spec requires deduplication based on `source_ref` and `content`. Similarly, for `CriterionResult`, we need to resolve collisions using `relevance_confidence` rather than just "last writer wins".

### Findings:

#### 1. Evidence List Reducer (Deduplicating)

A custom reducer in LangGraph is just a function that takes `(existing, new)` and returns the updated state.

```python
def merge_evidence(left: list[Evidence], right: list[Evidence]) -> list[Evidence]:
    # Use a dictionary to deduplicate by (source_ref, content_hash)
    merged = { (e.source_ref, hash(e.content)): e for e in left }
    for e in right:
        merged[(e.source_ref, hash(e.content))] = e
    return list(merged.values())
```

_Correction_: Pydantic models are not hashable by default unless `frozen=True`. Since we want immutability (Constitution XVI), we should use `frozen=True`.

#### 2. Criterion Result Reducer (Confidence-based)

```python
def merge_criterion_results(left: dict[str, CriterionResult], right: dict[str, CriterionResult]) -> dict[str, CriterionResult]:
    merged = left.copy()
    for k, v in right.items():
        if k not in merged or v.relevance_confidence > merged[k].relevance_confidence:
            merged[k] = v
    return merged
```

### Alternatives Considered:

- **Default `operator.add`**: Rejected because it creates duplicates, violating the clean audit requirement.
- **Pydantic `RootModel`**: Considered for wrapping lists, but `Annotated` in `TypedDict` is the standard LangGraph pattern.

## Decision: Pydantic Validation Constraints

### Rationale:

Using Pydantic `Field(ge=..., le=...)` ensures that LLM hallucinations outside valid ranges are caught early at the state boundary.

### Implementation Pattern:

```python
class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_ref: str
    content: str
    relevance_confidence: float = Field(ge=0.0, le=1.0)
```
