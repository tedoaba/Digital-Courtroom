"""
Global Error Handling Node for the Digital Courtroom.
Captures catastrophic failures and prepares state for partial report generation.
"""

import logging
from typing import Any

from src.state import AgentState

logger = logging.getLogger("digital_courtroom.error_handler")


def error_handler_node(state: AgentState) -> dict[str, Any]:
    """
    ErrorHandler Node.
    Routes here if any node fails or an explicit error is detected.
    """
    errors = state.get("errors", [])

    # Log the failure for diagnostics
    logger.error(
        {
            "event": "orchestration_failure",
            "error_count": len(errors),
            "last_error": errors[-1] if errors else "Unknown error",
        },
    )

    # Mark metadata as failed to impact manifest
    metadata = state.get("metadata", {}).copy()
    metadata["run_status"] = "FAILED"
    metadata["failure_reasons"] = errors

    # We route to ReportGenerator next to produce a partial report
    # No state modification needed other than tagging the failure
    return {
        "metadata": metadata,
        "errors": errors,
    }
