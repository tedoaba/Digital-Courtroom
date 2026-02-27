"""
Centralized structured logging helpers for concurrency events.
Emits structured JSON events per SC-003 spec for:
  queueing, acquired, released, retry, timeout

Each event includes agent name, dimension ID, and slot/queue counters.
"""

import json
import logging

logger = logging.getLogger("digital_courtroom.concurrency")


def _emit_event(event_data: dict, level: int = logging.INFO) -> None:
    """Emit a structured JSON log event."""
    logger.log(level, json.dumps(event_data))


def log_queueing(agent: str, dimension: str, queue_depth: int) -> None:
    """SC-003: Log when a task enters the semaphore queue."""
    _emit_event(
        {
            "event": "queueing",
            "agent": agent,
            "dimension": dimension,
            "queue_depth": queue_depth,
        }
    )


def log_acquired(agent: str, dimension: str, active_slots: int) -> None:
    """SC-003: Log when a task acquires a semaphore slot."""
    _emit_event(
        {
            "event": "acquired",
            "agent": agent,
            "dimension": dimension,
            "active_slots": active_slots,
        }
    )


def log_released(agent: str, dimension: str, active_slots: int) -> None:
    """SC-003: Log when a task releases a semaphore slot."""
    _emit_event(
        {
            "event": "released",
            "agent": agent,
            "dimension": dimension,
            "active_slots": active_slots,
        }
    )


def log_retry(
    agent: str,
    dimension: str,
    attempt: int,
    status_code: int,
    delay_s: float,
) -> None:
    """SC-003: Log a retry event with backoff details."""
    _emit_event(
        {
            "event": "retry",
            "agent": agent,
            "dimension": dimension,
            "attempt": attempt,
            "status_code": status_code,
            "delay_s": round(delay_s, 3),
        },
        level=logging.WARNING,
    )


def log_timeout(agent: str, dimension: str, timeout_s: float) -> None:
    """SC-003: Log when a request times out."""
    _emit_event(
        {
            "event": "timeout",
            "agent": agent,
            "dimension": dimension,
            "timeout_s": timeout_s,
        },
        level=logging.WARNING,
    )


def log_permanent_failure(
    agent: str,
    dimension: str,
    last_status_code: int | None,
    elapsed_s: float,
) -> None:
    """Edge Case – Persistent Failures: Log after exhausting all retries."""
    _emit_event(
        {
            "event": "permanent_failure",
            "agent": agent,
            "dimension": dimension,
            "last_status_code": last_status_code,
            "elapsed_s": round(elapsed_s, 3),
        },
        level=logging.ERROR,
    )


def log_concurrency_limit(limit: int) -> None:
    """FR-009: Log the active concurrency limit at job start."""
    _emit_event(
        {
            "event": "job_start",
            "active_concurrency_limit": limit,
        }
    )
