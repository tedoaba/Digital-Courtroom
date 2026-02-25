# Quickstart: Testing the Evidence Aggregator

This document explains how to verify the `EvidenceAggregator` node in isolation using `pytest`.

## Prerequisites

- `uv` installed
- `pytest` installed (`uv pip install pytest`)

## Running Unit Tests

The unit tests simulate the fan-in state and verify merging and cross-referencing logic.

```bash
uv run pytest tests/unit/test_evidence_aggregator.py
```

## Mocking the State

To test the aggregator manually or in a script:

```python
from src.nodes.evidence_aggregator import aggregator_node
from src.state import AgentState, Evidence, EvidenceClass
from datetime import datetime

# 1. Setup mock evidence
repo_ev = Evidence(
    evidence_id="repo_GIT_0",
    source="repo",
    evidence_class=EvidenceClass.GIT_FORENSIC,
    goal="List files",
    found=True,
    location="root",
    content="src/main.py, src/utils.py", # Aggregator parses manifest from content
    confidence=1.0,
    timestamp=datetime.now()
)

doc_ev = Evidence(
    evidence_id="docs_CLAIM_0",
    source="docs",
    evidence_class=EvidenceClass.DOCUMENT_CLAIM,
    goal="Verify auth",
    found=True,
    location="p. 5",
    content="implemented in src/auth.py",
    confidence=0.9,
    timestamp=datetime.now()
)

# 2. Call the node
state = {
    "evidences": {"repo": [repo_ev], "docs": [doc_ev]},
    "errors": []
}
result = aggregator_node(state)

# 3. Verify Hallucination Flag
# Since src/auth.py is NOT in the repo manifest, a new evidence item should exist in result["evidences"]["docs"]
```
