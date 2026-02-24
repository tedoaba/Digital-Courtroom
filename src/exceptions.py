"""
Exception hierarchy for the Digital Courtroom framework.
Defines Retryable and Fatal exceptions to guide automated recovery strategies.
"""

class AppException(Exception):
    """Base exception for all application-specific errors."""
    def __init__(self, message: str = "An application error occurred"):
        super().__init__(message)
        self.fatal = True  # Default to True for safety unless specialized

class RetryableException(AppException):
    """Exceptions that indicate a transient failure and can be retried."""
    def __init__(self, message: str = "A transient error occurred"):
        super().__init__(message)
        self.fatal = False

class FatalException(AppException):
    """Exceptions that indicate a permanent failure and should not be retried."""
    def __init__(self, message: str = "A permanent error occurred"):
        super().__init__(message)
        self.fatal = True

class TimingError(RetryableException):
    """Raised when an operation times out (Retryable)."""
    pass

class ConnectivityError(RetryableException):
    """Raised when a network or service connection fails (Retryable)."""
    pass

class SchemaViolationError(FatalException):
    """Raised when data does not conform to the expected schema (Fatal)."""
    pass

class InvalidInputError(FatalException):
    """Raised when user input or configuration is invalid (Fatal)."""
    pass
