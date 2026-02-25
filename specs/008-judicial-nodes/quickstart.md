# Quickstart: Dialectical Judicial Agents (Layer 2)

## Overview

This guide detail how to execute and verify the Judicial Agent layer (Layer 2) in isolation.

## Prerequisites

- Environment setup with `uv`.
- Configured LLM keys in `.env` (Gemini Pro recommended).

## Environment Setup

1. Sync dependencies:

   ```bash
   uv sync
   ```

2. Verify environment variables:
   ```bash
   cp .env.example .env
   # Ensure LANGCHAIN_TRACING_V2=true is set
   ```

## Local Execution (Mocks)

To test the judicial nodes without running the full detective layer:

1. Use the provided test harness:
   ```bash
   uv run python tests/harness/run_judicial_mock.py
   ```
   _Note: This script passes simulated forensic evidence into the judicial nodes._

## Running Tests

Execute the specific test suites for this feature:

1. **Unit Tests** (Persona logic & Fallbacks):

   ```bash
   uv run pytest tests/unit/test_judges.py
   ```

2. **Persona Overlap Check**:

   ```bash
   uv run pytest tests/unit/test_judges.py -k "test_prompt_divergence"
   ```

3. **Integration Tests** (Fan-out/Fan-in):
   ```bash
   uv run pytest tests/integration/test_judicial_workflow.py
   ```

## Debugging

1. Open **LangSmith** to view the parallel fan-out ofLLM calls.
2. Check `state.errors` if a judge returns the "System Error" fallback.
