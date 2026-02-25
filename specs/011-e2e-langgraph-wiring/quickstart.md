# Quickstart: Wiring the E2E Graph

## Prerequisites

Ensure all individual nodes are verified via their own unit tests:

- `ContextBuilder`
- Detectives (Repo, Doc, Vision)
- EvidenceAggregator
- Judges (Prosecutor, Defense, TechLead)
- ChiefJustice
- ReportGenerator

## Implementation Steps

1. **Initialize StateGraph**:

   ```python
   builder = StateGraph(AgentState)
   ```

2. **Add Nodes**:
   Import all node functions and add them to the builder.

3. **Wire Edges**:
   - `START` to `ContextBuilder`.
   - `ContextBuilder` to the 3 detective nodes.
   - All 3 detectives to `EvidenceAggregator`.
   - `EvidenceAggregator` to the 3 judge nodes.
   - All 3 judges to `ChiefJustice`.
   - `ChiefJustice` (conditional) to `ReportGenerator`.

4. **Define Reducers**:
   Verify `src/state.py` has `Annotated[..., operator.add]` for the `opinions` list.

5. **Test Parallelism**:
   Run with a target repo and check LangSmith to ensure detectives start together.

## Running the End-to-End Audit

```bash
uv run audit --repo https://github.com/example/repo --spec ./my_report.pdf
```
