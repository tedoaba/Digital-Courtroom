# Data Model: Evidence Aggregation

## Entities

### AgentState (Relevant fields)

The `AgentState` is the primary container for evidence data during graph execution.

- `evidences`: `Annotated[dict[str, list[Evidence]], merge_evidences]`.
  - Keys: `repo`, `docs`, `vision`.
  - Values: Lists of validated `Evidence` objects.
  - Reducer: `merge_evidences` ensures that if multiple detectives write to the same source key (unlikely in normal fan-out but possible in retries), duplicate `evidence_id`s are filtered out.

### Evidence (Cross-Reference Findings)

### Clean Evidence Dictionary (Judge Node Input)

The output of `EvidenceAggregator` is the transformed `AgentState.evidences` dict, guaranteed to meet these criteria:

```json
{
  "repo": [
    { "evidence_id": "repo_FILE_X", "found": true, "location": "src/main.py", ... }
  ],
  "docs": [
    {
      "evidence_id": "docs_DOCUMENT_CLAIM_abc123",
      "evidence_class": "DOCUMENT_CLAIM",
      "found": false,
      "location": "non_existent.py",
      "rationale": "Path cited in documentation does not exist in the repository manifest."
    }
  ],
  "vision": [ ... ]
}
```

## Validation Rules

1. **Path Sanitization**:
   - Rule 1: `path.is_absolute()` -> REJECT.
   - Rule 2: `path.resolve()` must start with `repo_root` -> REJECT IF ESCAPES.
   - Rule 3: `path.normalize()` to POSIX (forward slashes).
2. **Mandatory Keys**: The aggregator MUST check for the presence of `repo` and `docs` keys in the `evidences` dict.
3. **Deduplication**: `evidence_id` MUST be unique across all sources. If a collision occurs (e.g., from two different list items in `docs`), the FIRST entry is preserved.
4. **Hallucination ID**: `docs_DOCUMENT_CLAIM_{sha256(path)[:8]}`.

## Lifecycle Transitions

1. **Raw Evidence Collection**: Detectives create `Evidence` objects in parallel.
2. **State Merge (LangGraph Automatic)**: The `merge_evidences` reducer runs as the detectives return their results to the graph, merging the top-level keys.
3. **Aggregation & Verification**:
   - The `EvidenceAggregator` node reads the merged `evidences` dict.
   - It iterates through `docs` evidence.
   - For each path in `docs`, it checks if it exists in the `repo` file manifest (collected from `repo` evidence objects).
   - It appends NEW `Evidence` objects (hallucination flags) back to the `evidences["docs"]` list if missing.
   - It logs a `PROJECT_LIFECYCLE` event.
4. **Finalized Evidence**: The state is now ready for judges. Metadata `pipeline_integrity` is updated to `SUCCESS` or `FAILED`.
