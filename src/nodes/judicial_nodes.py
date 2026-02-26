"""
Bounded-Concurrency Controller for Judicial LLM Calls.

Implements FR-001, FR-002, FR-007, FR-008, FR-009 from spec 012-bounded-agent-eval.
Added Circuit Breaker integration (013-ironclad-hardening).
"""
import asyncio
import logging
import random
import time
from typing import Any, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from src.config import judicial_settings
from src.utils.logging import (
    log_acquired,
    log_concurrency_limit,
    log_permanent_failure,
    log_queueing,
    log_released,
    log_retry,
    log_timeout,
)
from src.utils.orchestration import get_circuit_breaker, get_global_rate_limiter

logger = logging.getLogger(__name__)


class ConcurrencyController:
    """
    Global concurrency controller using asyncio.Semaphore (FR-001).
    """
    def __init__(self, max_concurrent: Optional[int] = None) -> None:
        self._limit = max_concurrent or judicial_settings.max_concurrent_llm_calls
        self._semaphore = asyncio.Semaphore(self._limit)
        self._active_count = 0
        self._lock = asyncio.Lock()
        self._job_active = False

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def active_count(self) -> int:
        return self._active_count

    def start_job(self) -> None:
        self._job_active = True
        log_concurrency_limit(self._limit)

    def end_job(self) -> None:
        self._job_active = False

    async def acquire(self, agent: str, dimension: str) -> None:
        async with self._lock:
            queue_depth = self._limit - self._semaphore._value
        log_queueing(agent, dimension, queue_depth)
        await self._semaphore.acquire()
        async with self._lock:
            self._active_count += 1
            active = self._active_count
        log_acquired(agent, dimension, active)

    async def release(self, agent: str, dimension: str) -> None:
        self._semaphore.release()
        async with self._lock:
            self._active_count -= 1
            active = self._active_count
        log_released(agent, dimension, active)


async def bounded_llm_call(
    controller: ConcurrencyController,
    agent: str,
    dimension: str,
    llm_callable: Any,
    settings: Optional[Any] = None,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Any:
    """
    Executes an LLM call with bounded concurrency, retries, timeouts, and circuit breaker.
    """
    conf = settings or judicial_settings
    cb = get_circuit_breaker(agent)
    
    retryer = retry(
        stop=stop_after_attempt(conf.retry_max_attempts),
        wait=wait_exponential(
            multiplier=conf.retry_initial_delay,
            min=conf.retry_initial_delay,
            max=conf.retry_max_delay,
        ) + wait_random(0, 0.5), 
        retry=retry_if_exception_type(retryable_exceptions),
        reraise=True,
        before_sleep=lambda retry_state: log_retry(
            agent=agent,
            dimension=dimension,
            attempt=retry_state.attempt_number,
            status_code=getattr(retry_state.outcome.exception(), "status_code", 0),
            delay_s=retry_state.next_action.sleep,
        )
    )

    async def _execute_inner():
        """Internal call wrapped in timeout (FR-008)."""
        try:
            return await asyncio.wait_for(
                llm_callable(), 
                timeout=conf.llm_call_timeout
            )
        except asyncio.TimeoutError:
            log_timeout(agent, dimension, conf.llm_call_timeout)
            raise

    # SC-003: Verify circuit breaker and cascading failure detection
    async def _execute_safe():
        return await cb.aexecute(_execute_inner)

    retrying_call = retryer(_execute_safe)

    start_time = time.perf_counter()
    try:
        await controller.acquire(agent, dimension)
        try:
            # SC-004: Apply traffic shaping (token bucket)
            await get_global_rate_limiter().consume()
            return await retrying_call()
        finally:
            await controller.release(agent, dimension)
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        status_code = getattr(e, "status_code", None)
        log_permanent_failure(agent, dimension, status_code, elapsed)
        raise


_controller: Optional[ConcurrencyController] = None

def get_concurrency_controller() -> ConcurrencyController:
    global _controller
    if _controller is None:
        _controller = ConcurrencyController()
    return _controller

def reset_concurrency_controller() -> None:
    global _controller
    _controller = None
