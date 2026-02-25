"""
Orchestration utilities for layer synchronization, timeouts, and error handling.
"""
import functools
import threading
from typing import Any, Callable, Dict, TypeVar

T = TypeVar("T")

def timeout_wrapper(seconds: int = 120):
    """
    Decorator to enforce a timeout on a synchronous function.
    Returns the original state with an error message appended if the timeout is hit.
    """
    def decorator(func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        @functools.wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            result_container = []
            exception_container = []

            def target():
                try:
                    res = func(state)
                    result_container.append(res)
                except Exception as e:
                    exception_container.append(e)

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                # Timeout occurred
                node_name = func.__name__
                error_msg = f"TimeoutError: Node '{node_name}' exceeded {seconds}s limit."
                new_errors = state.get("errors", []) + [error_msg]
                # Return state with error to trigger ErrorHandler routing
                return {**state, "errors": new_errors}
            
            if exception_container:
                # Re-raise or handle internal exception
                e = exception_container[0]
                node_name = func.__name__
                error_msg = f"Exception in '{node_name}': {str(e)}"
                new_errors = state.get("errors", []) + [error_msg]
                return {**state, "errors": new_errors}

            if result_container:
                return result_container[0]
            
            return state

        return wrapper
    return decorator


import re
import pathlib
from datetime import datetime

def sanitize_repo_name(name: str) -> str:
    """Sanitizes repository name for use in filesystem paths."""
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', name)
    sanitized = re.sub(r'\.\.+', '_', sanitized)
    return sanitized.lstrip('_')

def get_report_workspace(repo_name: str) -> pathlib.Path:
    """Initializes and returns a timestamped workspace directory for audit artifacts."""
    sanitized_name = sanitize_repo_name(repo_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Anchor to project root
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    workspace = root / "audit" / "reports" / sanitized_name / timestamp
    
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


import math
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(n: float, decimals: int = 0) -> float:
    """Standard 'round half up' logic."""
    multiplier = 10**decimals
    return float(math.floor(n * multiplier + 0.5) / multiplier)

def round_score(score: float) -> int:
    """Deterministic score rounding to nearest integer."""
    return int(
        Decimal(str(score)).quantize(Decimal("1"), rounding=ROUND_HALF_UP),
    )

class SynthesisError(Exception):
    """Raised when synthesis fails due to missing inputs."""
    pass
