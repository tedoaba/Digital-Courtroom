# Quickstart: Parallel Detective Agents (Layer 1)

## Overview

This feature implements the Layer 1 "Detectives" of the Digital Courtroom. These agents scan repositories, documents, and diagrams to gather factual evidence.

## Setup

Ensure you have `git` and `uv` installed.

1. **Install dependencies**:

   ```bash
   uv sync
   ```

2. **Set up Environment**:
   Create a `.env` file with your LLM API keys:
   ```env
   GOOGLE_API_KEY=your_key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_key
   ```

## Running Detectives

To run the detectives against a target repository and PDF:

```python
from src.graph import app

inputs = {
    "repo_url": "https://github.com/user/project",
    "pdf_path": "./reports/submission.pdf"
}

# Run the graph until the detectives complete
for output in app.stream(inputs):
    for key, value in output.items():
        if key in ["RepoInvestigator", "DocAnalyst", "VisionInspector"]:
            print(f"Evidence from {key}: {value['evidences']}")
```

## Testing

Run unit tests for the detectives:

```bash
uv run pytest tests/unit/nodes/test_detectives.py
uv run pytest tests/unit/tools/
```
