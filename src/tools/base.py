from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

ToolStatus = Literal[
    "success",
    "failure",
    "timeout",
    "disk_limit_exceeded",
    "access_denied",
    "network_failure",
]


class ToolResult(BaseModel, Generic[T]):
    """Wrapper for a tool execution result."""

    status: ToolStatus
    data: list[T] | None = None
    error: str | None = None
    execution_time: float = 0.0
