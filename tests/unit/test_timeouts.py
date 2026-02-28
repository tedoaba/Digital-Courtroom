"""
Unit tests for request timeouts via asyncio.wait_for.
Covers: asyncio.TimeoutError handling after LLM_CALL_TIMEOUT.
Spec: FR-008

Tests are written FIRST per TDD — they should FAIL before timeout wiring is complete.
"""

import asyncio

import pytest

from src.config import JudicialSettings
from src.nodes.judicial_nodes import (
    ConcurrencyController,
    bounded_llm_call,
    reset_concurrency_controller,
)


class TestTimeoutBehavior:
    """Tests for FR-008: LLM call timeout handling."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        reset_concurrency_controller()
        yield
        reset_concurrency_controller()

    @pytest.mark.asyncio
    async def test_timeout_fires_for_hung_request(self):
        """FR-008: A hung LLM call should be cancelled after LLM_CALL_TIMEOUT."""
        controller = ConcurrencyController(max_concurrent=5)

        async def hung_call():
            await asyncio.sleep(10)  # Simulate hung request
            return {"score": 4}

        settings = JudicialSettings(
            llm_call_timeout=0.1,  # Very short timeout for testing
            retry_max_attempts=1,  # Don't retry, just test timeout
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
        )

        with pytest.raises((asyncio.TimeoutError, asyncio.CancelledError, Exception)):
            await bounded_llm_call(
                controller=controller,
                agent="Prosecutor",
                dimension="DIM1",
                llm_callable=hung_call,
                settings=settings,
                retryable_exceptions=(),
            )

    @pytest.mark.asyncio
    async def test_semaphore_released_after_timeout(self):
        """FR-007 + FR-008: Semaphore must be released after a timeout."""
        controller = ConcurrencyController(max_concurrent=5)

        async def hung_call():
            await asyncio.sleep(10)
            return {"score": 4}

        settings = JudicialSettings(
            llm_call_timeout=0.1,
            retry_max_attempts=1,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
        )

        try:
            await bounded_llm_call(
                controller=controller,
                agent="Prosecutor",
                dimension="DIM1",
                llm_callable=hung_call,
                settings=settings,
                retryable_exceptions=(),
            )
        except Exception:
            pass

        assert controller.active_count == 0, (
            "Semaphore slot must be released after timeout"
        )

    @pytest.mark.asyncio
    async def test_successful_call_within_timeout(self):
        """FR-008: Normal calls that complete within timeout should succeed."""
        controller = ConcurrencyController(max_concurrent=5)

        async def fast_call():
            await asyncio.sleep(0.01)
            return {"score": 5, "argument": "Excellent"}

        settings = JudicialSettings(
            llm_call_timeout=5.0,
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
        )

        result = await bounded_llm_call(
            controller=controller,
            agent="Defense",
            dimension="DIM2",
            llm_callable=fast_call,
            settings=settings,
            retryable_exceptions=(),
        )

        assert result == {"score": 5, "argument": "Excellent"}
        assert controller.active_count == 0

    @pytest.mark.asyncio
    async def test_timeout_triggers_retry_on_retryable(self):
        """FR-008: Timeout should trigger retry when TimeoutError is retryable."""
        controller = ConcurrencyController(max_concurrent=5)
        call_count = 0

        async def sometimes_hung():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                await asyncio.sleep(10)  # Hang on first 2 calls
            return {"score": 3}

        settings = JudicialSettings(
            llm_call_timeout=0.1,
            retry_max_attempts=3,
            retry_initial_delay=0.01,
            retry_max_delay=0.05,
        )

        result = await bounded_llm_call(
            controller=controller,
            agent="TechLead",
            dimension="DIM3",
            llm_callable=sometimes_hung,
            settings=settings,
            retryable_exceptions=(asyncio.TimeoutError,),
        )

        assert result == {"score": 3}
        assert call_count == 3  # 2 timeouts + 1 success
        assert controller.active_count == 0
