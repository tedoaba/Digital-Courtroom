# Quickstart: DevOps Hardening

## Local Development (Makefile)

The new workflow abstracts complex `uv` commands into simple targets.

1.  **Initialize Environment**:

    ```bash
    cp .env.example .env
    # Add your keys
    ```

2.  **Run Quality Checks**:

    ```bash
    make lint
    make test
    ```

3.  **Run an Audit**:
    ```bash
    make run REPO=https://github.com/user/repo SPEC=reports/spec.pdf
    ```

## Containerized Execution (Docker)

To ensure exactly the same environment as production:

1.  **Build the Image**:

    ```bash
    make docker-build
    ```

2.  **Run the Auditor Dashboard**:
    ```bash
    make docker-run REPO=... SPEC=...
    ```

## CI/CD Pipeline

The GitHub Actions pipeline is defined in `.github/workflows/main.yml`. It automatically enforces:

- **Linting**: No `ruff` errors allowed.
- **Security**: No known vulnerabilities in dependencies (`pip-audit`).
- **Testing**: 100% pass rate.
- **Infrastructure**: Successful Docker build.
