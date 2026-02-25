# Quickstart: Using the State Schema

## 1. Initializing State

The state starts with the input judicial opinion text.

```python
from src.state import AgentState

initial_state: AgentState = {
    "opinion_text": "Court case text here...",
    "evidences": {},
    "opinions": [],
    "criterion_results": {},
    "errors": []
}
```

## 2. Creating Models with Validation

Pydantic enforces constraints and strict typing at runtime.

```python
from src.state import Evidence, CriterionResult

# This works (Integers and floats provided correctly)
e = Evidence(source_ref="p1", content="Fact", relevance_confidence=0.9)

# This raises ValidationError (relevance_confidence out of bounds [0,1])
e = Evidence(source_ref="p1", content="Fact", relevance_confidence=1.5)

# This raises ValidationError (extra field 'notes' not allowed)
e = Evidence(source_ref="p1", content="Fact", relevance_confidence=0.5, notes="some note")

# This raises ValidationError (strict=True, numeric_score must be int, not "5")
c = CriterionResult(criterion_id="T1", numeric_score="5", reasoning="...")
```

## 3. Security Override Usage

The `security_violation_found` flag triggers capping in the synthesis layer.

```python
# A result found to have a security flaw
c = CriterionResult(
    criterion_id="SEC-01",
    numeric_score=5,  # Judge thought it was good...
    reasoning="...",
    security_violation_found=True  # ...but a flaw was detected
)
# The Chief Justice node will cap this at 3 in the final report.
```

## 4. Parallel State Merging (Fatal on Error)

Custom reducers prevent structural corruption.

```python
from src.state import merge_evidences

# This works
merged = merge_evidences(dict_a, dict_b)

# This raises TypeError (Fatal Exception per spec)
# if a node accidentally returns a string instead of a dict
merged = merge_evidences(dict_a, "invalid update")
```
