"""
Orchestration and resilience utilities for Operation Ironclad Swarm.
(013-ironclad-hardening)
"""

import asyncio
import pathlib
import re
import time
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

from src.state import CircuitBreakerState, CircuitBreakerStatus


def timeout_wrapper(seconds: float):
    """Decorator to apply asyncio timeout to a node function."""

    def decorator(func: Callable):
        import inspect

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Check if it's definitely an async function
                if inspect.iscoroutinefunction(func):
                    coro = func(*args, **kwargs)
                    return await asyncio.wait_for(coro, timeout=seconds)

                # Otherwise, it might be sync or a wrapper (like LangSmith)
                # To avoid blocking the main loop for slow sync functions, we use to_thread.
                # BUT if it's a wrapper for an async function, calling it in a thread
                # will return a coroutine, which we then must await in the main loop.
                result = await asyncio.to_thread(func, *args, **kwargs)

                if inspect.isawaitable(result):
                    return await asyncio.wait_for(result, timeout=seconds)
                return result

            except TimeoutError:
                # Log timeout and inject error into state if applicable
                from src.utils.logger import StructuredLogger

                logger = StructuredLogger("timeout_wrapper")
                logger.error(f"Node {func.__name__} timed out after {seconds}s")
                # If the first arg is state, append an error
                if args and isinstance(args[0], dict) and "errors" in args[0]:
                    args[0]["errors"].append(
                        f"TIMEOUT: Node {func.__name__} exceeded {seconds}s limit."
                    )
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
        self.last_failure_time: float | None = None

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
            import inspect

            if inspect.iscoroutinefunction(func):
                res = func(*args, **kwargs)
            else:
                # Use to_thread to support sync calls and avoid blocking loop
                res = await asyncio.to_thread(func, *args, **kwargs)

            if inspect.isawaitable(res):
                result = await res
            else:
                result = res
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
            last_failure_time=datetime.fromtimestamp(self.last_failure_time)
            if self.last_failure_time
            else None,
        )


def trigger_rollback(last_valid_state: dict[str, Any], error: str) -> dict[str, Any]:
    """FR-009: Restore system to last known valid state (T030)."""
    rollback_state = last_valid_state.copy()
    if "metadata" not in rollback_state:
        rollback_state["metadata"] = {}
    rollback_state["metadata"]["rollback_triggered"] = True
    rollback_state["metadata"]["rollback_reason"] = error
    rollback_state["metadata"]["rollback_timestamp"] = datetime.now().isoformat()
    return rollback_state


def detect_cascading_failure(errors: list[str]) -> bool:
    """FR-011: Check if core streams are failing."""
    forensic_count = sum(
        1 for e in errors if any(kw in e for kw in ["FORENSIC", "CRITICAL", "FATAL"])
    )
    return forensic_count >= 3


_cb_registry: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Registry for circuit breakers per resource (T029)."""
    if name not in _cb_registry:
        _cb_registry[name] = CircuitBreaker(name)
    return _cb_registry[name]


class TokenBucketRateLimiter:
    """
    FR-011: Traffic shaping for outbound API bursts.
    Ensures we don't exceed model tier quotas.
    """

    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def consume(self, amount: float = 1.0):
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens < amount:
                wait_time = (amount - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= amount


_limiter: TokenBucketRateLimiter | None = None


def get_global_rate_limiter() -> TokenBucketRateLimiter:
    global _limiter
    if _limiter is None:
        # Defaults to 2 calls per second with burst of 5
        _limiter = TokenBucketRateLimiter(rate=2.0, capacity=5.0)
    return _limiter


# --- Restored Orchestration Helpers ---


def sanitize_repo_name(url: str) -> str:
    """Extracts a filesystem-safe name from a GitHub URL (FR-014, FR-016)."""
    # 1. Strip protocol and common domains if present
    name = re.sub(r"^https?://[^/]+/", "", url)
    # 2. Strip .git suffix
    if name.endswith(".git"):
        name = name[:-4]

    # 3. Handle special delimiters to match test requirements
    name = name.replace("..", "_")
    name = name.replace("/", "_")

    # 4. Strip leading/trailing underscores and dots (filesystem protection)
    name = name.lstrip("_").lstrip(".")

    # 5. Replace all remaining non-alphanumeric (except - and _) with underscores
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name)


def get_report_workspace(
    repo_url: str, base_dir: str = "audit/reports"
) -> pathlib.Path:
    """Creates a dedicated output directory for the audit run (FR-014)."""
    repo_name = sanitize_repo_name(repo_url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = pathlib.Path(base_dir) / repo_name / timestamp
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
