"""
Integration tests for bounded evaluation with 429 retry behavior.
Covers: Retry verification at 3 attempts max, targeting status codes 429/502/503/408.
Spec: FR-002

Tests are written FIRST per TDD — they should FAIL before retry wiring is complete.
"""

import pytest

from src.config import JudicialSettings
from src.nodes.judicial_nodes import (
    ConcurrencyController,
    bounded_llm_call,
    reset_concurrency_controller,
)


class FakeHTTPError(Exception):
    """Simulates an HTTP error with a status code."""

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(message or f"HTTP {status_code}")


class TestBoundedRetryBehavior:
    """Integration tests for retry logic with bounded concurrency."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        reset_concurrency_controller()
        yield
        reset_concurrency_controller()

    @pytest.mark.asyncio
    async def test_retries_on_429_up_to_max(self):
        """FR-002: System retries on 429 up to 3 times."""
        controller = ConcurrencyController(max_concurrent=5)

        call_count = 0

        async def failing_llm_call():
            nonlocal call_count
            call_count += 1
            raise FakeHTTPError(429, "Rate limit exceeded")

        # Should exhaust 3 retries (initial + 2 retries = 3 attempts)
        settings = JudicialSettings(
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
            llm_call_timeout=5.0,
        )

        with pytest.raises(FakeHTTPError):
            await bounded_llm_call(
                controller=controller,
                agent="Prosecutor",
                dimension="DIM1",
                llm_callable=failing_llm_call,
                settings=settings,
                retryable_exceptions=(FakeHTTPError,),
            )

        assert call_count == 3, f"Expected 3 attempts, got {call_count}"

    @pytest.mark.asyncio
    async def test_retries_on_502(self):
        """FR-002: System retries on 502 (Bad Gateway)."""
        controller = ConcurrencyController(max_concurrent=5)
        call_count = 0

        async def failing_call():
            nonlocal call_count
            call_count += 1
            raise FakeHTTPError(502, "Bad Gateway")

        settings = JudicialSettings(
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
            llm_call_timeout=5.0,
        )

        with pytest.raises(FakeHTTPError):
            await bounded_llm_call(
                controller=controller,
                agent="Defense",
                dimension="DIM2",
                llm_callable=failing_call,
                settings=settings,
                retryable_exceptions=(FakeHTTPError,),
            )

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_success_after_transient_failure(self):
        """FR-002: Request succeeds after transient failures."""
        controller = ConcurrencyController(max_concurrent=5)
        call_count = 0

        async def eventually_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise FakeHTTPError(503, "Service Unavailable")
            return {"score": 4, "argument": "Valid result"}

        settings = JudicialSettings(
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
            llm_call_timeout=5.0,
        )

        result = await bounded_llm_call(
            controller=controller,
            agent="TechLead",
            dimension="DIM3",
            llm_callable=eventually_succeeds,
            settings=settings,
            retryable_exceptions=(FakeHTTPError,),
        )

        assert result == {"score": 4, "argument": "Valid result"}
        assert call_count == 3  # 2 failures + 1 success

    @pytest.mark.asyncio
    async def test_no_retry_on_non_retryable_error(self):
        """Non-retryable errors should propagate immediately."""
        controller = ConcurrencyController(max_concurrent=5)
        call_count = 0

        async def non_retryable():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid argument")

        settings = JudicialSettings(
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
            llm_call_timeout=5.0,
        )

        with pytest.raises(ValueError, match="Invalid argument"):
            await bounded_llm_call(
                controller=controller,
                agent="Prosecutor",
                dimension="DIM1",
                llm_callable=non_retryable,
                settings=settings,
                retryable_exceptions=(FakeHTTPError,),
            )

        assert call_count == 1, "Non-retryable errors should not be retried"

    @pytest.mark.asyncio
    async def test_semaphore_released_after_all_retries_exhausted(self):
        """FR-007: Semaphore must be released even after all retries fail."""
        controller = ConcurrencyController(max_concurrent=5)

        async def always_fails():
            raise FakeHTTPError(429)

        settings = JudicialSettings(
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
            llm_call_timeout=5.0,
        )

        with pytest.raises(FakeHTTPError):
            await bounded_llm_call(
                controller=controller,
                agent="Prosecutor",
                dimension="DIM1",
                llm_callable=always_fails,
                settings=settings,
                retryable_exceptions=(FakeHTTPError,),
            )

        # Semaphore should be fully released
        assert controller.active_count == 0
