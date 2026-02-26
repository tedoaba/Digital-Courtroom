import pytest
import time
from src.utils.orchestration import CircuitBreaker
from src.state import CircuitBreakerStatus

def test_circuit_breaker_transitions():
    """T024: Test CircuitBreaker state transitions (Closed -> Open)."""
    cb = CircuitBreaker(name="test_api", failure_threshold=2, reset_timeout=1)
    
    # Corrected: Use CircuitBreakerStatus, not CircuitBreakerState
    assert cb.state == CircuitBreakerStatus.CLOSED
    
    # First failure
    cb.record_failure()
    assert cb.state == CircuitBreakerStatus.CLOSED
    
    # Second failure (threshold reached)
    cb.record_failure()
    assert cb.state == CircuitBreakerStatus.OPEN
    
    # Try call when open
    assert not cb.can_execute()
    
    # Wait for reset timeout
    time.sleep(1.2)
    assert cb.can_execute() 
    assert cb.state == CircuitBreakerStatus.HALF_OPEN
    
def test_circuit_breaker_recovery():
    """T024: Test Recovery (Half-Open -> Closed)."""
    cb = CircuitBreaker(name="test_api", failure_threshold=1, reset_timeout=0.1)
    cb.record_failure()
    assert cb.state == CircuitBreakerStatus.OPEN
    
    time.sleep(0.2)
    assert cb.can_execute()
    
    # Success in Half-Open
    cb.record_success()
    assert cb.state == CircuitBreakerStatus.CLOSED
