# Research: Sandboxed Forensic Execution Interfaces

## Decision 1: Git Sandboxing and Forensics

**Decision**: Use `tempfile.TemporaryDirectory` with `subprocess.run(list_args)` and `--depth 100`.
**Rationale**: `tempfile.TemporaryDirectory` provides automatic cleanup. `subprocess.run` with list arguments prevents shell injection. `--depth 100` balances history depth vs performance/disk limits.
**Alternatives considered**:

- `git clone --depth 1`: Rejected because it might miss the "narrative" history required by Protocol A.
- `shutil.rmtree` manually: Rejected as error-prone; `tempfile` context managers are safer.

## Decision 2: Non-Executing Code Analysis

**Decision**: Use standard library `ast` module with `ast.walk`.
**Rationale**: Guarantees zero execution of audited code. `ast.walk` is sufficient for detecting `BaseModel` and `StateGraph` patterns as specified in the rubric.
**Alternatives considered**:

- `importlib`: Rejected (Violates Constitution XV-5).
- `regex`: Rejected as brittle (Violates Protocol B requirements for structural verification).
- `tree-sitter`: Considered but `ast` is lightweight and built-in for Python-only analysis.

## Decision 3: Document Parsing

**Decision**: Use `docling` for PDF to Markdown conversion and image extraction.
**Rationale**: Recommended in `ARCHITECTURE_NOTES.md`. Provides high-quality markdown export and built-in image artifact tracking.
**Alternatives considered**:

- `PyMuPDF`: Valid alternative for image extraction, but `docling` offers better structural markdown conversion for "Theoretical Depth" analysis.

## Decision 4: Determinism

**Decision**: Enforce UTF-8 encoding for all file reads and use `datetime.fromtimestamp` on commit data.
**Rationale**: Ensures bit-identical findings across platforms.
