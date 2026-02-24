# Feature Specification: Pydantic State Schema and Annotated Reducers

**Feature Branch**: `003-pydantic-state-schema`  
**Created**: 2026-02-24  
**Status**: Draft  
**Input**: User description: "Feature: Pydantic State Schema and Annotated Reducers - Objective: Implement strongly typed state models to govern the data flow through the LangGraph architecture. - Scope: Evidence, JudicialOpinion, CriterionResult, AuditReport models. AgentState TypedDict with merge_evidences and merge_criterion_results reducers. - Unit Test Expectations: confidence [0.0, 1.0], score [1, 5]."

## Clarifications

### Session 2026-02-24

- Q: What level of structured metadata is required for the JudicialOpinion entity? → A: Simple object (text + basic identifiers: `case_id`, `court_name`).
- Q: How should the system identify the source of a specific piece of evidence? → A: Generic Reference (string field for URL, page name, or paragraph ID).
- Q: What should be the resolution strategy if multiple updates for the same criterion_id occur? → A: Highest Confidence (Keep the version with the highest `relevance_confidence`).
- Q: Should the AuditReport schema include a derived global metrics field? → A: Single Global Score (a derived numeric average/rating).
- Q: Should the AgentState preserve a history of updates or only the "latest verified" state? → A: Snapshot only (Store only the current merged results).
- Q: How should the system handle duplicate evidence items when merging lists? → A: Content-based Deduplication (Identify and merge duplicates based on source + content).
- Q: What level of numeric precision should be maintained for the global audit score? → A: One decimal place (e.g., 4.2 / 5.0).
- Q: Should metadata fields like case_id and court_name be strictly mandatory? → A: Optional with defaults (e.g., defaults to "Unknown").
- Q: Should there be a limit on the number of evidence items stored in the state? → A: No hard limit (Allow the list to grow with all valid evidence).
- Q: How should the "Security Override" constraint be represented in the data models? → A: Dedicated Flag (An explicit boolean flag that triggers capping in the report/aggregator).
- Q: Should the data models strictly forbid additional fields not defined in the schema? → A: Forbid Extra (Raise error if extra fields are present).
- Q: Should the data models allow type coercion for incoming data? → A: Strict (Disallow coercion; data must exactly match the type hint).
- Q: How should the custom reducers handle structurally invalid data during a merge? → A: Fatal Exception (Stop the graph and raise a system error).
- Q: How should the AuditReport.global_score be calculated from individual criterion results? → A: Weighted Average (Applying Constitution XI weightings: Security capping + weighted categories).

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

1. **Given** an existing state with results for 'Criterion A', **When** a new update with results for 'Criterion B' is applied via `merge_criterion_results`, **Then** the state contains results for both 'Criterion A' and 'Criterion B'.
2. **Given** an existing dict of `evidences`, **When** a new dict is applied via `merge_evidences`, **Then** the unique items are merged into the lists.

---

### User Story 3 - Criterion Scoring Constraints (Priority: P1)

As a legal auditor, I want scores assigned to judicial criteria to be strictly within the 1-5 range so that the final audit report reflects the project's standardized rubric.

**Why this priority**: Standardization of scoring is critical for the audit's validity.

**Independent Test**: Can be tested by creating `CriterionResult` models with scores of 0, 3, and 6, verifying only the 3 is accepted.

**Acceptance Scenarios**:

1. **Given** a score of 6, **When** creating a `CriterionResult`, **Then** it fails validation.
2. **Given** a score of 1, **When** creating a `CriterionResult`, **Then** it passes validation.

### Edge Cases

- **Duplicate Keys in merge**: If two agents provide the same `criterion_id`, the system MUST retain the one with the higher confidence/quality metric to ensure the most reliable audit data is preserved.
- **Empty Evidence Lists**: How does `operator.add` handle an empty list? (Should preserve existing state).
- **Malformed Nested Data**: If an `Evidence` object inside a list is invalid, does the entire state update fail? (Yes, Pydantic should fail the outer validation).
- **Structural Failure in Reducer**: If a reducer receives a non-container type (e.g., string instead of list), it MUST raise a fatal exception to prevent state corruption.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST define a schema for `Evidence` with fields: `source_ref`, `content`, and `relevance_confidence`.
- **FR-002**: System MUST enforce confidence bounds of [0.0, 1.0].
- **FR-003**: System MUST define a schema for `JudicialOpinion` to hold the source text and basic identifiers including `case_id` and `court_name` (optional with defaults).
- **FR-004**: System MUST define a `CriterionResult` schema with fields: `criterion_id`, `numeric_score`, `reasoning`, and a `security_violation_found` boolean flag.
- **FR-005**: System MUST enforce score bounds of [1, 5].
- **FR-006**: System MUST define an `AuditReport` schema as an aggregation of `CriterionResult` entries, a comprehensive text summary, and a derived global audit score calculated using a weighted average (per Constitution XI) and rounded to one decimal place.
- **FR-007**: System MUST define a central `State` definition that maintains a snapshot of the most recent validated results.
- **FR-008**: System MUST implement a merge strategy for `evidences` (dict of lists) that performs SHA-256 content-based deduplication and raises a fatal exception if structural types are mismatched.
- **FR-009**: System MUST implement a merge strategy for `criterion_results` that resolves collisions by highest confidence and raises a fatal exception if structural types are mismatched.
- **FR-010**: System MUST ensure that all data passed between processing nodes is validated against defined schemas using strict enforcement (no extra fields allowed, no type coercion) to prevent malformed data propagation.

### Key Entities _(include if feature involves data)_

- **Evidence**: Represents a specific piece of information extracted from a source, with a confidence metric and a reference to its location.
- **JudicialOpinion**: The primary source document being audited, containing the text and case metadata.
- **CriterionResult**: The outcome of auditing a specific legal criterion (e.g., Transparency, Bias), including a check for security violations.
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
