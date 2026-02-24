# Quickstart Guide: Observability and Error Handling

## 1. Logging

To use the structured logger in a node or tool:

```python
from src.utils.logger import StructuredLogger

logger = StructuredLogger(name="my_node")

# Log lifecycle events
logger.log_node_entry(state={"input": "important"})
logger.log_evidence_created(evidence_id="E1", source="git")

# PII is auto-redacted in payloads
logger.info("Processing user", payload={"email": "user@example.com"})
# Output: {"timestamp": "...", "event_type": "info", "payload": {"email": "[REDACTED]"}}
```

## 2. Distributed Tracing

Tracing is automatic for functions decorated with `@traceable`. Ensure environment variables are set.

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls__...
export LANGCHAIN_PROJECT=courtroom-dev
```

## 3. Raising Errors

Choose the appropriate base class to drive recovery:

```python
from src.exceptions import NetworkError, InvalidInputError

# This will trigger 3 retries in the orchestrator (Retryable)
raise NetworkError("Connection failed")

# This will fail fast and log at CRITICAL level (Fatal)
raise InvalidInputError("Missing required field")
```
