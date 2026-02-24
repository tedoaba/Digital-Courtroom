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

with clone_repo("https://github.com/user/repo") as (tmp, repo_path):
    commits = extract_git_history(repo_path)
    print(f"Found {len(commits)} commits")
```

### AST Analysis

```python
from src.tools.ast_tools import scan_repository

findings = scan_repository(repo_path)
for finding in findings:
    print(f"Found {finding.node_type}: {finding.name}")
```

### PDF Ingestion

```python
from src.tools.doc_tools import ingest_pdf

chunks = ingest_pdf("path/to/report.pdf")
print(f"Extracted {len(chunks)} text chunks")
```
