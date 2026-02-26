# Feature Specification: Operation Ironclad Swarm — Production-Grade Hardening

**Feature Branch**: `013-ironclad-hardening`  
**Created**: 2026-02-26  
**Status**: Draft  
**Input**: User description: "Operation Ironclad Swarm — Production-Grade Hardening"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Hardened Execution & Configuration (Priority: P1)

As a System Administrator, I want the Digital Courtroom to operate in a fully hardened environment with zero hardcoded configuration and secure tool execution, so that the system is production-ready and resistant to injection or data leakage.

**Why this priority**: Correct configuration and secure execution are foundational for production stability and security.

**Independent Test**: Verify that the system fails to start without a complete environment configuration and that all tool calls are executed within resource-constrained sandboxes.

**Acceptance Scenarios**:

1. **Given** a new environment without hardcoded strings, **When** the swarm is initialized, **Then** it correctly loads all model names, endpoints, and timeouts from environment variables.
2. **Given** a detective agent executing a tool, **When** the tool call is triggered, **Then** it runs in a sandboxed directory with restricted resource usage and sanitized input/output.
3. **Given** a Tool with sensitive credentials, **When** it is invoked, **Then** it retrieves secrets from a local encrypted store (using `.env` with decryption) rather than local plain files or variables.

---

### User Story 2 - Real-time Swarm Observability (Priority: P1)

As a Forensic Auditor, I want a real-time dashboard and deep execution tracing, so that I can visualize node status tracking and debug complex swarm interactions.

**Why this priority**: Visibility is critical for a "Digital Courtroom" where reasoning paths must be transparent and auditable.

**Independent Test**: Start the swarm and verify that node transitions appear in the dashboard in real-time and that the tracing system captures 100% of graph node executions.

**Acceptance Scenarios**:

1. **Given** an active swarm execution, **When** a node begins processing, **Then** a CLI/TUI dashboard (using `rich` or similar) updates its status to "Processing" with live performance metrics.
2. **Given** any graph node, **When** it completes execution, **Then** a full trace is exported to the centralized tracing system with structured JSON audit trails of all tool calls.

---

### User Story 3 - Report Integrity & Graph Resilience (Priority: P2)

As a Legal Stakeholder, I want the evidence to be cryptographically linked to the final verdict and the system to be resilient to external API failures, so that the final report is verifiable and the process is robust against outages.

**Why this priority**: Integrity ensures the "Forensic" nature of the system, while resilience ensures business continuity.

**Independent Test**: Tamper with an evidence file and verify the cryptographic check fails. Simulate an API timeout and verify the circuit breaker opens and triggers a state rollback.

**Acceptance Scenarios**:

1. **Given** a set of collected evidence, **When** the report is generated, **Then** each piece of evidence is part of a sequential hash chain linked to the final hash.
2. **Given** a failing external API, **When** the failure threshold is met, **Then** a circuit breaker mechanism halts further calls and initiates an automated rollback to the last valid state.

---

### User Story 4 - Judicial Dialectics Abstraction (Priority: P2)

As a Developer, I want a dedicated abstraction layer for reasoning strategies and multi-factorial scoring rubrics, so that reasoning logic is clearly separated from orchestration.

**Why this priority**: Improves maintainability and allows for more complex, nuanced reasoning strategies.

**Independent Test**: Implement a new reasoning strategy within the judicial layer and verify it can be swapped without modifying the core graph nodes.

**Acceptance Scenarios**:

1. **Given** the judicial layer, **When** a judge evaluates a criterion, **Then** it uses a multi-factorial scoring rubric defined in the abstraction layer rather than ad-hoc logic.
2. **Given** conflicting judge opinions, **When** the synthesis occurs, **Then** the reasoning strategies used are extracted from the judicial layer for the dissent summary.

### Edge Cases

- **Hallucinated Evidences**: If a detective claims evidence exists but the cryptographic chain indicates tampering or missing data.
- **Cascading API Failure**: If the circuit breaker opens for a core service, the system must trigger a "Descent into Safe Mode" and generate a partial report rather than crashing.
- **Vault Unavailability**: If the secure storage is unreachable, the system must halt and log a high-priority security alert.

## Clarifications

### Session 2026-02-26

- Q: What are the concrete resource limits for the detective sandboxes to ensure they are truly "constrained"? → A: Fixed strict limits (e.g., 512MB RAM, 1 CPU core)
- Q: Which encryption algorithm should be used for the "local encrypted store"? → A: AES-256 (with environment-stored key)
- Q: What should be the default thresholds for the "Circuit Breaker"? → A: 3 failures / 30s reset window
- Q: Which hashing algorithm should be used for the "sequential hash chain"? → A: SHA-256
- Q: How frequently should the CLI/TUI dashboard refresh? → A: Real-time / 1s polling

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST migrate all remaining hardcoded strings (model names, API endpoints, timeouts) to external environment configuration.
- **FR-002**: System MUST implement a secure credential management system (AES-256 local encrypted store) for all tool secrets.
- **FR-003**: System MUST enforce input/output validation and sanitization for all external tool calls.
- **FR-004**: Detectives MUST operate in resource-constrained sandboxes with fixed strict limits (512MB RAM, 1 CPU core).
- **FR-005**: All graph nodes MUST be instrumented for 100% trace coverage in a centralized tracing system.
- **FR-006**: System MUST implement a real-time visualization dashboard (1s refresh) tracking node health and performance.
- **FR-007**: System MUST implement SHA-256 sequential cryptographic validation chains for all evidence.
- **FR-008**: System MUST implement circuit breaker patterns for all external API dependencies with a default threshold of 3 failures and a 30s reset window.
- **FR-009**: System MUST support automated rollback testing for state recovery during orchestration crashes.
- **FR-010**: System MUST implement a dedicated 'judicial layer' abstraction to separate reasoning strategies from graph nodes.
- **FR-011**: System MUST implement cascading failure detection that halts processing when core evidence streams (e.g., RepoInvestigator) fail.

### Key Entities _(include if feature involves data)_

- **HardenedConfig**: The data structure managing environment and secure storage parameters.
- **SandboxEnvironment**: The ephemeral, constrained execution space for tools with fixed resource limits.
- **TraceAuditTrail**: The structured JSON logs exported to the tracing system.
- **CryptographicChain**: The set of hashes linking raw evidence to the final verdict.
- **CircuitBreakerState**: The status (Closed, Open, Half-Open) of external integrations.
- **JudicialLayer**: The abstraction containing reasoning strategies and scoring rubrics.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of hardcoded configuration strings are removed and moved to external configuration.
- **SC-002**: 100% graph node coverage in execution traces.
- **SC-003**: Tool executions in sandboxes show 0% leakage to the host file system outside allowed ephemeral storage and do not exceed 512MB RAM / 1 CPU.
- **SC-004**: Circuit breaker successfully opens within exactly 3 consecutive failures of an external API.
- **SC-005**: Cryptographic validation using SHA-256 detects 100% of manual tampering attempts in the evidence store.
- **SC-006**: Execution recovery from a simulated orchestration crash completes in under 10 seconds.
- **SC-007**: Zero mock components remain in the production execution path.
