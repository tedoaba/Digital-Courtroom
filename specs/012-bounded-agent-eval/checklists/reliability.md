# Requirements Quality Checklist: Bounded-Concurrency Evaluation

**Purpose**: "Unit Tests for English" - Validating requirements quality, clarity, and completeness for the concurrency refactor.
**Created**: 2026-02-26
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [ ] CHK001 - Are all transient error codes (e.g., 429, 502, 503) that trigger retries explicitly documented? [Completeness, Spec §FR-002]
- [ ] CHK002 - Is the fallback behavior for "Permanent Failures" (max retries reached) defined with specific log and state mutation rules? [Completeness, Spec §Edge Cases]
- [ ] CHK003 - Are the exact environment variable names for all configuration parameters defined? [Completeness, Spec §FR-003, Gap]
- [ ] CHK004 - Does the spec define the requirement for semaphore release in all exit paths (success, error, timeout)? [Completeness, Gap]

## Requirement Clarity

- [ ] CHK005 - Is the "Global Concurrency Limit" quantified with an absolute default value and upper/lower bounds? [Clarity, Spec §FR-001]
- [ ] CHK006 - Is the "exponential backoff" algorithm defined clearly enough to distinguish between fixed, linear, and true exponential implementations? [Clarity, Spec §FR-002]
- [ ] CHK007 - Is the "Structured Batching" JSON contract/schema documented to ensure consistent LLM prompting? [Clarity, Spec §FR-005, Gap]

## Acceptance Criteria Quality

- [ ] CHK008 - Can the "Zero 429 Errors" success criterion be objectively measured across different provider tiers? [Measurability, Spec §SC-001]
- [ ] CHK009 - Is "Predictable Load" quantified with a specific polling frequency or audit window for measurement? [Measurability, Spec §SC-002]
- [ ] CHK010 - Are the "Queueing" and "Acquired" log message formats specified for automated monitoring? [Measurability, Spec §SC-003]

## Scenario & Edge Case Coverage

- [ ] CHK011 - Are recovery requirements specified for when a "Partial Success" batch contains invalid/corrupt data instead of just missing IDs? [Coverage, Spec §FR-005, Gap]
- [ ] CHK012 - Does the spec define the requirement for request timeouts to prevent semaphore deadlock from "Hung Requests"? [Coverage, Spec §Edge Cases]
- [ ] CHK013 - Are requirements defined for system behavior when the concurrency limit N is modified during an active job? [Coverage, Gap]

## Constraints & Dependencies

- [ ] CHK014 - Is there a requirement for identifying which LLM providers in the registry support structured output for batching? [Dependency, Spec §FR-004, Gap]
- [ ] CHK015 - Is the requirement for jitter in the backoff algorithm documented to prevent "thundering herd" scenarios? [Consistency, Spec §FR-002]
