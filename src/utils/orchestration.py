"""
Orchestration and resilience utilities for Operation Ironclad Swarm.
(013-ironclad-hardening)
"""
import time
import asyncio
import re
import pathlib
from typing import Optional, List, Dict, Any, Callable
from functools import wraps
from datetime import datetime
from src.state import CircuitBreakerStatus, CircuitBreakerState

def timeout_wrapper(seconds: float):
    """Decorator to apply asyncio timeout to a node function."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                # Log timeout and inject error into state if applicable
                from src.utils.logger import StructuredLogger
                logger = StructuredLogger("timeout_wrapper")
                logger.error(f"Node {func.__name__} timed out after {seconds}s")
                # If the first arg is state, append an error
                if args and isinstance(args[0], dict) and "errors" in args[0]:
                    args[0]["errors"].append(f"TIMEOUT: Node {func.__name__} exceeded {seconds}s limit.")
                raise
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Stateful circuit breaker for API resilience (T028).
    (FR-008, FR-011)
    """
    def __init__(self, name: str, failure_threshold: int = 3, reset_timeout: int = 30):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = CircuitBreakerStatus.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[float] = None

    def can_execute(self) -> bool:
        if self.state == CircuitBreakerStatus.CLOSED:
            return True
        if self.state == CircuitBreakerStatus.OPEN:
            if time.time() - (self.last_failure_time or 0) > self.reset_timeout:
                self.state = CircuitBreakerStatus.HALF_OPEN
                return True
            return False
        if self.state == CircuitBreakerStatus.HALF_OPEN:
            return True
        return False

    def record_success(self):
        if self.state == CircuitBreakerStatus.HALF_OPEN:
            self.state = CircuitBreakerStatus.CLOSED
            self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitBreakerStatus.OPEN

    async def aexecute(self, func: Callable, *args, **kwargs):
        """Execute async call with circuit breaker protection."""
        if not self.can_execute():
            raise RuntimeError(f"Circuit Breaker '{self.name}' is OPEN. Call rejected.")
        
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

    def get_status(self) -> CircuitBreakerState:
        """Return current status."""
        return CircuitBreakerState(
            resource_name=self.name,
            status=self.state,
            failure_count=self.failures,
            last_failure_time=datetime.fromtimestamp(self.last_failure_time) if self.last_failure_time else None
        )

def trigger_rollback(last_valid_state: Dict[str, Any], error: str) -> Dict[str, Any]:
    """FR-009: Restore system to last known valid state (T030)."""
    rollback_state = last_valid_state.copy()
    if "metadata" not in rollback_state:
        rollback_state["metadata"] = {}
    rollback_state["metadata"]["rollback_triggered"] = True
    rollback_state["metadata"]["rollback_reason"] = error
    rollback_state["metadata"]["rollback_timestamp"] = datetime.now().isoformat()
    return rollback_state

def detect_cascading_failure(errors: List[str]) -> bool:
    """FR-011: Check if core streams are failing."""
    forensic_count = sum(1 for e in errors if any(kw in e for kw in ["FORENSIC", "CRITICAL", "FATAL"]))
    return forensic_count > 3

_cb_registry: Dict[str, CircuitBreaker] = {}

def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Registry for circuit breakers per resource (T029)."""
    if name not in _cb_registry:
        _cb_registry[name] = CircuitBreaker(name)
    return _cb_registry[name]

# --- Restored Orchestration Helpers ---

def sanitize_repo_name(url: str) -> str:
    """Extracts a filesystem-safe name from a GitHub URL."""
    name = url.split('/')[-1]
    if name.endswith('.git'):
        name = name[:-4]
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def get_report_workspace(base_dir: str, repo_url: str) -> pathlib.Path:
    """Creates a dedicated output directory for the audit run."""
    repo_name = sanitize_repo_name(repo_url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = pathlib.Path(base_dir) / f"{repo_name}_{timestamp}"
    path.mkdir(parents=True, exist_ok=True)
    return path

def round_half_up(n, decimals=0):
    """Correct rounding behavior for financial/judicial precision."""
    multiplier = 10**decimals
    return float(int(n * multiplier + 0.5) / multiplier)

def round_score(score: float) -> int:
    """Rounds judicial scores to the nearest integer 1-5."""
    return int(max(1, min(5, round_half_up(score))))

class SynthesisError(Exception):
    """Raised when judicial consensus fails due to structural reasons."""
    pass
