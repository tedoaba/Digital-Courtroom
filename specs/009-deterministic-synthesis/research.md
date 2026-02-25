# Research: Deterministic Synthesis Logic

## Decision: Python "Round Half Up" Implementation

**Rationale**: Python's built-in `round()` function uses "round half to even" (e.g., `round(2.5)` is 2, `round(3.5)` is 4). The spec requires "round half up" (2.5 -> 3).
**Implementation**: Use `decimal.Decimal` with `ROUND_HALF_UP` or a helper function:

```python
def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier
```

Using `decimal` is safer for precision:

```python
from decimal import Decimal, ROUND_HALF_UP
def round_score(score):
    return int(Decimal(score).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
```

## Decision: Security Override Triggers

**Rationale**: Principle XI requires capping scores at 3 if security flaws are confirmed.
**Triggers**:

1.  **Evidence Search**: Check `evidences["repo"]` for findings where `found=True` and `evidence_class == EvidenceClass.SAFE_TOOLING` with specific content matches like `os.system`, `shell=True`, or `chmod 777`.
2.  **Judicial Signal**: If the Prosecutor's `charges` list contains keywords like "Security Violation", "Shell Injection", or "Insecure Tooling".
    **Action**: If triggered, `final_score = min(final_score, 3)`.

## Decision: Deterministic Dissent Summary

**Rationale**: Principle X requires summarizing conflict without LLM calls.
**Strategy**: Use a template-based approach.
**Template**:
"Major conflict detected (variance={variance}). The Prosecutor argued for {p_score} citing {p_evidence}. The Defense argued for {d_score} highlighting {d_mitigations}. The Tech Lead's pragmatic assessment of {t_score} was used as the primary anchor."
**Components**:

- Variance calculation.
- Evidence ID extraction from opinions.
- Mitigation/Charge extraction from opinions.

## Decision: Variance Re-evaluation Logic

**Rationale**: Principle XI.5 requires explicit re-evaluation when variance > 2.
**Logic**:

- Calculate `variance = max(scores) - min(scores)`.
- If `variance > 2`:
  - Set `re_evaluation_required = True`.
  - Check if the high score citations are `found=True` but have low `confidence` (< 0.6).
  - If evidence quality is low, add a warning to `execution_log`.
  - Note: This is an automated flag; actual "reasoning" change remains deterministic.

## Decision: Fact Supremacy Nullification

**Rationale**: If a judge cites non-existent evidence, their influence must be suppressed.
**Logic**:

- Iterate over `opinion.cited_evidence`.
- Cross-reference with `state["evidences"]`.
- If any `evidence_id` is missing or has `found=False`, penalize that judge's score: `adjusted_score = max(1, original_score - penalty_value)` where `penalty_value = 2`.
- Log the nullification in `execution_log`.

## Decision: Constitutional Alignment (Principle XI)

**Rationale**: Ensure the synthesis node strictly follows the legal hierarchy of the Digital Courtroom.
**Synthesis Priorities (Hierarchy)**:

1.  **Security Override**: Hard cap at 3.0 for any verified critical vulnerability.
2.  **Fact Supremacy**: Penalty/Nullification for citing non-existent facts.
3.  **Functionality Weight**: Tech Lead weighting (2.0x) for technical dimensions.
4.  **Dissent Requirement**: Mandatory template-based summary for variance > 2.
5.  **Variance Re-evaluation**: Automatic flagging for human audit if variance > 2.

## Alternatives Considered

- **LLM-based Synthesis**: Rejected by Principle III.5 and XI (requires deterministic Python logic).
- **Simple Averaging**: Rejected by Principle XI (requires weighted scores and overrides).
- **Hard-coding exact keywords**: Preferring a combination of Evidence class and keyword scanning for robustness.
