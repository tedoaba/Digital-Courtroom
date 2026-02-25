# Requirements Quality Checklist: Deterministic Synthesis (Layer 3)

**Purpose**: Unit Tests for Requirements - Validating the quality, clarity, and completeness of the Chief Justice synthesis logic.
**Created**: 2026-02-25
**Feature**: [spec.md](../spec.md)

## Mathematical Rigor & Precision

- [x] CHK001 - Is the "Round Half Up" logic specified with precision edge cases (e.g., handling 2.499 vs 2.5)? [Clarity, Spec §FR-006]
- [x] CHK002 - Is the order of operations between weighted averaging and the security cap explicitly defined? [Consistency, Spec §FR-006, Research §Decision: Security Override]
- [x] CHK003 - Is the "penalty value" for Fact Supremacy violations (e.g., -2 points) quantified in the requirement? [Clarity, Spec §FR-005]
- [x] CHK004 - Does the requirement specify if weighted scores are rounded per-criterion or only at the final global aggregation? [Clarity, Spec §FR-006]
- [x] CHK005 - Is the handling of float-to-integer casting for the `final_score` (int 1-5) unambiguously defined? [Clarity, Spec §FR-006, Research §Decision: Python "Round Half Up"]

## Constitutional Alignment (Principle XI)

- [x] CHK006 - Does the spec explicitly reference the five synthesis priorities from Digital Courtroom Constitution §XI? [Traceability, Research §Decision: Constitutional Alignment]
- [x] CHK007 - Are the specific "Security Keywords" that trigger the override enumerated or referenced? [Completeness, Spec §Clarifications]
- [x] CHK008 - Is the "Dissent Summary" content (e.g., which judge IDs to include) specified for variance > 2? [Completeness, Spec §FR-007, Data Model §CriterionResult]
- [x] CHK009 - Does the spec explicitly prohibit LLM usage within the synthesis node to satisfy Principle III.5? [Consistency, Spec §FR-001]
- [x] CHK010 - Are the criteria for "High Variance (>2)" based on raw scores or adjusted scores? [Clarity, Spec §FR-003, FR-010]

## Layer 4 Handoff & Serialization

- [x] CHK011 - Is the required output data shape for the Report Generator (Layer 4) fully documented (e.g., serialized Markdown vs nested Pydantic)? [Handoff, Data Model §CriterionResult]
- [x] CHK012 - Are the remediation instructions required to be aggregated into a single string or kept as a list per judge? [Clarity, Spec §FR-007, Data Model §CriterionResult]
- [x] CHK013 - Does the spec define the visual format/templates required for the "Dissent Summary" in the final state? [Handoff, Spec §User Scenarios, Research §Decision: Deterministic Dissent Summary]

## Resilience & Edge Case Coverage

- [x] CHK014 - Are requirements defined for the "Extreme Failure" scenario where 0 out of 3 judges return an opinion? [Recovery, Spec §FR-009]
- [x] CHK015 - Is the behavior specified for "Zero Evidence" scenarios (no information to verify Fact Supremacy)? [Edge Case, Spec §FR-009]
- [x] CHK016 - Does the spec define how to handle "Judge Persona Collusion" (all judges providing identical scores for the same reasons)? [Coverage, Spec §FR-003, FR-010]
- [x] CHK017 - Are requirements specified for partial judge failures (e.g., 1 judge fails, 2 succeed)? [Recovery, Spec §FR-009]
- [x] CHK018 - Does the spec define what happens if a judge cites a valid Evidence ID but providing a conflicting interpretation of its "found" status? [Conflict, Spec §FR-005]

## Non-Functional Quality

- [x] CHK019 - Is the 50ms latency requirement accompanied by a specific hardware or environment assumption? [Clarity, Spec §SC-004]
- [x] CHK020 - Are the execution trace logging requirements specified with a mandatory field list for auditability? [Completeness, Spec §FR-008]
