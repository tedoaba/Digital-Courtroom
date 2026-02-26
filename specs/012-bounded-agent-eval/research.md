# Research: Bounded Concurrency and Structured Batching

## Decision: Concurrency Control via `asyncio.Semaphore`

### Rationale

`asyncio.Semaphore` is the most direct and lightweight way to enforce a global concurrency limit in an asynchronous Python application using LangGraph. Since LangGraph nodes in a single run typically share the same event loop, a module-level semaphore instance initialized with `MAX_CONCURRENT_LLM_CALLS` will effectively throttle parallel LLM invocations across all active agents and criteria evaluations.

### Implementation Pattern

```python
# Create a global semaphore in src/nodes/judges.py or src/concurrency.py
concurrency_semaphore = asyncio.Semaphore(settings.max_concurrent_llm_calls)

async def evaluate_criterion(task: JudicialTask):
    async with concurrency_semaphore:
        logger.info(f"Acquired slot for {task['judge_name']}")
        # logic...
```

---

## Decision: Exponential Backoff with `tenacity`

### Rationale

The project already uses `tenacity`, which is highly compatible with `langchain` and `asyncio`. We will update the retry configuration to strictly follow the specification (1s initial delay, 60s max, with jitter).

### Configuration

```python
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60), # multiplier=1, min=1 means starts at 1s
    retry=retry_if_exception_type((RateLimitError, APIError)), # Target specific LLM errors
    reraise=True
)
```

---

## Decision: Structured Batching for Criteria Evaluation

### Rationale

"Structured Batching" drastically reduces the number of LLM calls by evaluating all dimensions in a single request per judge. This changes the fan-out from (Agents x Dimensions) to just (Agents).

### Pattern for Partial Success

If the LLM returns evaluations for 8 out of 10 dimensions, the system will:

1. Accept the 8 successful evaluations.
2. Identify the 2 missing dimension IDs.
3. Automatically trigger 2 separate parallel calls (still throttled by the semaphore) to complete the missing work.

### Prompting Strategy

The prompt will be modified to ask for a list of `JudicialOpinion` objects corresponding to the provided criteria list.

---

## Alternatives Considered

### Worker Pool (Queue Based)

- **Evaluation**: Would require a centralized queue and background worker tasks.
- **Result**: Rejected as over-engineered for the current LangGraph architecture. `asyncio.Semaphore` provides the same benefit with significantly less boilerplate.

### Simple `asyncio.gather` with chunking

- **Evaluation**: Divide the 30 tasks into chunks of N and run them sequentially.
- **Result**: Rejected because it's less flexible than a semaphore. A semaphore allows a new task to start as soon as any previous one finishes, maximizing throughput within the limit.

### Using `langgraph` built-in concurrency limits

- **Evaluation**: Some LangGraph implementations allow limiting parallel execution of certain nodes.
- **Result**: `asyncio.Semaphore` inside the node provides more granular control over specifically the _LLM call_ part of the node's execution, which is the primary source of 429 errors.
