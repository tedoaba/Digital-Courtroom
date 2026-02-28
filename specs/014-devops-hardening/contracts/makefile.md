# Contract: Unified Makefile Interface

## Overview

The Makefile serves as the primary interface for both developers and the CI/CD pipeline. All system interactions must be possible through these defined targets.

## Command Schemas

### `make run`

Executes the standard background audit.

- **Arguments**:
  - `REPO` (string, optional): Remote repository URL
  - `SPEC` (path, optional): Path to the specification PDF
  - `RUBRIC` (path, optional): Path to a custom rubric JSON
- **Returns**: Code 0 on successful graph termination, non-zero on error.

### `make cli`

Executes the high-fidelity TUI dashboard.

- **Arguments**: Same as `run`.
- **Pre-requisite**: Interactive terminal.

### `make lint`

Runs code quality gates.

- **Tools**: `ruff`
- **Scope**: `src/`, `tests/`
- **Return**: Multi-code (fails if any tool fails).

### `make test`

Executes the full test suite with coverage.

- **Tools**: `pytest`, `pytest-cov`
- **Output**: Writes `htmlcov/` and prints terminal summary.

### `make docker-build`

Creates the OCI image.

- **Tag**: `digital-courtroom:latest`

### `make docker-run`

Runs the containerized TUI.

- **Volumes**: Maps `audit` and `reports` from host.
