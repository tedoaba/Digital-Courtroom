# Data Model: ContextBuilder Initialization Node

This document defines the state initialization and data structures managed by the `ContextBuilder` node.

## State Initialization

The `ContextBuilder` is responsible for populating the following fields in the `AgentState` (`src/state.py`):

| Field               | Type                         | Initialization Logic                                                    |
| :------------------ | :--------------------------- | :---------------------------------------------------------------------- |
| `rubric_dimensions` | `List[Dict]`                 | Loaded from the `dimensions` array in the rubric JSON.                  |
| `synthesis_rules`   | `Dict[str, str]`             | Loaded from the `synthesis_rules` object in the rubric JSON.            |
| `evidences`         | `Dict[str, List[Evidence]]`  | Initialized as an empty dictionary `{}` to enable parallel merge logic. |
| `opinions`          | `List[JudicialOpinion]`      | Initialized as an empty list `[]` to enable parallel aggregation.       |
| `criterion_results` | `Dict[str, CriterionResult]` | Initialized as an empty dictionary `{}`.                                |
| `errors`            | `List[str]`                  | Initialized as `[]` (or appended to if validation fails).               |

## Input Validation Rules

The node enforces the following constraints on incoming state before proceeding:

### 1. Repository URL (`repo_url`)

- **Pattern**: `^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$`
- **Forbidden Schemes**: `file://`, `ftp://`
- **Forbidden Hosts**: `localhost`, `127.0.0.1`
- **Validation Action**: If invalid, append `"Invalid URL format: {url}"` to `errors`.

### 2. PDF Path (`pdf_path`)

- **Check**: `os.path.exists(pdf_path)`
- **Validation Action**: If missing, append `"Missing PDF report at: {path}"` to `errors`.

### 3. Rubric File (`rubric_path`)

- **Check**: `os.path.exists(rubric_path)` AND `json.loads()` success.
- **Validation Action**: If missing or malformed, append `"Fatal: Could not load rubric from {path}"` to `errors`.

## Rubric Schema (Input)

The expected structure of the `rubric_path` JSON file:

```json
{
  "rubric_metadata": {
    "version": "string"
  },
  "dimensions": [
    {
      "id": "string",
      "name": "string",
      "target_artifact": "string",
      "forensic_instruction": "string",
      "success_pattern": "string",
      "failure_pattern": "string"
    }
  ],
  "synthesis_rules": {
    "rule_name": "rule_description"
  }
}
```
