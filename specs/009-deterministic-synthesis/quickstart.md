# Quickstart: Testing Chief Justice Synthesis

This guide explains how to verify the deterministic synthesis rules of Layer 3.

## 1. Prerequisites

- `uv` installed.
- Repository set up with `uv sync`.

## 2. Unit Testing Synthesis Rules

The `ChiefJusticeNode` logic is entirely deterministic. You can run the unit tests directly:

```bash
uv run pytest tests/unit/test_justice.py
```

These tests verify:

- **Weighted Scoring**: `(Prosecutor + Defense + 2*TechLead) / 4`.
- **Rounding**: Verifying `2.5` becomes `3` and `2.25` becomes `2`.
- **Security Override**: Capping score at 3 when `os.system` evidence is present.
- **Fact Supremacy**: Penalty when a judge cites an evidence ID that is `found=False`.
- **Missing Judge**: Fallback to mean of remaining 2 judges.

## 3. Manual Verification

You can use the provided script to run a mock synthesis:

```bash
# Example command (TBD after implementation)
uv run python scripts/mock_synthesis.py
```

## 4. Expected Output

The synthesis node will update the `criterion_results` dictionary in the state. Each entry should look like:

```json
{
  "numeric_score": 3,
  "applied_rules": ["FUNCTIONALITY_WEIGHT", "ROUND_HALF_UP"],
  "dissent_summary": "Minor disagreement (variance=1) between Prosecutor and Defense resolved via Tech Lead weight.",
  "security_violation_found": false
}
```
