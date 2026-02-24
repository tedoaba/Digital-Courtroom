from typing import Generic, List, Literal, Optional, TypeVar
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
    data: Optional[List[T]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
