# Implementation Plan: Sandboxed Forensic Execution Interfaces

**Branch**: `004-forensic-tools-sandbox` | **Date**: 2026-02-25 | **Spec**: [specs/004-forensic-tools-sandbox/spec.md]
**Input**: Feature specification from `/specs/004-forensic-tools-sandbox/spec.md`

## Summary

This feature involves developing a robust, security-hardened toolkit for forensic evidence collection. The primary requirement is to isolate all external interactions (cloning, parsing) to prevent command injection and unauthorized code execution. We will implement three core tools: `repo_tools.py` (Git operations via temp directories), `ast_tools.py` (non-executing Python analysis), and `doc_tools.py`/`vision_tools.py` (PDF and visual extraction). The technical approach leverages Python's `subprocess` with list-arguments, `tempfile` for isolation, `ast` for static analysis, and `docling` for document parsing.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `docling`, `pydantic`, `git` (CLI)  
**Storage**: Transient files in `tempfile.TemporaryDirectory`  
**Testing**: `pytest`  
**Target Platform**: Windows (Development) / Linux (Runtime Target)  
**Project Type**: Library / Forensic Toolkit  
**Performance Goals**: Sub-60s execution per tool call  
**Constraints**: 1GB disk limit per operation, zero execution of audited code, shell-injection safety  
**Scale/Scope**: Supports repositories up to 1GB and PDFs up to 50MB  
**Architectural Boundary**: Tools are strictly for **fact extraction** (structural/metadata); they do NOT interpret logic or assign scores (reserved for Nodes).

## Constitution Check

_GATE: Passed. (Initial: 2026-02-25 | Post-Design Re-check: 2026-02-25)_

| ID   | Principle                                                         | Compliance Status                        |
| ---- | ----------------------------------------------------------------- | ---------------------------------------- |
| XV-1 | All `git clone` MUST target `tempfile.TemporaryDirectory()`       | ✅ Confirmed in `repo_tools.py` contract |
| XV-2 | All subprocess calls MUST use list-form arguments                 | ✅ Confirmed in `repo_tools.py` contract |
| XV-3 | `os.system()` is PROHIBITED                                       | ✅ Strict adherence in all tools         |
| XV-4 | All subprocess calls MUST include a `timeout` parameter (max 60s) | ✅ Confirmed in `repo_tools.py` contract |
| XV-5 | Cloned code MUST be parsed via `ast.parse()` (never imported)     | ✅ Confirmed in `ast_tools.py` contract  |
| XX-1 | Code MUST be in `src/tools/`                                      | ✅ Applied in Project Structure          |

## Project Structure

### Documentation (this feature)

```text
specs/004-forensic-tools-sandbox/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
└── tools/
    ├── base.py          # Shared tool interfaces (ToolResult)
    ├── repo_tools.py    # Git operations (clone, log)
    ├── ast_tools.py     # Static analysis logic
    ├── doc_tools.py     # PDF parsing logic
    └── vision_tools.py  # Image extraction logic

tests/
├── unit/
│   └── tools/
│       ├── test_repo_tools.py
│       ├── test_ast_tools.py
│       └── test_doc_tools.py
└── integration/
    └── tools/
        └── test_forensic_suite.py
```

**Structure Decision**: Single project structure centered in `src/tools/` as per Constitutional principle XX.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

_No violations identified._
