# Feature Specification: Pydantic State Schema and Annotated Reducers

**Feature Branch**: `003-pydantic-state-schema`  
**Created**: 2026-02-24  
**Status**: Draft  
**Input**: User description: "Feature: Pydantic State Schema and Annotated Reducers - Objective: Implement strongly typed state models to govern the data flow through the LangGraph architecture. - Scope: Evidence, JudicialOpinion, CriterionResult, AuditReport models. AgentState TypedDict with operator.add and operator.ior reducers. - Unit Test Expectations: confidence [0.0, 1.0], score [1, 5]."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Evidence Validation (Priority: P1)

As a system developer, I want all collected evidence to be validated against a strict schema so that downstream agents never process malformed or out-of-bounds data.

**Why this priority**: Foundational data integrity is required for the entire graph execution. Incorrect confidence scores would lead to invalid judicial reasoning.

**Independent Test**: Can be tested by instantiating an `Evidence` model with various confidence scores (valid and invalid) and verifying Pydantic enforcement.

**Acceptance Scenarios**:

1. **Given** a confidence score of 1.5, **When** creating an `Evidence` model, **Then** a `ValidationError` is raised.
2. **Given** a confidence score of 0.8, **When** creating an `Evidence` model, **Then** the model is successfully created.

---

### User Story 2 - Parallel State Merging (Priority: P1)

As a system engineer, I want state updates from parallel agents to merge correctly using reducers so that data from multiple audit criteria is aggregated without overwriting.

**Why this priority**: LangGraph's fan-in/fan-out capabilities rely on these reducers to combine results from multiple nodes.

**Independent Test**: Can be tested by manually invoking the `ior` and `add` reducers on sample state dictionaries and verifying the merged output matches expectations.

**Acceptance Scenarios**:

1. **Given** an existing state with results for 'Criterion A', **When** a new update with results for 'Criterion B' is applied via `ior`, **Then** the state contains results for both 'Criterion A' and 'Criterion B'.
2. **Given** an existing list of `Evidence`, **When** a new list is applied via `add`, **Then** the lists are concatenated.

---

### User Story 3 - Criterion Scoring Constraints (Priority: P1)

As a legal auditor, I want scores assigned to judicial criteria to be strictly within the 1-5 range so that the final audit report reflects the project's standardized rubric.

**Why this priority**: Standardization of scoring is critical for the audit's validity.

**Independent Test**: Can be tested by creating `CriterionResult` models with scores of 0, 3, and 6, verifying only the 3 is accepted.

**Acceptance Scenarios**:

1. **Given** a score of 6, **When** creating a `CriterionResult`, **Then** it fails validation.
2. **Given** a score of 1, **When** creating a `CriterionResult`, **Then** it passes validation.

### Edge Cases

- **Duplicate Keys in ior merge**: How does the system handle two agents providing the same key in a dictionary? (Default: later update wins if keys collide, but reducers should be used to prevent loss if needed).
- **Empty Evidence Lists**: How does `operator.add` handle an empty list? (Should preserve existing state).
- **Malformed Nested Data**: If an `Evidence` object inside a list is invalid, does the entire state update fail? (Yes, Pydantic should fail the outer validation).

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST define a schema for `Evidence` with fields: `source_url`, `content`, and `relevance_confidence`.
- **FR-002**: System MUST enforce confidence bounds of [0.0, 1.0].
- **FR-003**: System MUST define a schema for `JudicialOpinion` to hold the source text and metadata.
- **FR-004**: System MUST define a `CriterionResult` schema with fields: `criterion_id`, `numeric_score`, and `reasoning`.
- **FR-005**: System MUST enforce score bounds of [1, 5].
- **FR-006**: System MUST define an `AuditReport` schema as an aggregation of `CriterionResult` entries and a summary.
- **FR-007**: System MUST define a central `State` definition in the state management module.
- **FR-008**: System MUST implement an additive merge strategy for evidence collections (new items appended to existing).
- **FR-009**: System MUST implement an inclusive-OR merge strategy for criterion results (dictionary-style merge where entries for different criteria are combined).
- **FR-010**: System MUST ensure that all data passed between processing nodes is validated against defined schemas to prevent malformed data propagation.

### Key Entities _(include if feature involves data)_

- **Evidence**: Represents a specific piece of information extracted from a source, with a confidence metric.
- **JudicialOpinion**: The primary source document being audited.
- **CriterionResult**: The outcome of auditing a specific legal criterion (e.g., Transparency, Bias).
- **AuditReport**: The final aggregated output of the judicial audit process.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of inter-node data models are covered by automated schema validation.
- **SC-002**: No unstructured data types are used for complex state transitions.
- **SC-003**: Schema validation failures provide the specific data path to the invalid constraint.
- **SC-004**: Parallel updates to the state results result in a complete set containing all uniquely identified criterion results.

## Assumptions & Dependencies

- **Dependency**: Relies on Feature 2 (Observability) for logging validation errors.
- **Assumption**: `JudicialOpinion` will be provided as a string or a structured object containing at least the text of the opinion.
- **Assumption**: `AgentState` will be the primary state object used in `LangGraph` `StateGraph` definitions.
