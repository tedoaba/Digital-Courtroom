# Research Decision Log: Core Observability and Error Handling

## PII Redaction Strategy

### Decision

Implement a custom `PIIRedactionFilter` (inheriting from `logging.Filter`) combined with `python-json-logger`.

### Rationale

- **Regex-based Masking**: Provides a safety net for string-based PII (emails, phone numbers) appearing in messages.
- **Key-based Redaction**: Reliable way to scrub specific fields in structured payloads (e.g., `client_secret`).
- **Standard Library Alignment**: Using `logging.Filter` is non-intrusive and works across all handlers (stdout, file, etc.).

### Alternatives Considered

- **structlog**: Powerful but adds significant complexity and a new dependency that might conflict with other ecosystem tools.
- **Manual scrubbing**: Error-prone and hard to maintain across the codebase.

---

## LangSmith Context Propagation

### Decision

Use `langsmith.traceable` decorators for all orchestrator nodes and critical tool executions.

### Rationale

- **Native Integration**: LangGraph and LangChain automatically respect `langsmith` thread-local context.
- **Auto-Nesting**: `@traceable` correctly identifies parent spans without explicit ID passing.
- **Minimal Overhead**: Only active when `LANGCHAIN_TRACING_V2=true`.

### Alternatives Considered

- **OpenTelemetry with Manual Spans**: Too much boilerplate for the current project scale.
- **Manual ID Passing**: Violates the "automatic propagation" requirement in the feature spec.

---

## Exception Mapping

### Decision

Categorize all framework exceptions into `RetryableException` (Map to `WARNING` logs) and `FatalException` (Map to `CRITICAL` logs).

### Rationale

- **Alertability**: Mapping Fatal errors to `CRITICAL` allows simple cloud monitoring alerts on log streams.
- **Recovery Logic**: Distinguishing retryable errors at the type level simplifies LangGraph node retry configurations.

### Alternatives Considered

- **Standard Python Exceptions**: Lacks the semantic meaning needed for automated recovery decisions.
