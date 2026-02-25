# Feature Specification: ContextBuilder Initialization Node

**Feature Branch**: `005-context-builder-init`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Build the initial graph node responsible for bootstrapping execution state and asserting preconditions. Validates inputs fast, sets up the initial execution space, and reads the definitive evaluation rulebook (rubric JSON) centrally."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Successful Audit Initialization (Priority: P1)

As an auditor, I want to provide a repository URL and a PDF report path so that the system can load the evaluation rubric and prepare for forensic analysis.

**Why this priority**: Without initialization, the graph cannot execute. This is the entry point for all audits.

**Independent Test**: Can be tested by invoking the `ContextBuilder` node with valid inputs and verifying that the returned state contains the loaded rubric dimensions and validated paths.

**Acceptance Scenarios**:

1.  **Given** a valid GitHub repository URL and a valid path to an existing PDF report, **When** the `ContextBuilder` node is executed, **Then** it should return a state object containing all 10 rubric dimensions from `rubric/week2_rubric.json`.
2.  **Given** valid inputs, **When** the node starts, **Then** it should log a `context_builder_entry` event and upon completion a `context_builder_exit` event using the `StructuredLogger`.

---

### User Story 2 - Input Validation Fast-Fail (Priority: P2)

As a system operator, I want the auditor to fail immediately if the inputs are malformed, protecting downstream agents from wasting resources on invalid targets.

**Why this priority**: Prevents resource waste and provides immediate feedback on configuration errors.

**Independent Test**: Can be tested by passing invalid URL formats (e.g., `not-a-url`, `file:///etc/passwd`, `localhost`) or non-existent file paths and verifying that an exception is raised before any other tasks are performed.

**Acceptance Scenarios**:

1. **Given** an invalid URL format or a security-risk URL (localhost/file scheme), **When** the `ContextBuilder` node is executed, **Then** it should raise an `Invalid URL format` error and append a descriptive failure message to the `errors` state.
2. **Given** a non-existent `pdf_path`, **When** the node is executed, **Then** it should raise a `Missing rubric file or PDF` error.

---

### User Story 3 - Dynamic Rubric Configuration (Priority: P3)

As a developer, I want to be able to specify which rubric file to use so that I can audit different project types without hardcoding paths.

**Why this priority**: Essential for maintainability and multi-week progression.

**Independent Test**: Can be tested by configuring a custom rubric path via environment variables or configuration settings and verifying the node loads the correct file.

**Acceptance Scenarios**:

1. **Given** a configured path to a valid JSON rubric, **When** the node starts, **Then** it should load the specific rubric version and log the loaded dimension count.

---

### Edge Cases

- **Malformed Rubric JSON**: How does the system handle a `rubric.json` that is not valid JSON?
  - _Response_: Node must catch `json.JSONDecodeError`, log a critical error, and fail the audit immediately.
- **Empty Rubric Case**: What if the rubric file is valid JSON but empty or missing required keys?
  - _Response_: Node must validate the presence of the `dimensions` key and fail if it's missing.
- **URL Injection**: What if the URL contains shell metacharacters?
  - _Response_: Strict regex validation must reject any URL not matching the GitHub HTTPS pattern.

## Clarifications

### Session 2026-02-25

- Q: How is the rubric path configured? → A: Passed via State Input (e.g., in the `AgentState`).
- Q: What is the failure behavior for validation errors? → A: Append to `errors` list and return (Allows routing to `ErrorHandler`).
- Q: Which rubric dimensions should be loaded? → A: Load all dimensions found in the rubric.
- Q: Should synthesis rules be loaded by this node? → A: Load both `dimensions` and `synthesis_rules` from the rubric JSON.
- Q: Should state fields be initialized to empty structures? → A: Initialize `evidences`, `opinions`, and `criterion_results` as empty structures.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The node MUST load the rubric from a path provided in the `AgentState` (defaulting to `rubric/week2_rubric.json` if not provided).
- **FR-002**: The node MUST validate that `repo_url` matches the pattern `^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$`.
- **FR-003**: The node MUST reject URLs containing `localhost`, `127.0.0.1`, or the `file://` protocol.
- **FR-004**: The node MUST verify the existence of the PDF report at `pdf_path` using `os.path.exists()`.
- **FR-005**: The node MUST parse the rubric JSON and extract both the `dimensions` array and the `synthesis_rules` dictionary into the corresponding state fields (`rubric_dimensions` and `synthesis_rules`).
- **FR-006**: The node MUST log `context_builder_entry` and `context_builder_exit` events with the `StructuredLogger`. The entry log MUST include the rubric version and dimension count in the payload.
- **FR-007**: The node MUST fail gracefully on validation errors by appending a descriptive error message to the `errors` state list and returning the current state, allowing upstream routing to handle the failure.
- **FR-008**: The node MUST use the `rubric_path` field from the initial state to determine which rulebook to load.
- **FR-009**: The node MUST initialize `evidences` (dict), `opinions` (list), and `criterion_results` (dict) as empty structures if they are missing from the state, ensuring downstream reducers operate on valid collections.

### Key Entities _(include if feature involves data)_

- **Rubric**: The definitive evaluation rulebook (JSON) containing dimensions, instructions, and synthesis rules.
- **AgentState**: The shared graph state, which the `ContextBuilder` initializes with inputs and dimensions.
- **EvidenceClass**: Enumeration of forensic categories loaded from the rubric.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of tested valid inputs result in a populated `rubric_dimensions` list in under 500ms.
- **SC-002**: 100% of invalid URLs or missing files are caught at the `ContextBuilder` node, preventing execution of detective nodes.
- **SC-003**: The `rubric_dimensions` list in state perfectly matches the content of the configured JSON file.
- **SC-004**: All node activities are recorded in JSON logs with a correct `correlation_id` and `event_type`.
