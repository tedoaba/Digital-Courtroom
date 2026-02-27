# Quickstart: DevOps Hardening

## Local Development (Makefile)

The new workflow abstracts complex `uv` commands into simple targets. All targets include **Pre-flight Checks** to ensure your environment is ready.

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

> **Note**: If a prerequisite is missing (e.g., `.env`), you will see an error matching `ERROR: [ITEM] MISSING detected.`.

## Containerized Execution (Docker)

To ensure exactly the same environment as production, execute via the isolated container.

1.  **Build the Image**:

    ```bash
    make docker-build
    ```

2.  **Run the Auditor Dashboard**:
    ```bash
    make docker-run SPEC=reports/sample.pdf
    ```

The container runs as a **non-root user** (`courtroom_user`) and mounts:

- `/reports` as **Read-Only** (contains your input spec)
- `/audit` as **Read-Write** (for persisting evidence)

## CI/CD Pipeline

The GitHub Actions pipeline is defined in `.github/workflows/main.yml`. It automatically enforces:

- **Linting**: No `ruff` errors allowed; `hadolint` check on Dockerfile.
- **Security**: No known vulnerabilities in dependencies (`pip-audit`).
- **Testing**: Minimum 80% coverage gate.
- **Infrastructure**: Successful Docker build and artifact cleanup.
