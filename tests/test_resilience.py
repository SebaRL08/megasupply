import pytest
from src.infrastructure.resilient_http import CircuitBreaker, CircuitOpenError

def test_breaker_opens_and_recovers():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0)
    cb.on_failure()
    cb.on_failure()
    assert cb.state == "OPEN"
    cb.before_call()
    assert cb.state == "HALF_OPEN"
    cb.on_success()
    assert cb.state == "CLOSED"

def test_breaker_blocks_calls_when_open():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
    cb.on_failure()
    with pytest.raises(CircuitOpenError):
        cb.before_call()