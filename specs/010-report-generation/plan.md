# Implementation Plan: Final Report Generation and Audit Artifacts

**Branch**: `010-report-generation` | **Date**: 2026-02-25 | **Spec**: [specs/010-report-generation/spec.md](spec.md)
**Input**: Feature specification from `/specs/010-report-generation/spec.md`

## Summary

The `ReportGenerator` (Layer 4) will transform the synthesized `AuditReport` Pydantic model into a deterministic, human-readable Markdown audit report. This involves using a Jinja2 template to render the executive summary, criterion breakdown (including dissenting views), remediation plans, and a forensic evidence manifest. Additionally, it will generate a `run_manifest.json` containing the full forensic checksum log for reproducibility.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `jinja2`, `pathlib`, `pydantic`
**Storage**: Local filesystem (`audit/reports/{repo_name}/`)
**Testing**: `pytest`
**Target Platform**: Windows/Cross-platform
**Project Type**: Library Component / LangGraph Node
**Performance Goals**: < 500ms rendering time
**Constraints**:

- Deterministic output (same input → same Markdown byte-for-byte).
- Safe file I/O (no `os.system`).
- Relative path stability via `pathlib`.
  **Scale/Scope**: ~10 Criteria, 3 Judge Opinions per criterion, up to 100 Evidence objects.

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle                    | Status | Implementation Note                                                                        |
| ---------------------------- | ------ | ------------------------------------------------------------------------------------------ |
| **I. Spec-Driven**           | PASS   | `spec.md` covers all user scenarios and requirements.                                      |
| **II. TDD**                  | PASS   | `tests/unit/nodes/test_justice.py` (for report gen) will be created before implementation. |
| **IV. Schema-First**         | PASS   | Leverages `AuditReport` and `Evidence` models from `src/state.py`.                         |
| **XIII. Hierarchical**       | PASS   | Correctly placed as Layer 4 (final node).                                                  |
| **XV. Sandboxed Tooling**    | PASS   | Uses `pathlib` for safe, OS-agnostic file writes; no shell execution.                      |
| **XVII. Traceable Scoring**  | PASS   | Explicitly includes `evidence_id` citations and a forensic manifest section.               |
| **XX. Modular Architecture** | PASS   | Integrated into `src/nodes/justice.py` (or separate `report.py` if logic is large).        |
| **XXII. Structured Logging** | PASS   | Uses `StructuredLogger` for entry/exit events.                                             |
| **XXV. Unit Tests Per Node** | PASS   | Dedicated tests for Markdown rendering and manifest generation.                            |

## Project Structure

### Documentation (this feature)

```text
specs/010-report-generation/
├── plan.md              # This file
├── research.md          # Markdown templating & GFM collapsible research
├── data-model.md        # Report & Manifest schemas
├── quickstart.md        # Manual report generation guide
├── checklists/          # Requirement quality checklist
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
src/
├── nodes/
│   └── justice.py       # Contains the ReportGenerator node logic
├── state.py             # AuditReport and Evidence schemas (Shared)
└── templates/           # Jinja2 templates for the audit report
    └── report.md.j2     # The master template

tests/
├── unit/
│   └── nodes/
│       └── test_report.py
└── integration/
    └── test_full_pipeline.py
```

**Structure Decision**: Single project layout. The report generator logic will reside in `src/nodes/justice.py` (or a dedicated `src/nodes/report.py` if complex), and a new `src/templates/` directory will store the Markdown template.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

_No violations detected._
