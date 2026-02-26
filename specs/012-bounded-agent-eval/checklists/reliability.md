# Requirements Quality Checklist: Bounded-Concurrency Evaluation

**Purpose**: "Unit Tests for English" - Validating requirements quality, clarity, and completeness for the concurrency refactor.
**Created**: 2026-02-26
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 - Are all transient error codes (e.g., 429, 502, 503) that trigger retries explicitly documented? [Completeness, Spec §FR-002] — _Resolved: FR-002 now lists 429, 502, 503, 408._
- [x] CHK002 - Is the fallback behavior for "Permanent Failures" (max retries reached) defined with specific log and state mutation rules? [Completeness, Spec §Edge Cases] — _Resolved: Edge Cases §Persistent Failures now specifies ERROR log, score=None opinion, state.errors append._
- [x] CHK003 - Are the exact environment variable names for all configuration parameters defined? [Completeness, Spec §FR-003, Gap] — _Resolved: FR-003 now lists all 6 env vars with types and defaults._
- [x] CHK004 - Does the spec define the requirement for semaphore release in all exit paths (success, error, timeout)? [Completeness, Gap] — _Resolved: FR-007 mandates release via async with or try/finally._

## Requirement Clarity

- [x] CHK005 - Is the "Global Concurrency Limit" quantified with an absolute default value and upper/lower bounds? [Clarity, Spec §FR-001] — _Resolved: FR-001 now specifies default=5, valid range 1–50._
- [x] CHK006 - Is the "exponential backoff" algorithm defined clearly enough to distinguish between fixed, linear, and true exponential implementations? [Clarity, Spec §FR-002] — _Resolved: FR-002 now includes the exact formula with multiplier, jitter range, and max._
- [x] CHK007 - Is the "Structured Batching" JSON contract/schema documented to ensure consistent LLM prompting? [Clarity, Spec §FR-005, Gap] — _Resolved: FR-005 now references data-model.md § Batching Contract._

## Acceptance Criteria Quality

- [x] CHK008 - Can the "Zero 429 Errors" success criterion be objectively measured across different provider tiers? [Measurability, Spec §SC-001] — _Resolved: SC-001 now specifies log parsing methodology._
- [x] CHK009 - Is "Predictable Load" quantified with a specific polling frequency or audit window for measurement? [Measurability, Spec §SC-002] — _Resolved: SC-002 now defines acquired-minus-released delta measurement._
- [x] CHK010 - Are the "Queueing" and "Acquired" log message formats specified for automated monitoring? [Measurability, Spec §SC-003] — _Resolved: SC-003 now defines 5 structured JSON event formats._

## Scenario & Edge Case Coverage

- [x] CHK011 - Are recovery requirements specified for when a "Partial Success" batch contains invalid/corrupt data instead of just missing IDs? [Coverage, Spec §FR-005, Gap] — _Resolved: FR-005 and Edge Cases §Corrupt Batch Response now cover malformed entries._
- [x] CHK012 - Does the spec define the requirement for request timeouts to prevent semaphore deadlock from "Hung Requests"? [Coverage, Spec §Edge Cases] — _Resolved: FR-008 and Edge Cases §Hung Requests define asyncio.wait_for with LLM_CALL_TIMEOUT._
- [x] CHK013 - Are requirements defined for system behavior when the concurrency limit N is modified during an active job? [Coverage, Gap] — _Resolved: FR-009 defines immutable-during-job policy._

## Constraints & Dependencies

- [x] CHK014 - Is there a requirement for identifying which LLM providers in the registry support structured output for batching? [Dependency, Spec §FR-004, Gap] — _Resolved: FR-004 now specifies fallback to individual calls for non-structured-output providers._
- [x] CHK015 - Is the requirement for jitter in the backoff algorithm documented to prevent "thundering herd" scenarios? [Consistency, Spec §FR-002] — _Resolved: FR-002 now specifies jitter as random value in [0, 0.5s] with explicit thundering-herd rationale._
