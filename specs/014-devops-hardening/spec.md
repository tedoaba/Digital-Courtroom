# Feature Specification: DevOps Hardening — Containerization, Automation & CI/CD

**Feature Branch**: `014-devops-hardening`  
**Created**: 2026-02-27  
**Status**: Draft  
**Input**: User description: "DevOps Hardening — Containerization, Automation & CI/CD..."

## Clarifications

### Session 2026-02-27

- Q: Should the CI/CD pipeline also trigger on specific release-candidate branches? → A: Trigger on `main`, PRs, and `rc/*` branches.
- Q: Should the Makefile also verify the presence of required Docker volumes or specific environment variables? → A: Verify `.env`, `uv`, and critical directory existence (audit/reports).
- Q: Beyond ruff, should the CI pipeline include specific security scanning tools? → A: Include `ruff` (python), `hadolint` (Docker), and `pip-audit` (dependencies).
- Q: What are the specific metrics for "high code quality"? → A: No `ruff` errors/warnings (standard rules), Pytest coverage ≥ 80% on core modules, and `hadolint` severity `info` or higher.
- Q: What are the secret requirements for CI? → A: `GOOGLE_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2` (optional), and any provider-specific keys.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Unified Command Interface (Priority: P1)

Developers want a simple, consistent way to interact with the multi-agent swarm without needing to manage complex `uv run` flags or docker CLI arguments manually.

**Why this priority**: Correct and consistent execution is the foundation of local development and automated testing. It reduces the "works on my machine" friction.

**Independent Test**: Can be fully tested by running `make` commands locally and verifying they execute the expected underlying logic (e.g., `make lint` triggers `ruff`). If prerequisites fail, message MUST be clear: "ERROR: [PREREQUISITE] not found. Please [ACTION]."

**Acceptance Scenarios**:

1. **Given** a new environment, **When** running `make lint`, **Then** the system executes Ruff and fails if linting errors exist.
2. **Given** a `.env` file is missing, **When** running `make run`, **Then** the process fails with a clear instruction to create the environment file.
3. **Given** a repo URL and PDF path, **When** running `make run REPO=url SPEC=path`, **Then** the standard audit executes.

---

### User Story 2 - Standardized Execution via Docker (Priority: P1)

The system must run in an isolated, reproducible environment to ensure that forensic analysis and judicial rendering are consistent across local dev and production-like environments.

**Why this priority**: Containerization ensures all dependencies (including native ones like `docling` or `pymupdf` requirements) are correctly provisioned regardless of the host OS.

**Independent Test**: Can be tested by building the image and running the containerized TUI with mapped volumes.

**Acceptance Scenarios**:

1. **Given** the source code, **When** running `make docker-build`, **Then** a tagged `digital-courtroom` image is created using a non-root user and `python:3.12-slim`.
2. **Given** a sample PDF in `reports/`, **When** running `make docker-run SPEC=/reports/sample.pdf`, **Then** the container initializes, maps the volume, and starts the audit.

---

### User Story 3 - Automated Quality Gates (Priority: P2)

The repository must enforce high code quality and functional correctness automatically on every change to prevent regressions.

**Why this priority**: Automated gates are critical for the "Ironclad" reliability goal of the project, ensuring no broken code reaches the main branch.

**Independent Test**: Can be tested by pushing a PR and observing the GitHub Actions result.

**Acceptance Scenarios**:

1. **Given** a PR with failing tests, **When** the CI pipeline triggers, **Then** the build fails and blocks the merge.
2. **Given** a merge to a release-candidate branch, **When** the CI triggers, **Then** a full Docker build verification is performed to ensure the container is deployable.

---

### Edge Cases

- **Missing Volumes**: How does the Docker container behave if `/audit` or `/reports` are not mapped but required? (Should fail-fast with guidance: "ERROR: Required volume mapping [path] is missing. Use -v argument or make docker-run.").
- **Environment Variable Mismatch**: What happens if the host `.env` contains secrets but the Docker container isn't passed those variables? (Container entrypoint script MUST verify presence of critical variables before launching app).
- **Resource Constraints**: How does the containerized app handle low memory in a CI environment (optimized base image helps here).
- **Build Failures**: GitHub environment should automatically prune dangling images and volumes from failed builds using `docker system prune` in a post-run step.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide a **Multi-stage Dockerfile** optimized for `uv`, utilizing `python:3.12.9-slim` (pinned to minor version for reproducibility).
- **FR-002**: Container MUST execute under a **non-root user** (e.g., `courtroom_user`) to adhere to security best practices.
- **FR-003**: System MUST include a **Unified Makefile** with the following targets: `run`, `cli`, `test`, `lint`, `docker-build`, `docker-run`, and `clean`.
- **FR-004**: Makefile MUST include **Pre-flight Checks** verifying `.env` existence, availability of `uv`, and presence of critical directories (e.g., `/audit`, `/reports`).
  - Failure messages MUST follow pattern: `[MISSING] detected. Run 'make setup' or create [FILE].`
- **FR-005**: System MUST implement a **GitHub Actions CI/CD Pipeline** (`.github/workflows/main.yml`) using `hadolint` v2.x and `pip-audit` v2.x. Pipeline triggers on pushes to `main`, `rc/*` branches, and all Pull Requests.
  - Required Secrets: `GOOGLE_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` (for Observability).
- **FR-006**: Pipeline MUST **fail-fast** if:
  - `ruff` reports any errors or warnings.
  - `hadolint` reports severity `info` or higher.
  - `pip-audit` detects any vulnerabilities.
  - Pytest coverage falls below 80% (Core Modules).
- **FR-007**: Docker configuration MUST support **Volume Mapping** with specific permissions:
  - `/reports` (Input): Read-Only (`ro`)
  - `/audit` (Output): Read-Write (`rw`)

### Key Entities _(include if feature involves data)_

- **Build Artifact**: The OCI-compliant Docker image containing the Digital Courtroom runtime.
- **CI/CD Workflow**: The YAML-defined logic for automated verification and gatekeeping.
- **Makefile Token**: Abstractions for environment variables (REPO, SPEC, RUBRIC) passed to the courtroom entrypoint.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: `make docker-build` completes in under 3 minutes on a fresh environment (after initial layer caching).
- **SC-002**: Docker image size remains under 400MB (excluding large model weights if any were baked in, though here we use API/Ollama).
- **SC-003**: CI pipeline achieves 100% pass rate on `main` branch pushes.
- **SC-004**: Containerized TUI successfully initializes and displays the dashboard when run via `make docker-run`.
- **SC-005**: Zero warnings or errors are reported by `ruff` across the entire project in the automated pipeline.
