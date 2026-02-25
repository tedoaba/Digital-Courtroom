# Requirements Quality Checklist: Dialectical Judicial Agents (Layer 2)

**Purpose**: "Unit Tests for Requirements" — validating the quality, clarity, and completeness of the judicial layer specification.
**Created**: 2026-02-25
**Feature**: [spec.md](../spec.md)
**Focus**: Reasoning Quality & Execution Resilience (Author/Reviewer mix)

## Requirement Completeness

- [ ] CHK001 - Are prompt construction requirements defined for all three personas (Prosecutor, Defense, TechLead)? [Completeness, Spec §FR-001]
- [ ] CHK002 - Does the spec define how the judicial layer handles the transition from EvidenceAggregator? [Completeness, Spec §Assumptions]
- [ ] CHK003 - Are the specific requirements for "Persona Philosophy Blocks" documented? [Completeness, Plan §Phase 0]
- [ ] CHK004 - Are requirements specified for handling conflicting evidence from multiple detectives? [Gap]

## Requirement Clarity

- [ ] CHK005 - Is the "< 10% text overlap" requirement measurable and defined with a specific method (e.g., Jaccard similarity)? [Clarity, Spec §FR-002, SC-002]
- [ ] CHK006 - Is the "neutral fallback" state clarified with exact default values for all schema fields? [Clarity, Spec §Clarifications]
- [ ] CHK007 - Is "granular parallelization" clearly defined as one call per persona per criterion? [Clarity, Spec §FR-011]
- [ ] CHK008 - Is the meaning of "Critical", "Optimistic", and "Pragmatic" lenses quantified with specific behavioral expectations? [Clarity, Spec §FR-003, 004, 005]

## Requirement Consistency

- [ ] CHK009 - Do the retry requirements in §FR-007 align with the exponential backoff requirements in §FR-008? [Consistency]
- [ ] CHK010 - Is the use of `JudicialOpinion` consistent across Functional Requirements and Data Model entities? [Consistency, Spec §FR-006, §Key Entities]
- [ ] CHK011 - Does the requirement for `temperature=0` consistently apply to all judicial prompts? [Consistency, Spec §FR-009, SC-005]

## Acceptance Criteria Quality

- [ ] CHK012 - Can the verify-ability of cited `evidence_id` values be objectively tested? [Measurability, Spec §SC-004]
- [ ] CHK013 - Is the pass/fail threshold for prompt similarity analysis specifically defined (e.g., native text vs. templated markers)? [Measurability, Spec §SC-002]
- [ ] CHK014 - Are the success criteria for LLM retry behavior (SC-001) technology-agnostic? [Measurability, Spec §SC-001]

## Scenario & Edge Case Coverage

- [ ] CHK015 - Does the spec define requirements for the "Empty Evidence" scenario? [Edge Case, Spec §Edge Cases]
- [ ] CHK016 - Are requirements specified for "Hallucinated Citations" (ids cited by judges that don't exist in detectives' output)? [Edge Case, Spec §Edge Cases]
- [ ] CHK017 - Is the behavior specified for "Schema Exhaustion" after max retries? [Exception Flow, Spec §Edge Cases]
- [ ] CHK018 - Does the spec define requirements for "Persona Collusion" detection? [Edge Case, Spec §Edge Cases]

## Non-Functional Requirements

- [ ] CHK019 - Are security requirements for sandboxed prompt construction (no data leakage) defined? [Security, Gap]
- [ ] CHK020 - Are performance targets for the 30+ parallel LLM calls specified? [Performance, Gap]
- [ ] CHK021 - Are logging requirements (Principle XXII) specifically mapped for node entry/exit and opinion rendering? [Observability, Constitution §XXII]

## Dependencies & Assumptions

- [ ] CHK022 - Is the dependency on Layer 1.5 (EvidenceAggregator) explicitly validated via requirements? [Dependency, Spec §Dependencies]
- [ ] CHK023 - Is the assumption of standardized model configuration in `config.py` documented? [Assumption, Spec §Assumptions]
