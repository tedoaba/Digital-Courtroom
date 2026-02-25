# Internal Contracts: Foundational Scaffolding

This document defines the internal interfaces for the core project foundation, primarily focused on configuration and environment validation.

## Contract: Configuration Provider

This contract defines the interface between the `config.py` module and all other application modules.

### Protocol

- **Implementation**: `src/config.py` provides a global `settings` object.
- **Access Pattern**: `from src.config import settings`
- **Validation**: All settings are validated at import time. Failure raises `ValidationError` and halts execution.

### Schema

```json
{
  "OPENAI_API_KEY": "SecretStr (Mandatory)",
  "LANGCHAIN_API_KEY": "SecretStr (Mandatory)",
  "LANGCHAIN_TRACING_V2": "bool (Default: true)",
  "LANGCHAIN_PROJECT": "str (Default: 'digital-courtroom')",
  "DEFAULT_MODEL": "str (Default: 'gpt-4o')",
  "TEMPERATURE": 0.0
}
```

## Contract: Directory Structure Integrity

Defines the physical organizational contract of the repository as required by Constitution Principle XX.

| Path           | Required | Contents / Role                          |
| -------------- | -------- | ---------------------------------------- |
| `src/`         | Yes      | All source code                          |
| `src/nodes/`   | Yes      | Individual LangGraph node logic          |
| `src/tools/`   | Yes      | External tool integrations               |
| `src/state.py` | Yes      | Typed project state (Pydantic/TypedDict) |
| `tests/`       | Yes      | Automated test suite                     |

## Contract: Command Execution (CLI)

Defines how developers and CI interact with the project.

| Intent    | Command                  |
| --------- | ------------------------ |
| Setup     | `uv sync`                |
| Execution | `uv run <target_script>` |
| Testing   | `uv run pytest`          |
| Quality   | `uv run ruff check .`    |
