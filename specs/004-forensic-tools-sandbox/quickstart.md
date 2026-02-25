# Quickstart: Sandboxed Forensic Execution Interfaces

## Prerequisites

- Windows OS (Dev)
- `uv` installed
- `git` installed (v2.17+ recommended for list-argument stability) and in PATH

## Installation

```bash
uv add docling pydantic
```

## Basic Usage

### Cloning and History

```python
from src.tools.repo_tools import clone_repo, extract_git_history

with clone_repo("https://github.com/user/repo") as result:
    if result.status == "success":
        repo_path = result.data[0]
        history_result = extract_git_history(repo_path)
        if history_result.status == "success":
            print(f"Found {len(history_result.data)} commits")
    else:
        print(f"Clone failed: {result.error}")
```

### AST Analysis

```python
from src.tools.ast_tools import scan_repository

findings_result = scan_repository("path/to/repo")
if findings_result.status == "success":
    for finding in findings_result.data:
        print(f"Found {finding.node_type}: {finding.name}")
```

### PDF Ingestion

```python
from src.tools.doc_tools import ingest_pdf

result = ingest_pdf("path/to/report.pdf")
if result.status == "success":
    markdown_text = result.data[0]
    print("Extracted MKD:", markdown_text[:100])
```

### Visual Extraction

```python
from src.tools.vision_tools import extract_visuals
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmpdir:
    result = extract_visuals("path/to/report.pdf", workspace=tmpdir)
    if result.status == "success":
        print(f"Extracted images to: {result.data}")
```
