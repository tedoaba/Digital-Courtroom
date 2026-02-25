# Feature Specification: Parallel Detective Agents (Layer 1)

**Feature Branch**: `006-parallel-detectives`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Feature: Parallel Detective Agents (Layer 1)..."

## Clarifications

### Session 2026-02-25

- Q: What is the maximum allowed execution time (timeout) for a single detective node before it must truncate and return `found=False`? → A: 60 seconds (Standard, matches architectural notes).
- Q: Beyond the classification string, should the `VisionInspector` also include a brief textual description of the flow captured in the diagram? → A: Yes, include classification and structural description (matches architecture notes).
- Q: What specific metrics must each detective node log upon completion to satisfy the requirement for high observability? → A: Operation duration and artifact count (files/pages/images).
- Q: How should `rubric_dimensions` be handled by detectives? → A: Detectives MUST only process dimensions matching their source (e.g., `RepoInvestigator` filters for `source == "repo"`).
- Q: What specific git history is required for forensics? → A: The last 50 commits using `git log --oneline --reverse`.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Run RepoInvestigator on a Repository (Priority: P1)

The system needs to instantiate a `RepoInvestigator` that can clone a targeted Git repository into a sandboxed environment, read its commit history, and parse its Python AST to extract evidence of specific patterns like classes or imports.

**Why this priority**: It is the core requirement for collecting factual evidence from the source code, which is completely isolated from LLM opinion and provides the foundation for Git and State Management forensic evaluation.

**Independent Test**: Can be tested by invoking the `RepoInvestigator` with a valid rubric JSON and standard repository URL, verifying it yields raw `Evidence` objects containing strictly facts about the repository's code and git log.

**Acceptance Scenarios**:

1. **Given** a valid GitHub repository URL and rubric dimensions for `github_repo`, **When** the `RepoInvestigator` executes its node logic, **Then** it produces a dictionary containing a list of `Evidence` objects detailing AST structure and commit history without crashing.
2. **Given** a failed git clone (e.g., authentication error or invalid URL), **When** the `RepoInvestigator` executes, **Then** it gracefully returns an `Evidence` item with `found=False` and appends an error to the logs rather than failing the execution pipe.

---

### User Story 2 - Run DocAnalyst on a PDF Report (Priority: P1)

The system needs to instantiate a `DocAnalyst` that can parse a locally provided PDF report to extract text chunks, look for specific architecture keywords, and extract claimed file paths to be cross-referenced later.

**Why this priority**: Document verification is a critical component of the audit, ensuring that theoretical claims in the report match empirical evidence.

**Independent Test**: Can be independently tested by providing a standard PDF and `pdf_report` rubric dimensions, validating that the parsed chunks create factual `Evidence` objects of found text.

**Acceptance Scenarios**:

1. **Given** a valid local PDF file path, **When** the `DocAnalyst` node executes, **Then** it extracts the text and returns `Evidence` objects detailing the presence of key architectural terms and cited file paths.
2. **Given** an unparseable, non-existent, or password-protected PDF file, **When** the `DocAnalyst` executes, **Then** it logs the failure and safely returns an `Evidence` object with `found=False` allowing the evaluation pipeline to continue gracefully.

---

### User Story 3 - Run VisionInspector to classify Extracted Diagram Images (Priority: P2)

The system needs to instantiate a `VisionInspector` node capable of taking extracted architectural diagrams from a PDF and sending them to a multimodal LLM to classify if they represent proper parallel execution flows.

**Why this priority**: While valuable for detecting misleading sequence diagrams, visual classification relies on an external multimodal LLM which makes it secondary compared to direct code analysis. Implementation is required but execution is optional.

**Independent Test**: Can be tested by mocking an LLM and providing simulated extracted images, validating it creates an `Evidence` object identifying if the diagram represents parallel or linear flows.

**Acceptance Scenarios**:

1. **Given** a set of images extracted from the report, **When** the `VisionInspector` processes them via an LLM, **Then** it successfully parses the LLM output into an `Evidence` object specifying the diagram type.
2. **Given** an LLM timeout or an API configuration error, **When** the `VisionInspector` executes, **Then** it logs the exception and returns an `Evidence` object with `found=False`.

---

### Edge Cases

- **Timeout on Large Repositories**: If a code repository is extremely large and times out during clone or AST parsing (>60 seconds), the node MUST truncate operations and return `found=False` with a timeout rationale.
- **Empty Repositories**: If the Git clone results in an empty directory, `RepoInvestigator` returns `found=False` with rationale "Repository contains no detectable code files".
- **Corrupt Documents**: How does the system handle corrupt PDF documents that crash the parser? (Handled via catch-all exception and `found=False`).
- **Protected PDFs**: Password-protected PDFs are treated as unparseable; node returns `found=False` with rationale "Document encrypted/protected".
- **LLM Rate Limits**: What happens if the multimodal LLM rate limits requests during Vision Inspector execution? (Handled via retry logic and fallback to `found=False`).
- **Comprehensive Failure**: If all detectives fail comprehensively, they return failure items, allowing the pipeline to proceed to the aggregator which flags the absence of evidence.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST implement three separate python functions/nodes: `RepoInvestigator`, `DocAnalyst`, and `VisionInspector` in `src/nodes/detectives.py`.
- **FR-002**: Each detective MUST strictly produce outputs as immutable `Evidence` schemas containing factual data without scoring or incorporating opinionated judgments. Forbidden language includes interpretive adjectives (e.g., "cleanly implemented", "poorly structured") or numeric grades.
- **FR-003**: The `RepoInvestigator` MUST utilize AST parsing and safe subprocess calls (e.g. `tempfile` isolation, no `shell=True`) to perform code forensics safely. `DocAnalyst` MUST use Docling for structural extraction via sandboxed libraries.
- **FR-004**: System MUST ensure that any specific failure within a detective (e.g. timeout, unparseable file) does not crash the application.
- **FR-005**: In the event of an anticipated failure, the failing node MUST log an error and return an `Evidence` object where `found=False`.
- **FR-006**: Code within `detectives.py` MUST solely handle forensic collection, and MUST exclude synchronization logic (which is handled by `EvidenceAggregator`).
- **FR-007**: The system MUST implement dependency abstractions for the detectives to allow full unit testability via mocks of LLMs, GitHub APIs, and local PDF files.
- **FR-008**: The detectives MUST enforce a hard timeout of 60 seconds for all external operations (cloning, parsing, LLM calls).
- **FR-009**: Each detective node MUST log structured observability metrics upon completion, specifically operation duration and the count of processed artifacts (files, pages, or images).
- **FR-010**: The `RepoInvestigator` MUST include "Tool Safety" forensics, specifically searching for prohibited calls like `os.system()` or `eval()` in the target repository's code.
- **FR-011**: All LLM-backed detective operations MUST use `temperature=0` to ensure forensic determinism.
- **FR-012**: Detective nodes MUST implement the filter logic to only process `rubric_dimensions` where the `dimension["source"]` strictly matches the detective's assigned source (e.g., "repo", "docs", or "vision").
- **FR-013**: The system MUST support LangSmith tracing for all detective node executions for auditability.

### Key Entities

- **Evidence**: A strictly typed data structure capturing raw facts. For `VisionInspector`, this MUST include both a classification string and a structural description of the visualized flow.
- **AgentState**: The shared dictionary where the detectives will append their respective evidence under the appropriate keys correctly.
- **RubricDimension**: The specific rule set instructions driving the goal string inside each piece of Evidence.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Run a unit test suite where all external dependencies (Git, Docling, LLMs) are mocked; 100% of these tests must pass.
- **SC-002**: Detectives return `Evidence` objects correctly formatted 100% of the time.
- **SC-003**: Inducing a catastrophic failure (missing inputs, API connection drop) in at least one detective does not halt the overall pipeline execution (graceful degradation validated by tests).
- **SC-004**: No interpretation or scoring details (e.g., assigning a grade out of 5) are included in the `Evidence` object content whatsoever.
- **SC-005**: All detective nodes terminate and return results (or failure items) within the mandatory 60-second operational window.
