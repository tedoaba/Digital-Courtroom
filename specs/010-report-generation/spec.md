# Feature Specification: Final Report Generation and Audit Artifacts

**Feature Branch**: `010-report-generation`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Final Report Generation and Audit Artifacts: Produce the final human-readable AuditReport matching the requested specifications. Included: report_generator component inside justice.py. Creating the Markdown result incorporating dissenting viewpoints, specific instructions, and the checksum log. Excluded: LangGraph routing logic."

The objective of this feature is to implement Layer 4 (`ReportGenerator`) of the Digital Courtroom. It transforms the structured `AuditReport` Pydantic model produced by the `ChiefJustice` node into a professional, human-readable Markdown report that encapsulates the entire audit trail, including evidence citations, judicial debates, and actionable remediation steps.

## Clarifications

### Session 2026-02-25

- Q: Output File Naming & Location Strategy → A: audit/reports/{repo_name}/report.md (Namespace per repo)
- Q: Checksum Log Inclusion Format → A: Embedded Collapsible: Raw JSON in a `<details>` block at the end.
- Q: Remediation Plan Structure → A: Grouped by Criterion: Each criterion lists its own specific fixes.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Generate Comprehensive Audit Report (Priority: P1)

As an auditor, I want to receive a structured Markdown report that summarizes the audit findings, breaks down each criterion, and provides a clear remediation plan so that I can understand the quality of the target repository and how to improve it.

**Why this priority**: This is the primary output of the system. Without this, the system's findings are not accessible to human users.

**Independent Test**: Can be tested by providing a mocked `AuditReport` pydantic object to the `ReportGenerator` and verifying the resulting `.md` file contains the Executive Summary, all 10 criteria, and the Remediation Plan.

**Acceptance Scenarios**:

1. **Given** a fully populated `AuditReport` model, **When** the `report_generator` executes, **Then** a Markdown file is created with an `# Executive Summary` header.
2. **Given** a `CriterionResult` with an overall score of 1 and a `remediation` string, **When** rendered, **Then** the "Remediation Plan" section must contain the specific file-level instructions provided in that result.
3. **Given** a criterion with a score variance of 3 (major conflict), **When** rendered, **Then** a "Dissent Summary" block must be visible within that criterion's breakdown.

---

### User Story 2 - Forensic Evidence Traceability (Priority: P2)

As a technical reviewer, I want the report to include a "Checksum Log" or "Evidence Manifest" that links every finding to its forensic source so that I can verify the audit's integrity and reproducibility.

**Why this priority**: Ensures the "forensic" nature of the auditor. Users must be able to trust the report by seeing the breadcrumbs back to the code.

**Independent Test**: Can be tested by checking the "Citations" in the Markdown report and ensuring every `evidence_id` mentioned exists in the final "Evidence Manifest" section of the document.

**Acceptance Scenarios**:

1. **Given** a `JudicialOpinion` citing `evidence_id: "repo_git_001"`, **When** rendered, **Then** the Markdown must include a link or reference to that specific ID.
2. **Given** a list of 5 `Evidence` objects in the state, **When** rendered, **Then** the final section of the report must list all 5 items with their rationale and source (Repo/Docs/Vision).

---

### User Story 3 - Resilient Reporting on Partial Failures (Priority: P2)

As a system operator, I want the report generator to handle missing data gracefully (e.g., if a detective fails) and still produce a "Partial Report" rather than crashing so that I can see what was successfully audited even if some parts failed.

**Why this priority**: Production systems must be robust. A single node failure shouldn't prevent the generation of results from other nodes.

**Independent Test**: Can be tested by passing an `AuditReport` where some `criteria` are marked with error placeholders and verifying the generator produces a report that acknowledges the missing data instead of throwing an exception.

**Acceptance Scenarios**:

1. **Given** an `AgentState` with 1 valid criterion and 9 missing ones (due to failure), **When** rendered, **Then** the report should still generate the Executive Summary and the one valid criterion, with "Audit Error" headers for the rest.

---

### Edge Cases

- **Large Evidence Content**: How does the system handle an `Evidence` object containing 100 lines of code? (It should probably be truncated or placed in a collapsible block).
- **Symbol Overlap**: How does the Markdown handle special characters in commit messages or code snippets? (Must use proper escaping to prevent rendering breaks).
- **OS Portability**: How does the system handle relative paths for the output file on Windows vs Linux? (Must use `pathlib`).

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST translate the `AuditReport` Pydantic model into a structured Markdown document using a deterministic template.
- **FR-002**: System MUST format the report headers in hierarchical order:
  - `# Audit Report: [Repo Name]`
  - `## Metadata Table: Date (ISO8601), Git Hash, Rubric Version, and Aggregate Score.`
  - `## Executive Summary`
  - `## Criterion Breakdown`
  - `## Remediation Plan`
  - `## Forensic Evidence Manifest`
- **FR-003**: System MUST include a "Dissent Summary" block for any criterion where `dissent_summary` is non-null.
- **FR-004**: System MUST list specific, file-level instructions for remediation grouped by their parent rubric criterion.
- **FR-005**: System MUST include a "Forensic Evidence Manifest" at the end of the report, mapping every `evidence_id` to its `source`, `location`, and `rationale`.
- **FR-006**: System MUST handle all file I/O using OS-agnostic path logic to ensure cross-platform compatibility.
- **FR-007**: System MUST provide a `fallback_render` mode that catch-all exceptions during Markdown generation and returns a basic "System Fault Report" to prevent total pipeline failure.
- **FR-008**: System MUST include a "Checksum Log" consisting of all `Evidence` objects serialized to JSON; this MUST be embedded as a collapsible `<details>` block in report and optionally output as a sibling file `run_manifest.json`.
- **FR-009**: System MUST initialize the output workspace at `audit/reports/{repo_name}/{timestamp}/` where timestamp is `YYYYMMDD_HHMMSS` to prevent overwriting previous runs.
- **FR-010**: System MUST format Markdown using GitHub Flavored Markdown (GFM) standards, ensuring all code blocks use triple backticks and tables have valid alignment headers.
- **FR-011**: System MUST truncate `Evidence.content` if it exceeds 5000 characters, appending a `[TRUNCATED]` notice and directing users to the raw JSON manifest.
- **FR-012**: System MUST format remediation instructions as `[file_path]:[line_number] - [action]` (e.g., `src/auth.py:22 - Add input validation`).
- **FR-013**: System MUST render "No forensic evidence cited" placeholder if a criterion lacks supporting detective facts.
- **FR-014**: System MUST sanitize the `repo_name` by removing special characters and path traversal sequences (`..`, `/`, `\`) before creating filesystem directories.
- **FR-015**: System MUST render a "Judicial Note" block if `dissent_summary` is non-null but `final_score` variance is 0 (signaling nuanced consensus).
- **FR-016**: System MUST ensure cross-platform path stability for Windows (NTFS) and Linux (Ext4) by avoiding reserved filename characters.

### Key Entities _(include if feature involves data)_

- **AuditReport**: Top-level model containing `executive_summary`, `overall_score`, `criteria` (List), and `remediation_plan`.
- **CriterionResult**: Result for one rubric dimension, containing `final_score`, `judge_opinions`, `dissent_summary`, and `remediation`.
- **Evidence**: The forensic data points (id, source, found, rationale, location).
- **JudicialOpinion**: Individual judge's verdict (Prosecutor/Defense/TechLead).

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of successful `ChiefJustice` synthesis outputs trigger the generation of a `.md` file.
- **SC-002**: Rendered report matches the structural layout defined in `ARCHITECTURE_NOTES.md` Section 7.3.
- **SC-003**: Report generation time is < 500ms for a standard 10-criterion audit once the synthesis is complete.
- **SC-004**: All evidence citations in the Markdown body are resolvable to an entry in the "Forensic Evidence Manifest" section via exact ID matching regex `[a-z]+_[a-z]+_[0-9]+`.
- **SC-005**: Partial reports are generated within 1s even if 50% of the judicial data is missing or malformed.
- **SC-006**: Deterministic output MUST achieve 100% byte-for-byte identity when re-running the same `AgentState` on the same template version.
