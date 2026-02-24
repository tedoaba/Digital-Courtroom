import pytest
from src.exceptions import (
    AppException,
    RetryableException,
    FatalException,
    TimingError,
    ConnectivityError,
    SchemaViolationError,
    InvalidInputError,
)

def test_exception_inheritance():
    """Verify that exceptions follow the correct inheritance hierarchy."""
    assert issubclass(RetryableException, AppException)
    assert issubclass(FatalException, AppException)
    assert issubclass(TimingError, RetryableException)
    assert issubclass(ConnectivityError, RetryableException)
    assert issubclass(SchemaViolationError, FatalException)
    assert issubclass(InvalidInputError, FatalException)

def test_exception_fatal_attribute():
    """Verify that exceptions have the correct 'fatal' attribute."""
    assert RetryableException().fatal is False
    assert FatalException().fatal is True
    assert TimingError().fatal is False
    assert ConnectivityError().fatal is False
    assert SchemaViolationError().fatal is True
    assert InvalidInputError().fatal is True

def test_exception_message():
    """Verify that exceptions preserve the error message."""
    msg = "Test error message"
    exc = AppException(msg)
    assert str(exc) == msg
    
    exc = TimingError("Timeout occurred")
    assert str(exc) == "Timeout occurred"
