# Layer 1 Requirements Quality Checklist: Forensic Orchestration

**Purpose**: Validate the quality, completeness, and consistency of requirements for Layer 1 Parallel Detectives.
**Created**: 2026-02-25
**Feature**: [Parallel Detective Agents](../spec.md)
**Focus**: B (Orchestration & Forensic Rigor), Standard Risk, Both (Author/Reviewer/Constitutional Gate)

## Requirement Completeness

- [ ] **CHK001**: Are the specific forensic protocols (AST, Git, Tool Safety) defined for _every_ detective type? [Completeness, Spec §User Story 1]
- [ ] **CHK002**: Is the structure of the `Evidence` object explicitly defined for all three detectives (Repo, Doc, Vision)? [Completeness, Spec §Key Entities]
- [ ] **CHK003**: Are the required logging metadata fields (operation duration, artifact counts) documented for all nodes? [Completeness, Spec §FR-009]
- [ ] **CHK004**: Does the spec define the required filter logic for `rubric_dimensions` before dispatching to detectives? [Gap, Const. §XXI]
- [ ] **CHK005**: Are the specific Git log format requirements (`--oneline --reverse`) documented for forensic consistency? [Completeness, Spec §User Story 1]

## Requirement Clarity & Consistency

- [ ] **CHK006**: Is the "structural description" for `VisionInspector` quantified with specific complexity or length expectations? [Clarity, Spec §Clarifications]
- [ ] **CHK007**: Do the detective node signatures consistently follow the `AgentState` in/out contract? [Consistency, Contracts §Shared Interface]
- [ ] **CHK008**: Is "purely factual evidence" clarified with examples of forbidden interpretive language? [Clarity, Spec §FR-002, Const. §IX]
- [ ] **CHK009**: Are the 60-second timeout requirements applied consistently across all detective external operations? [Consistency, Spec §FR-008, Const. §XV]

## Scenario & Edge Case Coverage

- [ ] **CHK010**: Is the "Graceful Degradation" behavior defined for when _multiple_ detectives fail simultaneously? [Coverage, Spec §SC-003]
- [ ] **CHK011**: Does the spec define requirements for handling empty repositories or password-protected PDFs? [Edge Case, Spec §Edge Cases]
- [ ] **CHK012**: Are partial success scenarios (e.g., Git clone succeeds but AST parse fails) addressed in the evidence output requirements? [Coverage, Spec §Edge Cases]
- [ ] **CHK013**: Is the behavior specified for when the Vision LLM returns unparseable or non-compliant classification strings? [Edge Case, Spec §Edge Cases]

## Orchestration & State Safety

- [ ] **CHK014**: Does the requirement for `evidences` state mutation explicitly reference the use of `annotated` reducers to prevent parallel overwrites? [Consistency, Spec §Key Entities, Const. §VI]
- [ ] **CHK015**: Is the requirement for detectives to exclude sync/aggregation logic explicit to prevent architectural leakage? [Separation of Concerns, Spec §FR-006]
- [ ] **CHK016**: Are the unique ID format requirements (`{source}_{class}_{index}`) consistent for all detective outputs? [Consistency, Data Model §Evidence]

## Non-Functional & Security Requirements

- [ ] **CHK017**: Are the sandboxing requirements (no `os.system`, `tempfile` usage) documented as mandatory for any new tool introduction? [Security, Spec §FR-003, Const. §XV]
- [ ] **CHK018**: Is the mandatory `temperature=0` requirement for LLM nodes documented to ensure detective determinism? [Non-Functional, Const. §XXIV, Gap]
- [ ] **CHK019**: Are observability requirements for LangSmith tracing configuration documented? [Observability, Const. §XXII, Gap]

## Measurability & Success Criteria

- [ ] **CHK020**: Are the success criteria for "100% mocked testing" objectively verifiable without implementation knowledge? [Measurability, Spec §SC-001]
- [ ] **CHK021**: Is the "zero interpretive scores" criterion defined in a way that can be validated by a simple text scan of evidence? [Measurability, Spec §SC-004]
