# Quickstart: Foundational Scaffolding

Follow these steps to initialize your development environment for the Digital Courtroom project.

## 1. Prerequisites

- **Python**: 3.12+
- **UV**: Installed (see [uv documentation](https://github.com/astral-sh/uv))

## 2. Global Initialization

Run the following command from the repository root to synchronize your environment:

```bash
uv sync
```

## 3. Configuration Setup

Create your local environment file from the provided template:

```bash
cp .env.example .env
```

Edit `.env` and provide your API keys. Mandatory keys include:

- `OPENAI_API_KEY`
- `LANGCHAIN_API_KEY`

## 4. Run Verification

Verify your installation by running the foundational test suite and quality checks:

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run formatting check
uv run ruff format --check .
```

## 5. Development Command

To run any script in the project environment, always use `uv run`:

```bash
uv run python src/main.py
```
