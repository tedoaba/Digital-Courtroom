# Data Model: Foundational Scaffolding

This document defines the core data structures for the configuration system and the initial foundation of the Digital Courtroom.

## Entity: SystemSettings (Pydantic Model)

Represents the validated configuration of the application.

| Field                  | Type        | Description               | Validation                          |
| ---------------------- | ----------- | ------------------------- | ----------------------------------- |
| `OPENAI_API_KEY`       | `SecretStr` | Key for OpenAI services   | Mandatory                           |
| `LANGCHAIN_API_KEY`    | `SecretStr` | Key for LangSmith tracing | Mandatory                           |
| `LANGCHAIN_TRACING_V2` | `bool`      | Toggle for tracing        | Default: `True`                     |
| `LANGCHAIN_PROJECT`    | `str`       | Project name in LangSmith | Default: `"digital-courtroom"`      |
| `DEFAULT_MODEL`        | `str`       | Primary LLM name          | Default: `"gpt-4o"`                 |
| `TEMPERATURE`          | `float`     | LLM Temperature           | Constant: `0.0` (Constitution XXIV) |
| `LOG_LEVEL`            | `str`       | System log level          | Default: `"INFO"`                   |

## Entity: AppState (Initial Prototype)

Placeholder for the LangGraph state defined in Constitution Principle IV.

| Field       | Type                        | Description                                        |
| ----------- | --------------------------- | -------------------------------------------------- |
| `repo_url`  | `str`                       | URL of the repository to audit                     |
| `pdf_path`  | `str`                       | Path to the PDF audit report                       |
| `evidences` | `Dict[str, List[Evidence]]` | Merged forensic facts (Reducer: `operator.ior`)    |
| `opinions`  | `List[JudicialOpinion]`     | Appended judicial scores (Reducer: `operator.add`) |

## File Path Constraints

| Path            | Type           | Purpose                                        |
| --------------- | -------------- | ---------------------------------------------- |
| `src/config.py` | Implementation | Loads `SystemSettings`                         |
| `.env`          | External       | Storage of `SecretStr` values (Ignored by Git) |
| `.env.example`  | Template       | Developer onboarding template                  |
