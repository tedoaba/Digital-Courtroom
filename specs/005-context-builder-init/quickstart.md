# Quickstart: ContextBuilder Initialization Node

This guide explains how to invoke the `ContextBuilder` node within the `Digital Courtroom` graph.

## Configuration

The node reads the rubric path from the initial state or defaults to the week 2 rubric.

| Field         | Meaning                                  | Default                    |
| :------------ | :--------------------------------------- | :------------------------- |
| `rubric_path` | Path to the machine-readable rubric JSON | `rubric/week2_rubric.json` |

## Usage

### 1. Initial State Definition

To start an audit, provide the required inputs in the graph invocation:

```python
from src.graph import app

initial_state = {
    "repo_url": "https://github.com/user/project",
    "pdf_path": "./audit_report.pdf",
    "rubric_path": "rubric/week2_rubric.json" # Optional
}

# Run the graph
result = app.invoke(initial_state)
```

### 2. Validation Failures

If the inputs are invalid, the node will populate the `errors` field. You can check for failures immediately:

```python
if result.get("errors"):
    print(f"Audit setup failed: {result['errors']}")
```

## Internal Workflow

1. **Log Entry/Exit**: Emits `context_builder_entry` and `context_builder_exit` events.
2. **Validate URL**: Checks syntax and security constraints.
3. **Validate Files**: Checks existence of PDF and Rubric.
4. **Parse Rubric**: Extracts dimensions and rules into the `AgentState`.
5. **Initialize Collections**: Sets up empty `evidences` and `opinions` structures.
6. **Return State**: Passes the enriched state to the next graph layer.
