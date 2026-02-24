# Quickstart: Using the State Schema

## 1. Initializing State

The state starts with the input judicial opinion text.

```python
from src.state import AgentState

initial_state: AgentState = {
    "opinion_text": "Court case text here...",
    "evidence": [],
    "judicial_opinions": [],
    "results": {},
    "errors": []
}
```

## 2. Creating Models with Validation

Pydantic enforces constraints at runtime.

```python
from src.state import Evidence, CriterionResult

# This works
e = Evidence(source_ref="p1", content="Fact", relevance_confidence=0.9)

# This raises ValidationError
e = Evidence(source_ref="p1", content="Fact", relevance_confidence=1.5)
```

## 3. Parallel State Merging

When two nodes return state updates at the same time:

```python
# Node A returns: {"results": {"TRANS": res1}}
# Node B returns: {"results": {"TRANS": res2}}

# If res1.relevance_confidence > res2.relevance_confidence,
# the final state results['TRANS'] will contain res1.
```
