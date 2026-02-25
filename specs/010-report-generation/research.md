# Research: Report Generation & Forensic Artifacts

## Unresolved Items from Technical Context

- **Markdown Templating**: Jinja2 is preferred over f-strings for complex, multi-section reports.
- **GFM Collapsible Blocks**: Confirmation of `<details>` tag behavior in GitHub Flavoured Markdown.
- **Pathlib Workspace Pattern**: Ensuring repo-relative paths work regardless of the current working directory.

## Decisions

### 1. Templating Engine

- **Decision**: Use `Jinja2`.
- **Rationale**: The report has nested structures (Criteria -> Opinions -> Evidence). Jinja2 supports loops, conditionals, and filters natively, which makes the template much cleaner than string concatenation or nested f-strings.
- **Alternatives considered**:
  - `f-strings`: Too brittle for 10+ criteria and multiple judge personas.
  - `Mako`: Powerful, but Jinja2 is the industry standard for Python-based web/doc templating.

### 2. Collapsible Forensic Log

- **Decision**: Use HTML `<details>` and `<summary>` tags with nested Markdown code blocks.
- **Rationale**: GitHub and most modern Markdown renderers support this. It prevents the report from becoming 10,000 lines long while keeping the data accessible.
- **Alternatives considered**:
  - `Dedicated Manifest File Only`: Requires the user to switch files; embedding the "Checksum Log" in the report (as requested in Spec) is better for a self-contained "courtroom verdict".

### 3. Output Path Management

- **Decision**: Use `pathlib.Path(__file__).parents[2]` (or similar) to anchor to the project root, then append `audit/reports/{repo_name}/`.
- **Rationale**: Ensures that even if the graph is run from a subfolder, the reports are always aggregated in the root `audit/` folder.
- **Alternatives considered**:
  - `os.getcwd()`: Unreliable as it depends on where the user runs the command.

### 4. Manifest Format

- **Decision**: JSON (`run_manifest.json`) for the sibling file; JSON string for the embedded log.
- **Rationale**: JSON is the standard for forensic checksums and machine-readable logs.

## Best Practices Findings

- **Markdown Whitespace**: Jinja2's `trim_blocks=True` and `lstrip_blocks=True` are essential to prevent extra newlines in the rendered Markdown which can break table formatting.
- **Escaping**: Use a custom filter or standard escaping to ensure that code snippets containing backticks (```) do not break the surrounding Markdown blocks.

## Dependencies Research

- `jinja2`: Stable, lightweight, no major security risks for internal document rendering.
- `pathlib`: Standard library, provides `mkdir(parents=True, exist_ok=True)` for robust dir creation.
