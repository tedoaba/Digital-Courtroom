# Research: ContextBuilder Initialization Node

## Decision 1: Input Validation Strategy

- **Decision**: Use a strict regex pattern for `repo_url` validation and `os.path.exists()` for `pdf_path`.
- **Rationale**:
  - **Regex**: `^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$` ensures that only valid GitHub HTTPS URLs are processed, preventing shell injection and SSRF attempts.
  - **Blacklist**: Explicitly rejecting `localhost`, `127.0.0.1`, and `file://` provides an extra layer of security against local environment probes (Const. XV.4).
  - **Path Check**: `os.path.exists()` is the standard, efficient way to verify local file presence before attempting to parse.
- **Alternatives Considered**:
  - `validators` library: Rejected to keep dependencies minimal (Const. XXIII).
  - `requests.head()` for URL check: Rejected because it requires network access and the actual cloning is handled by the `RepoInvestigator`.

## Decision 2: State Initialization Approach

- **Decision**: Initialize `evidences`, `opinions`, and `criterion_results` as explicit empty structures (`{}` and `[]`) in the `AgentState`.
- **Rationale**:
  - **Reducer Compatibility**: LangGraph reducers like `operator.add` and `operator.ior` require the base objects to exist to perform merges correctly during parallel fan-in.
  - **Fault Tolerance**: Pre-initializing empty collections allows downstream nodes to iterate over them without special `None` checks, reducing boilerplate across the swarm.
- **Alternatives Considered**:
  - Initializing as `None`: Rejected as it complicates reducer logic and requires optional typing throughout the graph.

## Decision 3: Error Handling Philosophy

- **Decision**: Append error messages to `state['errors']` and return the state, rather than raising exceptions.
- **Rationale**:
  - **Graph Continuity**: In a complex MAS, a configuration error in one run shouldn't necessarily crash the entire application process if it's running as a service.
  - **Routing Integration**: This approach allows the LangGraph to use a conditional edge to route to the `ErrorHandler` then to `ReportGenerator`, ensuring a "failed audit" report is produced with the error details (as per the StateGraph flow in architecture notes).
- **Alternatives Considered**:
  - Raising `InvalidInputError`: Rejected for production-grade graph execution where graceful degradation is required (Const. VII.5).
