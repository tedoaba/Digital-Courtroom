# Research: Parallel Detective Agents (Layer 1)

## Unknowns & Research Tasks

| Unknown                  | Research Task                                                                         | Status   |
| ------------------------ | ------------------------------------------------------------------------------------- | -------- |
| Git Sandboxing           | Verify `tempfile.TemporaryDirectory` behavior for cross-platform Git clone isolation. | Resolved |
| AST Forensic Patterns    | Identify `ast` patterns to detect `StateGraph` wiring and `Pydantic` models reliably. | Resolved |
| PDF Extraction (Docling) | Best practices for extracting text chunks and images using `docling`.                 | Resolved |
| Multimodal Prompting     | Prompt engineering for zero-shot diagram classification in `VisionInspector`.         | Resolved |

## Findings

### 1. Git Sandboxing & AST Forensics

- **Decision**: Use `tempfile.TemporaryDirectory` context manager for each `RepoInvestigator` run. Use `subprocess.run` with `list` arguments and a 60s timeout.
- **Rationale**: Ensures that cloned code never persists or interferes with the host system. List-form arguments prevent shell injection.
- **AST Strategy**: Use `ast.walk` to find `Call` nodes to `StateGraph` and `ClassDef` nodes inheriting from `BaseModel`.
- **Alternatives**: `tree-sitter` was considered but `ast` is built-in and sufficient for structural verification of Python code.

### 2. PDF Analysis (DocAnalyst)

- **Decision**: Use `docling` for PDF to Markdown conversion, followed by paragraph-based chunking.
- **Rationale**: `docling` provides high-fidelity extraction of structural elements which is critical for verifying architectural claims.
- **Alternatives**: `PyMuPDF` is faster but less "intelligent" about document structure compared to `docling`.

### 3. Vision Inspector (VisionInspector)

- **Decision**: Extract images using `docling`'s image export features. Use **Gemini Pro Vision** for classification.
- **Rationale**: Multimodal models can distinguish between linear flowcharts and complex parallel graph diagrams. Gemini is the project's mandated multimodal provider.
- **Prompt Pattern**: "Classify the following architectural diagram into one of: 'Parallel Flow', 'Linear Pipeline', or 'Generic Flowchart'. Provide a 2-sentence structural description."

### 4. Error Handling & Logging

- **Decision**: Catch all `Exception` at the node boundary. Log the traceback via `StructuredLogger`. Return `Evidence(found=False, rationale=str(e))`.
- **Rationale**: Prevents a single detective failure from crashing the entire audit pipeline (Principle VII).
