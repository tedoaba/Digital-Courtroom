# Digital Courtroom - Sandboxed Forensic Tools

This module provides isolated, deterministic tools for digital forensic extraction and structural code analysis. It specifically enables safely inspecting repositories and documents without allowing unintended code execution.

## Features

- **Safe Repo Cloning:** Prevents command injection and limits disk usage. Clones securely into temporary environments.
- **AST Code Scanning:** Scans for specific language syntax or patterns (e.g. `BaseModel`, `StateGraph`) without executing the code.
- **Document & Visuals Parsing:** Uses `docling` to extract markdown and images from PDF reports. Ensures failure gracefully for password-protected files.
- **Execution Isolation:** All outputs implement `ToolResult` interface, with hard timeout enforcing via a subthread.
- **Dialectical Judicial Agents:** Three adversarial personas (Prosecutor, Defense, TechLead) evaluate evidence in parallel with < 10% prompt overlap and structured schema validation.
- **Determinism:** Guarantees deterministic behavior for git commit extraction using UTC timestamps.

_Refer to the [Quickstart Guide](specs/004-forensic-tools-sandbox/quickstart.md) for more usage examples._
