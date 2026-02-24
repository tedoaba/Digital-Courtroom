# Internal Tool Contracts: Sandboxed Forensic Execution Interfaces

## `repo_tools.py`

### `clone_repo(url: str) -> Tuple[TemporaryDirectory, Path]`

- **Input**: Validated GitHub URL.
- **Output**: The temp directory object (for cleanup) and the path to the cloned repository.
- **Constraints**: 60s timeout, no shell.

### `extract_git_history(repo_path: Path) -> List[Commit]`

- **Input**: Path to repository.
- **Output**: Chronologically sorted list of commits.

## `ast_tools.py`

### `scan_repository(repo_path: Path) -> List[ASTFinding]`

- **Input**: Path to code.
- **Output**: List of structural findings across all `.py` files.
- **Safety**: No imports, pure `ast.parse`.

## `doc_tools.py`

### `ingest_pdf(pdf_path: Path) -> List[str]`

- **Input**: Path to PDF.
- **Output**: List of text chunks.

### `extract_visuals(pdf_path: Path, output_dir: Path) -> List[Path]`

- **Input**: Path to PDF, directory to save images.
- **Output**: List of paths to extracted image files.
