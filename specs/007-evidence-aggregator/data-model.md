# Data Model: Evidence Aggregation

## Entities

### AgentState (Relevant fields)

The `AgentState` is the primary container for evidence data during graph execution.

- `evidences`: `Annotated[dict[str, list[Evidence]], merge_evidences]`.
  - Keys: `repo`, `docs`, `vision`.
  - Values: Lists of validated `Evidence` objects.
  - Reducer: `merge_evidences` ensures that if multiple detectives write to the same source key (unlikely in normal fan-out but possible in retries), duplicate `evidence_id`s are filtered out.

### Evidence (Cross-Reference Findings)

Created by the `EvidenceAggregator` when a mismatch is found.

- `evidence_id`: `aggregator_REPORT_ACCURACY_{digest}`
- `source`: `docs` (as it's a documentation claim being verified)
- `evidence_class`: `DOCUMENT_CLAIM` (existing enum in `src/state.py`)
- `found`: `False` (indicating a hallucination)
- `location`: The file path mentioned in the doc.
- `rationale`: "Path cited in documentation does not exist in the repository manifest."

## Validation Rules

1. **Path Sanitization**: All documentary paths MUST be passed through `Path(p).parts` or similar to ensure no `..` traversal above the repo root.
2. **Mandatory Keys**: The aggregator MUST check for the presence of `repo` and `docs` keys in the `evidences` dict.
3. **Deduplication**: `evidence_id` MUST be unique across all sources.

## Lifecycle Transitions

1. **Raw Evidence Collection**: Detectives create `Evidence` objects in parallel.
2. **State Merge (LangGraph Automatic)**: The `merge_evidences` reducer runs as the detectives return their results to the graph.
3. **Aggregation & Verification**: The `EvidenceAggregator` node reads the merged `evidences` dict, performs cross-path verification, and appends NEW `Evidence` objects (hallucination flags) back to the `evidences["docs"]` list.
4. **Finalized Evidence**: The state is now ready for judges.
