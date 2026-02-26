# Data Model: Bounded Concurrency Refactor

## Configuration Schema

The concurrency and retry settings are managed via the `JudicialSettings` Pydantic model, which reads from environment variables.

### `JudicialSettings` (Updated)

| Field                      | Type    | Default | Description                                     |
| -------------------------- | ------- | ------- | ----------------------------------------------- |
| `max_concurrent_llm_calls` | `int`   | `5`     | Global semaphore limit for active LLM requests. |
| `retry_initial_delay`      | `float` | `1.0`   | Initial exponential backoff delay in seconds.   |
| `retry_max_delay`          | `float` | `60.0`  | Maximum cap for exponential backoff delay.      |
| `retry_max_attempts`       | `int`   | `3`     | Maximum number of retry attempts per request.   |
| `batching_enabled`         | `bool`  | `False` | Toggle for "Structured Batching" mode.          |

## State Merging

The `AgentState` remains largely unchanged as the existing reducers already support variable-length list merging for opinions.

- **`opinions`**: `Annotated[list[JudicialOpinion], operator.add]`
  - If a judge evaluates 10 dimensions in one batched call, the node returns a list of 10 `JudicialOpinion` objects.
  - The `operator.add` reducer will append all 10 to the global state seamlessly.

## Batching Contract

When `batching_enabled=True`, the LLM prompt is modified to request a JSON list:

```json
[
  {
    "opinion_id": "Prosecutor_DIM1_...",
    "judge": "Prosecutor",
    "criterion_id": "DIM1",
    "score": 4,
    "argument": "...",
    "cited_evidence": ["ev1", "ev2"]
  },
  ...
]
```

The response parser will validate each item and identify any missing `criterion_id`s for subsequent granular retries.
