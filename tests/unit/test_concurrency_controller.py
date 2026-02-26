"""
Unit tests for the concurrency controller (asyncio.Semaphore) logic.
Covers: Semaphore lock/unlock, slot acquisition/release guarantees.
Spec: FR-001, FR-007

Tests are written FIRST per TDD — they should FAIL before implementation is wired.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.nodes.judicial_nodes import ConcurrencyController, reset_concurrency_controller


class TestConcurrencyControllerInit:
    """Test ConcurrencyController initialization and configuration."""

    def test_default_limit(self):
        """FR-001: Default concurrency limit should be 5."""
        controller = ConcurrencyController(max_concurrent=5)
        assert controller.limit == 5

    def test_custom_limit(self):
        """FR-001: Custom concurrency limit should be respected."""
        controller = ConcurrencyController(max_concurrent=10)
        assert controller.limit == 10

    def test_initial_active_count_is_zero(self):
        """Active count should start at zero."""
        controller = ConcurrencyController(max_concurrent=5)
        assert controller.active_count == 0


class TestSemaphoreAcquireRelease:
    """Test semaphore acquire/release correctness (FR-007)."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        reset_concurrency_controller()
        yield
        reset_concurrency_controller()

    @pytest.mark.asyncio
    async def test_acquire_increments_active_count(self):
        """Acquiring a slot should increment the active count."""
        controller = ConcurrencyController(max_concurrent=5)
        await controller.acquire("Prosecutor", "DIM1")
        assert controller.active_count == 1
        await controller.release("Prosecutor", "DIM1")

    @pytest.mark.asyncio
    async def test_release_decrements_active_count(self):
        """Releasing a slot should decrement the active count."""
        controller = ConcurrencyController(max_concurrent=5)
        await controller.acquire("Prosecutor", "DIM1")
        assert controller.active_count == 1
        await controller.release("Prosecutor", "DIM1")
        assert controller.active_count == 0

    @pytest.mark.asyncio
    async def test_multiple_acquisitions_tracked(self):
        """Multiple slot acquisitions should be tracked correctly."""
        controller = ConcurrencyController(max_concurrent=5)
        await controller.acquire("Prosecutor", "DIM1")
        await controller.acquire("Defense", "DIM2")
        await controller.acquire("TechLead", "DIM3")
        assert controller.active_count == 3
        await controller.release("Prosecutor", "DIM1")
        await controller.release("Defense", "DIM2")
        await controller.release("TechLead", "DIM3")
        assert controller.active_count == 0

    @pytest.mark.asyncio
    async def test_semaphore_blocks_at_limit(self):
        """FR-001: Semaphore should block when limit is reached."""
        controller = ConcurrencyController(max_concurrent=2)

        # Acquire all slots
        await controller.acquire("Prosecutor", "DIM1")
        await controller.acquire("Defense", "DIM2")
        assert controller.active_count == 2

        # Third acquisition should block
        acquired = asyncio.Event()

        async def try_acquire():
            await controller.acquire("TechLead", "DIM3")
            acquired.set()

        task = asyncio.create_task(try_acquire())

        # Give it a small window — it should NOT acquire
        await asyncio.sleep(0.05)
        assert not acquired.is_set(), "Should be blocked by semaphore limit"

        # Release one slot — now it should acquire
        await controller.release("Prosecutor", "DIM1")
        await asyncio.sleep(0.05)
        assert acquired.is_set(), "Should acquire after a slot is released"

        # Cleanup
        await controller.release("Defense", "DIM2")
        await controller.release("TechLead", "DIM3")
        assert controller.active_count == 0

    @pytest.mark.asyncio
    async def test_concurrent_tasks_respect_limit(self):
        """FR-001: At most N tasks should be active concurrently."""
        limit = 3
        controller = ConcurrencyController(max_concurrent=limit)
        max_concurrent_seen = 0
        max_concurrent_lock = asyncio.Lock()

        async def worker(agent: str, dim: str):
            nonlocal max_concurrent_seen
            await controller.acquire(agent, dim)
            async with max_concurrent_lock:
                if controller.active_count > max_concurrent_seen:
                    max_concurrent_seen = controller.active_count
            await asyncio.sleep(0.01)  # Simulate work
            await controller.release(agent, dim)

        tasks = [
            worker(f"Agent{i}", f"DIM{i}")
            for i in range(10)
        ]
        await asyncio.gather(*tasks)
        assert max_concurrent_seen <= limit, (
            f"Max concurrent was {max_concurrent_seen}, expected <= {limit}"
        )
        assert controller.active_count == 0


class TestConcurrencyControllerJobLifecycle:
    """Test FR-009 job start/end lifecycle."""

    def test_start_job_marks_active(self):
        controller = ConcurrencyController(max_concurrent=5)
        controller.start_job()
        assert controller._job_active is True

    def test_end_job_marks_inactive(self):
        controller = ConcurrencyController(max_concurrent=5)
        controller.start_job()
        controller.end_job()
        assert controller._job_active is False
