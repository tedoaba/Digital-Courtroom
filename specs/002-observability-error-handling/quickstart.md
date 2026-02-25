## 1. Logging

To use the structured logger in a node or tool:

```python
from src.utils.logger import StructuredLogger

logger = StructuredLogger(name="my_node")

# Log lifecycle events (injects current correlation_id and metadata)
logger.log_node_entry(node_name="researcher_node", task_id="T1")
logger.log_evidence_created(evidence_id="E001", source="github")

# PII is auto-redacted in messages and payloads (Emails, Tokens)
logger.info("Found user emails", payload={"emails": ["alice@gmail.com", "bob@example.com"]})
# Output: {"timestamp": "...", "severity": "INFO", "payload": {"emails": ["[REDACTED_EMAIL]", "[REDACTED_EMAIL]"], "message": "..."}, ...}
```

## 2. Distributed Tracing

Tracing is automatic for functions decorated with `@traceable`. Configuration is managed via `src.config.settings`.

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls__...  # Your LangSmith API Key
export LANGCHAIN_PROJECT=digital-courtroom
```

## 3. Raising and Logging Errors

Use the exception hierarchy to drive automated recovery logic. The logger automatically maps `FatalException` to `CRITICAL` severity and `RetryableException` to `WARNING`.

```python
from src.exceptions import ConnectivityError, InvalidInputError
from src.utils.logger import StructuredLogger

logger = StructuredLogger(__name__)

# This indicates a transient failure (Retryable)
# Logger will output at WARNING severity
try:
    raise ConnectivityError("Cloud service unavailable")
except ConnectivityError as e:
    logger.error("Failed to connect", exc=e)

# This indicates a permanent failure (Fatal)
# Logger will output at CRITICAL severity for immediate alerting
try:
    raise InvalidInputError("Unsupported file format: .exe")
except InvalidInputError as e:
    logger.error("Terminal error", exc=e)
```
