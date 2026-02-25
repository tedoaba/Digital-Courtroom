# Feature Specification: Evidence Aggregation Sync Node (Layer 1.5)

**Feature Branch**: `007-evidence-aggregator`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Evidence Aggregation Sync Node (Layer 1.5): Act as a fan-in point to synchronize, deduplicate, and cross-reference all collected evidence before judgment. Included: evidence_aggregator.py, path validation. Excluded: Graph deployment. Dependencies: Feature 6."

## Clarifications

### Session 2026-02-25

- Q: Policy for missing detective sources? → A: Fail if repo or docs is missing; Warn for vision.
- Q: Handling of out-of-bound paths in documentation? → A: Sanitize and restrict to repository root; flag as Hallucinated Path.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Consolidate Detective Evidence (Priority: P1)

As the system orchestrator, I want to merge the parallel outputs of all detective agents into a single, unified source of truth so that the judges have a complete picture of the forensic data.

**Why this priority**: This is the fundamental "fan-in" requirement of the architecture. Without it, judges would operate on incomplete data, leading to incorrect verdicts.

**Independent Test**: Provide multiple mock evidence dictionaries from different sources (repo, docs, vision) and verify they are all present in the aggregated output with correct keys.

**Acceptance Scenarios**:

1. **Given** evidence from `repo` and `docs`, **When** the aggregator runs, **Then** the final state contains both `repo` and `docs` evidence keys.
2. **Given** multiple evidence items for the same source, **When** aggregated, **Then** all items are preserved without duplication if they are unique.

---

### User Story 2 - Cross-Reference File Paths (Priority: P1)

As a forensic validator, I want to verify if the file paths claimed in the documentation actually exist in the repository so that I can expose hallucinations in the project's documentation.

**Why this priority**: Documentation often claims features or files exist that aren't there. Highlighting these is a core requirement for "Forensic Accuracy" as defined in the project constitution.

**Independent Test**: Mock doc evidence claiming `src/auth.py` and repo evidence that does NOT contain `src/auth.py` in its file list. Verify a "Hallucinated Path" evidence item is created.

**Acceptance Scenarios**:

1. **Given** doc evidence citing `src/utils.py` and repo evidence confirming `src/utils.py` exists, **When** cross-referenced, **Then** no hallucination is flagged for this path.
2. **Given** doc evidence citing `non-existent.py` and repo evidence that doesn't mention it, **When** cross-referenced, **Then** an `Evidence` object with `evidence_class="DOCUMENT_CLAIM"` and `found=False` (labeled "Hallucinated Path") is added to the state.

---

### User Story 3 - Missing Source Handling (Priority: P2)

As a system operator, I want the system to handle missing detective sources gracefully by logging errors rather than crashing, so that the judges can still process partial evidence.

**Why this priority**: Detective failures should not be silent, but they also shouldn't stop the entire pipeline (Constitution VII.5).

**Independent Test**: Run aggregation where the `repo` source is missing; verify an error is added to `state.errors` and the node completes execution.

**Acceptance Scenarios**:

1. **Given** `repo` or `docs` evidence is entirely missing, **When** aggregated, **Then** the node appends a descriptive error to `state.errors` and continues.
2. **Given** `vision` is missing, **When** aggregated, **Then** a warning is logged but no error is added to `state.errors`.

---

### Edge Cases

- **Empty Repo**: If the `RepoInvestigator` found no files (empty manifest), every path mentioned in docs SHOULD be flagged as hallucinated.
- **Multiple Hallucinations**: System MUST handle and report multiple missing files from a single doc analysis without stopping.
- **Path Normalization**: Handles different path formats (e.g., `./src/file.py` vs `src/file.py`) by normalizing to a standard relative path format before comparison. Case-sensitivity MUST match the target file system (default to Case-Sensitive for Linux-based CI/CD).
- **Directory vs File**: If documentation cites a path that exists in the repo but is a directory when a file was expected (or vice versa), it MUST be flagged as a `DOCUMENT_CLAIM` mismatch.
- **Failed Investigator Protocol**: If a file exists but the `RepoInvestigator` failed to analyze it due to an internal error, the aggregator MUST NOT flag it as hallucinated, but MUST include a warning in the `rationale`.
- **Malformed Input**: If input `evidences` is not a dict or lists are not `Evidence` objects, the node MUST log a FATAL level event and append a "CRITICAL_STATE_ERROR" to `state.errors`.
- **Circular References**: No risk here as it's a fan-in point, but must handle empty input dicts gracefully by failing fast or logging a fatal error.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST function as the primary fan-in synchronization point in the LangGraph, ensuring all parallel detective nodes (Repo, Doc, Vision) complete execution.
- **FR-002**: System MUST use the `merge_evidences` reducer pattern for the `evidences` field in the `AgentState` to merge dictionaries without data loss, aligning with Principle VI.1.
- **FR-003**: System MUST identify all file paths extracted by the `DocAnalyst` (from `location` or `content` fields) and cross-reference them against the actual file manifest discovered by the `RepoInvestigator`.
- **FR-004**: System MUST generate "Hallucinated Path" evidence entries with `evidence_id` format `docs_DOCUMENT_CLAIM_{hash}` (where hash is SHA-256 of the path) for any documentation claim that refers to a file not present in the repository.
- **FR-005**: System MUST NOT crash if detective sources are missing.
  - If `repo` or `docs` are missing (nil or key absent), it MUST append a descriptive `FORENSIC_SOURCE_MISSING` error to `state.errors` and set a `pipeline_integrity=FAILED` flag in metadata to prevent judges from issuing final verdicts.
- **FR-006**: System MUST deduplicate evidence items based on their unique identifiers (`evidence_id`). If duplicates exist within a source, it MUST preserve the first item and log a warning.
- **FR-007**: System MUST provide a "clean" evidence dictionary where:
  - Only valid Pydantic `Evidence` objects are present.
  - `docs` evidence items are annotated with `found: bool` based on repo manifest.
  - All paths are relative to repository root.
- **FR-008**: System MUST sanitize all file paths collected from documentation:
  - Reject any path with `..` that resolves outside the repo root.
  - Reject absolute paths (e.g., `/etc/passwd`).
  - Normalize to POSIX style (forward slashes).
  - Flag rejected paths as hallucinated with `rationale="SECURITY_VIOLATION: Path outside root"`.

### Key Entities

- **EvidenceAggregator**: The Python node (`evidence_aggregator.py`) implementing the fan-in logic.
- **Evidence**: The Pydantic model defined in `src/state.py` used to represent forensic findings.
- **AgentState**: The TypedDict representing the global graph state, specifically the `evidences` collection.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of file paths cited in documentation but missing from the repository are correctly flagged as "Hallucinated Path".
- **SC-002**: The aggregation process adds less than 50ms of overhead to the graph execution for datasets < 1000 items (verified via `timeit` in unit tests).
- **SC-003**: System correctly identifies and warns about 100% of missing detective sources in test suites.
- **SC-004**: 100% consolidation — No unique `evidence_id` produced by a detective is lost during the fan-in transition.
- **SC-005**: 100% of "Hallucinated Path" findings generate a `PROJECT_LIFECYCLE` log event at `WARNING` level with metadata containing the offending path.

## Non-Functional Requirements

- **NFR-001 (Security)**: Path validation MUST NOT perform disk I/O beyond checking existence in the provided `RepoInvestigator` manifest (Static Analysis Only, Principle XV.5).
- **NFR-002 (Observability)**: Every aggregation run MUST log a summary: `{"event": "aggregation_complete", "counts": {"repo": X, "docs": Y, "vision": Z}, "hallucinations": N}`.
