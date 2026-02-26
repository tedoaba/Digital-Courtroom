# Quickstart: Configuring Bounded Concurrency

## 1. Environment Configuration

Add the following variables to your `.env` file to control the evaluation throughput and reliability:

```bash
# Concurrency Control
MAX_CONCURRENT_LLM_CALLS=5

# Retry & Backoff
RETRY_INITIAL_DELAY=1.0
RETRY_MAX_DELAY=60.0
RETRY_MAX_ATTEMPTS=3

# Mode Selection
BATCHING_ENABLED=true  # Set to true to consolidate evaluations
```

## 2. Validation

To verify the bounded concurrency is working:

1. Run a full evaluation with `uv run python -m src.main ...`.
2. Check logs for `Queueing...` and `Acquired slot...` messages.
3. Observe that the total number of "Acquired" messages without a corresponding "Release" message never exceeds the `MAX_CONCURRENT_LLM_CALLS` limit.

## 3. Handling 429 Errors

If the provider returns a "Rate Limit Exceeded" (429) error:

- The system will log a warning.
- It will wait for the `RETRY_INITIAL_DELAY`.
- It will retry with exponential increases (`2s`, `4s`, `8s`...) until success or reaching `RETRY_MAX_DELAY`.
