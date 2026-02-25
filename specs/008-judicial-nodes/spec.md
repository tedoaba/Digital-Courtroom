# Feature Specification: Dialectical Judicial Agents (Layer 2)

**Feature Branch**: `008-judicial-nodes`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Implement three distinct persona-based LLM nodes (Prosecutor, Defense, TechLead) to interpret evidence objectively based on character philosophies."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Multi-Perspective Adversarial Review (Priority: P1)

As the Digital Courtroom system, I want to have three distinct judicial personas evaluate the same evidence for each rubric criterion so that I can ensure a balanced and adversarial review process.

**Why this priority**: This is the core of the "Digital Courtroom" concept. Without distinct, adversarial personas, the system becomes a single-point-of-failure "vibe coder" instead of a robust governance tool.

**Independent Test**: Can be tested by feeding a mock evidence payload and a single rubric criterion to all three judges and verifying that they produce distinct `JudicialOpinion` objects with different reasoning and scores.

**Acceptance Scenarios**:

1. **Given** a validated set of evidence and a rubric dimension, **When** the judicial layer is executed, **Then** three independent opinions are generated for that dimension.
2. **Given** a rubric dimension, **When** comparing the `Prosecutor` and `Defense` arguments, **Then** they must demonstrate opposing philosophical lenses (Critical vs. Optimistic).

---

### User Story 2 - Structured Judicial Feedback (Priority: P2)

As a user/trainee, I want the judges to provide structured feedback citing specific evidence IDs so that I can understand exactly which parts of my code or report led to their scores.

**Why this priority**: Actionable feedback is a primary goal of the system. Citations ensure the feedback is grounded in facts rather than hallucinations.

**Independent Test**: Verify that the `cited_evidence` field in the `JudicialOpinion` contains IDs that actually exist in the input `evidences` dictionary.

**Acceptance Scenarios**:

1. **Given** a judge opinion, **When** inspecting the `cited_evidence` list, **Then** all IDs must match existing `evidence_id` values from the detective layer.
2. **Given** an opinion, **When** checking the `argument` field, **Then** it must exceed 20 characters and contain rational justification.

---

### User Story 3 - Resilient Execution (Priority: P3)

As a system operator, I want the judicial nodes to handle LLM schema violations and timeouts gracefully so that the audit process does not halt abruptly due to transient errors.

**Why this priority**: LLMs are non-deterministic. Ensuring the pipeline completes even after minor parsing failures is critical for production stability.

**Independent Test**: Mock the LLM to return invalid JSON once, then valid JSON on retry, and verify the node successfully captures the output after the retry.

**Acceptance Scenarios**:

1. **Given** an LLM "schema violation" (unstructured text), **When** the node receives it, **Then** it retries up to 2 times before falling back to a neutral error state.
2. **Given** an HTTP timeout, **When** calling the LLM, **Then** the system applies exponential backoff before failing.

---

### Edge Cases

- **Hallucinated Citations**: A judge cites an `evidence_id` that doesn't exist. The system must be able to flag this in the synthesis layer (Layer 3).
- **Persona Collusion**: LLM prompts are too similar, causing judges to return identical text. FR-002 addresses this by enforcing < 10% overlap.
- **Empty Evidence**: No evidence was found by detectives. Judges must still render an opinion (likely a low score) based on the _absence_ of evidence.
- **Schema Exhaustion**: LLM fails to return valid schema even after 2 retries.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST construct three distinct system prompts for `Prosecutor`, `Defense`, and `TechLead` personas.
- **FR-002**: Persona-specific philosophical instructions MUST share less than 10% text overlap natively.
- **FR-003**: The `Prosecutor` node MUST apply a "Critical Lens" (Philosophy: "Trust No One. Assume Vibe Coding.").
- **FR-004**: The `Defense` node MUST apply an "Optimistic Lens" (Philosophy: "Reward Effort and Intent.").
- **FR-005**: The `TechLead` node MUST apply a "Pragmatic Lens" (Philosophy: "Does it work? Is it maintainable?").
- **FR-006**: All judicial nodes MUST utilize `.with_structured_output(JudicialOpinion)` for LLM interaction.
- **FR-007**: System MUST implement a fallback mechanism for schema validation errors with a maximum of 2 retries.
- **FR-008**: System MUST apply exponential backoff for HTTP timeouts during LLM calls.
- **FR-009**: All judicial LLM calls MUST be constrained to `temperature=0` via `config.py`.
- **FR-010**: Every generated `JudicialOpinion` MUST cite specific `evidence_id` values as justification.

### Key Entities _(include if feature involves data)_

- **JudicialOpinion**: A Pydantic model representing a single judge's verdict on a single criterion.
  - `judge`: "Prosecutor", "Defense", or "TechLead".
  - `criterion_id`: ID from the rubric.
  - `score`: Integer (1-5).
  - `argument`: Detailed reasoning text.
  - `cited_evidence`: List of `evidence_id` strings.
- **AgentState**: The shared LangGraph state containing the `opinions` list (accumulated via `operator.add`).

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of judicial nodes return valid objects adhering to the `JudicialOpinion` schema after at most 2 retries.
- **SC-002**: Prompt similarity analysis shows < 10% overlap between the distinctive philosophy sections of the three judges.
- **SC-003**: Audit execution continues without halting even if one judge node fails after 2 retries (returns a "neutral" fallback opinion).
- **SC-004**: All cited `evidence_id` values in opinions are verifiable against the input `evidences` set.
- **SC-005**: All LLM calls for judicial evaluations are verified to have been made with `temperature=0`.

## Assumptions

- The detective agents in Layer 1 have already populated the `evidences` dictionary in the state.
- The `EvidenceAggregator` (Layer 1.5) has synchronized and simplified the evidence for judicial consumption.
- LLM model configurations (Gemini Pro / GPT-4o) are managed by a centralized `config.py`.
