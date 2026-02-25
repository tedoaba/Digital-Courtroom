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
2. **Given** doc evidence citing `non-existent.py` and repo evidence that doesn't mention it, **When** cross-referenced, **Then** an `Evidence` object with `evidence_class="REPORT_ACCURACY"` (or similar) and `found=False` (labeled "Hallucinated Path") is added to the states.

---

### User Story 3 - Missing Source Warning (Priority: P2)

As a system operator, I want to be warned if a detective agent fails to provide any evidence so that I can investigate potential failures in the parallel fan-out layer.

**Why this priority**: Detective failures should not be silent. Judges need to know if they are missing an entire category of evidence (e.g., Vision).

**Independent Test**: Run aggregation where the `vision` evidence key is completely missing or empty, and check for a warning log in the system.

**Acceptance Scenarios**:

1. **Given** `repo` and `docs` evidence but empty `vision`, **When** aggregated, **Then** a warning is logged stating that evidence from source 'vision' is missing.

---

### Edge Cases

- **Empty Repo**: If the `RepoInvestigator` found no files, every path mentioned in docs should be flagged as hallucinated.
- **Multiple Hallucinations**: System should handle and report multiple missing files from a single doc analysis without stopping.
- **Path Normalization**: Handles different path formats (e.g., `./src/file.py` vs `src/file.py`) during cross-referencing.
- **Circular References**: No risk here as it's a fan-in point, but must handle empty input dicts gracefully by failing fast or logging a fatal error.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST function as the primary fan-in synchronization point in the LangGraph, ensuring all parallel detective nodes (Repo, Doc, Vision) complete execution.
- **FR-002**: System MUST use the `operator.ior` reducer pattern for the `evidences` field in the `AgentState` to merge dictionaries without data loss.
- **FR-003**: System MUST identify all file paths extracted by the `DocAnalyst` and cross-reference them against the actual file manifest discovered by the `RepoInvestigator`.
- **FR-004**: System MUST generate "Hallucinated Path" evidence entries for any documentation claim that refers to a file not present in the repository.
- FR-005: System MUST fail execution with a fatal error if 'repo' or 'docs' evidence sources are entirely missing; MUST log a warning if 'vision' is missing but continue execution.
- **FR-006**: System MUST deduplicate evidence items based on their unique identifiers (`evidence_id`) if multiple detectives produce the same piece of evidence.
- **FR-007**: System MUST provide a "clean" evidence dictionary that is ready for consumption by Judge nodes, ensuring all cross-references are annotated.
- **FR-008**: System MUST sanitize all file paths collected from documentation and reject any that resolve outside the repository root, flagging them as "Hallucinated Path".

### Key Entities

- **EvidenceAggregator**: The Python node (`evidence_aggregator.py`) implementing the fan-in logic.
- **Evidence**: The Pydantic model defined in `src/state.py` used to represent forensic findings.
- **AgentState**: The TypedDict representing the global graph state, specifically the `evidences` collection.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of file paths cited in documentation but missing from the repository are correctly flagged as "Hallucinated Path".
- **SC-002**: The aggregation process adds less than 50ms of overhead to the graph execution (focusing on dictionary merging and string matching).
- **SC-003**: System correctly identifies and warns about 100% of missing detective sources in test suites.
- **SC-004**: 100% consolidation — No evidence item produced by a detective is lost during the fan-in transition.
