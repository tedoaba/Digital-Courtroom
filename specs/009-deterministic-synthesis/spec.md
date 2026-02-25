# Feature Specification: Deterministic Synthesis via Chief Justice (Layer 3)

**Feature Branch**: `009-deterministic-synthesis`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Deterministic Synthesis via Chief Justice (Layer 3) - objective: Consolidate varying judicial opinions deterministically using strict precedence rules. Problem: Ensures non-LLM, guaranteed rule-based outcome resolution prioritizing Facts and Security over varied judge score spreads."

## Clarifications

### Session 2026-02-25

- Q: Missing Judge Fallback Strategy → A: Use the mean of the remaining two judge scores (rounded).
- Q: Scoring Tie-Breaking Direction → A: Round half up (e.g., 2.5 becomes 3).

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Resolving Conflicting Judicial Opinions (Priority: P1)

As a System Auditor, I want the Chief Justice to resolve conflicting scores from the Prosecutor, Defense, and Tech Lead using a transparent, rule-based engine, so that the final verdict is predictable and reproducible without LLM non-determinism.

**Why this priority**: Core objective of the Digital Courtroom. Resolving the "Thesis-Antithesis" into "Synthesis" is the final step of the reasoning pipeline.

**Independent Test**: Can be tested by providing a mock array of 3 `JudicialOpinion` objects with high variance (e.g., scores 1, 3, 5) and verifying the synthesized `CriterionResult` matches the calculated weighted outcome.

**Acceptance Scenarios**:

1. **Given** three judges return scores 2, 4, 3 for a non-security criterion, **When** Chief Justice executes, **Then** the final score is calculated using the FUNCTIONALITY_WEIGHT rule (TechLead weight = 2x) and rounded to the nearest integer.
2. **Given** a variance between scores is 3 or 4, **When** Chief Justice executes, **Then** a DISSENT_REQUIREMENT flag is triggered and a summary of the conflict is required in the output model.

---

### User Story 2 - Security Constraint Enforcement (Priority: P1)

As a Security Officer, I want confirmed security vulnerabilities to automatically cap the project's score, even if other judges argue for high marks due to "intent" or "effort," so that dangerous code is never given a passing grade.

**Why this priority**: Critical for system safety. Security overrides ensure that "Vibe Coding" doesn't mask fundamental flaws.

**Independent Test**: Provide a high Defense score (5) and a low Prosecutor score (1) with documented "os.system" usage; verify the final score is capped (e.g., at 3) despite the high Defense score.

**Acceptance Scenarios**:

1. **Given** the Prosecutor's argument contains confirmed security keywords (e.g., "shell injection") AND the RepoInvestigator found evidence of `os.system` usage, **When** Chief Justice executes, **Then** the `SECURITY_OVERRIDE` rule is applied and the final score is capped at 3.

---

### User Story 3 - Fact-Checking Judicial Arguments (Priority: P2)

As a Forensic Expert, I want the Chief Justice to invalidate judicial claims that cite non-existent evidence, so that the final report is grounded in verified repository facts rather than LLM hallucinations.

**Why this priority**: Prevents "hallucination leak" from the LLM judges into the final deterministic report.

**Independent Test**: Provide a Defense opinion citing `evidence_id: repo_01`, but mark `repo_01` as `found: False` in the Evidence pool. Verify the Defense's score influence is suppressed.

**Acceptance Scenarios**:

1. **Given** a `JudicialOpinion` cites an `evidence_id` that has `found=False` in the state, **When** Chief Justice executes, **Then** the `FACT_SUPREMACY` rule is applied, the judge's score is penalized/adjusted, and the event is logged.

---

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: Chief Justice MUST be implemented as a pure Python component with ZERO LLM operations.
- **FR-002**: System MUST accept an array of `JudicialOpinion` objects and a dictionary of `Evidence` objects as input.
- **FR-003**: System MUST calculate score variance (max - min) for every rubric dimension.
- **FR-004**: System MUST apply the `SECURITY_OVERRIDE` rule: confirmed security flaws (found in Evidence) MUST cap the criterion score at 3, overriding any higher scores.
- **FR-005**: System MUST apply the `FACT_SUPREMACY` rule: any judicial argument citing non-existent evidence (`found=False`) MUST have its score influence automatically suppressed or penalized.
- **FR-006**: System MUST apply the `FUNCTIONALITY_WEIGHT` rule: the Tech Lead's score carries double weight (2.0x) for technical/architectural criteria. Calculations MUST use "round half up" logic for fractional scores.
- **FR-007**: System MUST generate a `CriterionResult` model for every dimension, including the `final_score` and a `dissent_summary` if variance > 2.
- **FR-008**: System MUST log detailed execution traces for every criterion in a structured `execution_log` field, including raw scores, variance, specific rules applied, and intermediate calculation steps.
- **FR-009**: System MUST handle cases where a judge's opinion is missing (due to node failure) by calculating the mean of the remaining two judge scores (using "round half up" logic) and logging a "Degraded Synthesis" state.
- **FR-010**: System MUST apply the `VARIANCE_RE_EVALUATION` rule: if score variance > 2, the system MUST perform an automated secondary check of the cited evidence relevance vs the judge arguments and flag the result for manual verification with a `re_evaluation_required` flag.

### Key Entities _(include if feature involves data)_

- **CriterionResult**: The final synthesized output for a rubric dimension. Contains the final integer score, list of judge opinions, dissent summary, execution log, and re-evaluation status.
- **JudicialOpinion**: Input from Layer 2. Contains the judge ID, criterion ID, score (1-5), and evidence citations.
- **Evidence**: Forensic facts from Layer 1. Used to validate judicial claims (Fact Supremacy) and confirm security violations (Security Override).

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of `final_score` computations are deterministic and reproducible (same input = same output every time).
- **SC-002**: 100% of confirmed security violations result in a capped score, regardless of other judge inputs.
- **SC-003**: 100% of hallucinations (citing non-existent evidence) are successfully detected and suppressed by the `FACT_SUPREMACY` logic.
- **SC-004**: Processing time for the synthesis node is < 50ms (since it avoids LLM calls).
- **SC-005**: Each criterion in the generated state includes a structured log of all applied rules for traceability.
