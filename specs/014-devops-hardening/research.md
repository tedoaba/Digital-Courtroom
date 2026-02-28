# Research: DevOps Hardening — Containerization, Automation & CI/CD

## Decision: Multi-stage Dockerfile for `uv`

### Rationale

Multi-stage builds allow us to separate the build-time environment (with `uv`, compilers, and caches) from the production runtime. Using the official `ghcr.io/astral-sh/uv` image to copy the binary is the most efficient way to provision `uv`.

### Implementation Details

- **Base Image**: `python:3.12-slim` for the final stage.
- **Cache Mounts**: `RUN --mount=type=cache,target=/root/.cache/uv uv sync` to persist package downloads across builds.
- **Optimizations**: `UV_LINK_MODE=copy` and `UV_COMPILE_BYTECODE=1`.
- **Security**: Non-root user `courtroom_user` with UID 1000.

### Alternatives Considered

- **pip install uv**: Rejected because it's slower and adds an extra layer compared to binary copy.
- **Full python image**: Rejected (800MB+) in favor of slim (120MB+).

## Decision: Security & Linting Stack

### Rationale

`hadolint` is the industry standard for Dockerfile quality. `pip-audit` is maintained by PyPA and provides the most reliable vulnerability scanning for Python dependencies.

### Implementation Details

- **Hadolint**: Integrated via `hadolint/hadolint-action@v3.1.0`.
- **pip-audit**: Integrated via `pypa/gh-action-pip-audit@v1.1.0`.
- **Ruff**: Enforced both locally and in CI via `uv run ruff check`.

### Alternatives Considered

- **Safety**: Considered but `pip-audit` is generally preferred for its use of the PyPA advisory database.
- **Snyk/SonarQube**: Rejected as over-engineered for the current project scope.

## Decision: Makefile for Unified Workflow

### Rationale

A Makefile provides a technology-agnostic entry point. Developers don't need to know `uv run python -m src.main` vs `uv run python -m src.cli`; they just run `make run` or `make cli`.

### Implementation Details

- **Pre-flight Checks**: Hidden targets `.check-uv`, `.check-env`, and `.check-dirs` that fail with guidance if prerequisites are missing.
- **Variables**: Support for `REPO`, `SPEC`, and `RUBRIC` as overrides (e.g., `make run REPO=...`).

### Alternatives Considered

- **Shell Scripts**: Rejected because Make handles dependency tracking (targets) and environment variable defaults more cleanly.
