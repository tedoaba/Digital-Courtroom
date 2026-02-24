# Feature Specification: Sandboxed Forensic Execution Interfaces

**Feature Branch**: `004-forensic-tools-sandbox`  
**Created**: 2026-02-24  
**Status**: Draft  
**Input**: User description: "Develop isolated, secure tools for repository cloning, Git log extraction, Python AST static analysis, and PDF parsing. Ensures security (no command injection, no os.system usage) and reproducible evidence gathering without executing malicious cloned code."

## Clarifications

### Session 2026-02-24

- Q: Should we enforce a maximum disk usage limit for cloned repositories to prevent host resource exhaustion? → A: Option A - Enforce a strict 1GB limit per forensic task
- Q: Which commit metadata fields are mandatory for the "Git Narrative Analysis"? → A: Option A - Capture Hash, Author, Date, and Message
- Q: How should extracted visual artifacts be stored for downstream processing? → A: Option A - Save as files in the isolated temporary workspace
- Q: Should the static analysis extract full function bodies and internal call graphs, or focus on high-level declarations and specific framework-related calls? → A: Option A - Extract Classes, Functions, Bases, and specific Framework calls (e.g. StateGraph, BaseModel)
- Q: For deterministic output auditing, should the findings include the "execution time" or only the "data derivation time"? → A: Option A - Use data derivation time only (e.g. Commit timestamps)

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Secure External Evidence Collection (Priority: P1)

As a security-conscious auditor, I want to retrieve external source code and history into an isolated environment so that I can analyze the development process without risking the integrity of my own system or allowing malicious code to run.

**Why this priority**: Fundamental safety requirement. External code must be treated as hostile until proven otherwise.

**Independent Test**: Provide a valid source URL and verify that the data is retrieved into a isolated space, processed, and all temporary artifacts are purged immediately after use.

**Acceptance Scenarios**:

1. **Given** a valid external source URL, **When** the collection tool is invoked, **Then** code is retrieved into a strictly isolated temporary space, and structural metadata (including full Git history: Hash, Author, Date, Message) is extracted.
2. **Given** a malformed or unauthorized URL, **When** collection is attempted, **Then** the system rejects the request immediately with a clear security warning.
3. **Given** a source that takes too long to respond, **When** collection is attempted, **Then** the operation is terminated within 60 seconds to prevent resource exhaustion.

---

### User Story 2 - Safe Structural Code Analysis (Priority: P1)

As an auditor, I want to scan source code for structural patterns (such as data models or orchestration logic) without actually running the code, so that I can gather evidence without triggering hidden or malicious logic.

**Why this priority**: Prevents "backdoor" execution. If we audit a repo that has `os.system('rm -rf /')` at the top level, our tools must be able to "see" it without "running" it.

**Independent Test**: Provide a file containing destructive code and verify that the analysis tool identifies the structure but no destructive actions occur.

**Acceptance Scenarios**:

1. **Given** a code file with complex structural patterns, **When** analyzed, **Then** a detailed map of classes and logic flows is returned without any side effects.
2. **Given** a file with invalid syntax, **When** analyzed, **Then** the tool reports the error as a finding rather than crashing.

---

### User Story 3 - Document and Visual Evidence Extraction (Priority: P2)

As an auditor, I want to extract text and embedded images from PDF reports so that I can automatically verify if the written claims match the code-level evidence.

**Why this priority**: Enables cross-referencing between "paperwork" and "reality".

**Independent Test**: Provide a PDF with specific text and diagrams and verify the extracted data matches the known content exactly.

**Acceptance Scenarios**:

1. **Given** a valid PDF document, **When** processed, **Then** all text content and embedded images are extracted into a structured format for comparison.
2. **Given** a corrupt or missing document, **When** processed, **Then** the system records the failure gracefully and continues with other available evidence.

---

### Edge Case Assumptions

- **Hostile Inputs**: All external URLs and file contents are treated as potentially malicious.
- **Resource Limits**: No single forensic operation may consume more than 60 seconds of processing time or 1GB of disk space.
- **Cleanup Guarantee**: The system must cleanup all temporary forensic artifacts even if a crash occurs during processing.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST execute all external commands using a method that prevents shell-based command injection (e.g., using argument lists instead of raw strings).
- **FR-002**: All forensic collection operations MUST have a hard execution timeout of 60 seconds.
- **FR-003**: The system MUST provide an isolated temporary workspace for all external artifacts that is automatically purged upon completion or failure.
- **FR-004**: Code analysis MUST be strictly static, focusing on extracting high-level declarations (Classes, Functions, Bases) and specific framework interactions (e.g., StateGraph wiring, BaseModel fields). The target code is never imported or executed.
- **FR-005**: All document parsing failures MUST be caught and converted into a standard "unparseable" status rather than allowing library errors to halt the system.
- **FR-006**: The system MUST validate all source URLs against a strict whitelist of approved domains (e.g., `github.com`, `gitlab.com`) and protocols (strictly `https`) before attempting collection.
- **FR-007**: Image extraction MUST be able to retrieve visual artifacts from documents and save them as temporary files within the isolated workspace without executing any scripts embedded within the document.
- **FR-008**: All tool outputs MUST be deterministic, ensuring that identical inputs always result in identical evidence findings.
- **FR-009**: The system MUST enforce a maximum disk usage limit of 1GB for any single isolated workspace.

### Key Entities _(include if feature involves data)_

- **Forensic Finding**: A structured object containing the evidence "fact", its location, confidence level, and a data-driven timestamp (e.g., commit date, not execution time).
- **Source Snapshot**: A temporary collection of retrieved code and metadata (including Commits with Hash, Author, Date, and Message).
- **Visual Artifact**: An image or diagram extracted from a document, stored as a file path in the isolated workspace, used for pattern verification.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: **Total Isolation**: 0% of temporary forensic data remains on the system 1 second after the forensic task completes.
- **SC-002**: **Safety Guarantee**: 100% of tested command injection payloads are blocked before execution.
- **SC-003**: **Resource Protection**: 100% of long-running operations are terminated precisely at the 60-second mark.
- **SC-004**: **Execution Prevention**: Analysis of local "poison" scripts results in zero unexpected side effects in 100% of test cases.
- **SC-005**: **Reproducibility**: Repeated analysis of the same source results in bit-identical evidence objects every time (achieved by using UTC data-derivation timestamps instead of execution-time markers).
