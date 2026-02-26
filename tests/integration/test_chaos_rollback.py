import pytest
import asyncio
from src.state import AgentState
from src.utils.orchestration import trigger_rollback, detect_cascading_failure

def test_rollback_simulation():
    """
    (FR-009) Verify system can restore to a last valid state.
    """
    valid_state: AgentState = {
        "repo_url": "test",
        "evidences": {"repo": []},
        "errors": [],
        "metadata": {"step": "aggregator"}
    }
    
    # Simulate a crash in a subsequent node
    error_msg = "CRITICAL: Database connection lost during Chief Justice synthesis."
    
    rolled_back = trigger_rollback(valid_state, error_msg)
    
    assert rolled_back["metadata"]["rollback_triggered"] is True
    assert rolled_back["metadata"]["rollback_reason"] == error_msg
    assert "rollback_timestamp" in rolled_back["metadata"]
    assert rolled_back["metadata"]["step"] == "aggregator" # State preserved

def test_cascading_failure_detection():
    """
    (FR-011) Verify detection of correlated failures across forensic streams.
    """
    # Healthy case
    assert detect_cascading_failure(["Small warning"]) is False
    
    # Cascading case (3+ forensic errors)
    scary_errors = [
        "FORENSIC_TIMEOUT: repo_investigator",
        "CRITICAL: doc_analyst failed",
        "FATAL: vision_inspector offline",
        "Something else"
    ]
    assert detect_cascading_failure(scary_errors) is True

@pytest.mark.asyncio
async def test_traffic_shaping_simulation():
    """
    Simulate traffic shaping/burst control.
    Verifies that repeated rapid calls are rejected or delayed if we add a limiter.
    (Placeholder implementation for future RateLimiter node)
    """
    from src.nodes.judicial_nodes import get_concurrency_controller
    controller = get_concurrency_controller()
    
    # Set limit to 1 for strict test
    controller._limit = 1
    controller._semaphore = asyncio.Semaphore(1)
    
    async def fast_call():
        await controller.acquire("test", "dim")
        await asyncio.sleep(0.1)
        await controller.release("test", "dim")
        return True

    # First call should succeed immediately
    task = asyncio.create_task(fast_call())
    await asyncio.sleep(0.01)
    
    # Second call should be blocked (semaphore at 0)
    assert controller._semaphore.locked()
    
    await task
    assert not controller._semaphore.locked()
