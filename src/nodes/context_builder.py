"""
ContextBuilder Initialization Node for the Digital Courtroom.

This is the entry point (Layer 0) of the StateGraph. It bootstraps execution
state by validating inputs, loading the evaluation rubric, and initializing
parallel-safe state collections.

Constitutional Traceability:
    - Const. III: Deterministic logic (no LLM calls)
    - Const. IV: Schema-first design (Pydantic-backed state)
    - Const. VI: Parallel-safe reducers (empty collection init)
    - Const. VII: Explicit error handling (graceful failure)
    - Const. XX: Modular architecture (src/nodes/)
    - Const. XXII: Structured logging (entry/exit events)
    - Const. XXIII: Package management (uv)
"""

import json
import logging
import os
import re
import uuid
from typing import Any

from src.state import AgentState
from src.utils.logger import StructuredLogger
from src.utils.security import sanitize_repo_url
from src.utils.observability import node_traceable

# --- Constants (Const. XX.5: No hardcoded values) ---

DEFAULT_RUBRIC_PATH: str = "rubric/week2_rubric.json"

# Module-level logger
_logger = StructuredLogger(name="context_builder", level=logging.INFO)


def _validate_repo_url(url: str) -> str | None:
    """
    Validate the repository URL against the GitHub HTTPS pattern.
    """
    try:
        sanitize_repo_url(url)
        return None
    except ValueError as e:
        return str(e)



def _validate_pdf_path(pdf_path: str) -> str | None:
    """
    Validate the PDF report path exists on the filesystem.

    Args:
        pdf_path: The local filesystem path to check.

    Returns:
        Error message string if missing, None if exists.
    """
    # FR-004: Existence check only
    if not os.path.exists(pdf_path):
        return f"Missing PDF report at: {pdf_path}"

    return None


def _load_rubric(rubric_path: str) -> tuple[list[dict], dict[str, str], list[str]]:
    """
    Load and validate the rubric JSON file.

    Args:
        rubric_path: Path to the rubric JSON file.

    Returns:
        Tuple of (dimensions, synthesis_rules, errors).
        On failure, dimensions and rules are empty, errors contain messages.
    """
    errors: list[str] = []

    # Check file existence
    if not os.path.exists(rubric_path):
        errors.append(f"Fatal: Could not load rubric from {rubric_path}")
        return [], {}, errors

    # Parse JSON
    try:
        with open(rubric_path, "r", encoding="utf-8") as rubric_file:
            rubric_data = json.load(rubric_file)
    except (json.JSONDecodeError, OSError):
        errors.append(f"Fatal: Could not load rubric from {rubric_path}")
        return [], {}, errors

    # FR-010: Validate dimensions key exists and is non-empty
    dimensions = rubric_data.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) == 0:
        errors.append(
            f"Fatal: Rubric missing required 'dimensions' key at: {rubric_path}"
        )
        return [], {}, errors

    # FR-005: Extract synthesis_rules (default to empty dict if missing)
    synthesis_rules = rubric_data.get("synthesis_rules", {})

    return dimensions, synthesis_rules, errors


@node_traceable
def build_context(state: dict[str, Any]) -> dict[str, Any]:
    """
    ContextBuilder node function for the Digital Courtroom StateGraph.

    Bootstraps execution state by:
    1. Validating repo_url (FR-002, FR-003)
    2. Validating pdf_path (FR-004)
    3. Loading rubric dimensions and synthesis rules (FR-001, FR-005, FR-008, FR-010)
    4. Initializing parallel-safe collections (FR-009)

    On validation failure, appends errors to state['errors'] and returns
    the state for downstream routing (FR-007).

    Args:
        state: The incoming AgentState dictionary.

    Returns:
        Updated state dictionary with rubric data and initialized collections.
    """
    correlation_id = state.get("metadata", {}).get("correlation_id") or state.get("correlation_id") or str(uuid.uuid4())

    # FR-007: Preserve existing errors (append, never clear)
    errors: list[str] = list(state.get("errors", []))

    # FR-006: Log entry event at INFO level (Const. XXII)
    rubric_path = state.get("rubric_path", DEFAULT_RUBRIC_PATH)
    _logger.info(
        "ContextBuilder node started",
        event_type="context_builder_entry",
        correlation_id=correlation_id,
        payload={
            "rubric_path": rubric_path,
        },
    )

    # --- Input Validation (FR-002, FR-003, FR-004) ---

    repo_url = state.get("repo_url", "")
    url_error = _validate_repo_url(repo_url)
    if url_error:
        errors.append(url_error)

    pdf_path = state.get("pdf_path", "")
    pdf_error = _validate_pdf_path(pdf_path)
    if pdf_error:
        errors.append(pdf_error)

    # --- Rubric Loading (FR-001, FR-005, FR-008, FR-010) ---

    dimensions: list[dict] = []
    synthesis_rules: dict[str, str] = {}

    rubric_dimensions, rubric_synthesis_rules, rubric_errors = _load_rubric(rubric_path)
    errors.extend(rubric_errors)

    if not rubric_errors:
        dimensions = rubric_dimensions
        synthesis_rules = rubric_synthesis_rules

    # --- State Initialization (FR-009, Const. VI) ---

    result: dict[str, Any] = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_path": rubric_path,
        "rubric_dimensions": dimensions,
        "synthesis_rules": synthesis_rules,
        "evidences": state.get("evidences", {}),
        "opinions": state.get("opinions", []),
        "criterion_results": state.get("criterion_results", {}),
        "errors": errors,
    }

    # FR-006: Log exit event at INFO level (Const. XXII)
    status = "failed" if errors and errors != list(state.get("errors", [])) else "success"

    # Get rubric version for logging
    rubric_version = "unknown"
    if dimensions:
        try:
            with open(rubric_path, "r", encoding="utf-8") as f:
                rubric_data = json.load(f)
                rubric_version = rubric_data.get("rubric_metadata", {}).get(
                    "version", "unknown"
                )
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    _logger.info(
        "ContextBuilder node completed",
        event_type="context_builder_exit",
        correlation_id=correlation_id,
        payload={
            "status": status,
            "rubric_version": rubric_version,
            "dimension_count": len(dimensions),
        },
    )

    return result
