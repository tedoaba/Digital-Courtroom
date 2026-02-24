from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceClass(str, Enum):
    """Forensic classes for evidence categorisation."""

    GIT_FORENSIC = "GIT_FORENSIC"
    STATE_MANAGEMENT = "STATE_MANAGEMENT"
    ORCHESTRATION_PATTERN = "ORCHESTRATION_PATTERN"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    MODEL_DEFINITIONS = "MODEL_DEFINITIONS"
    DOCUMENT_CLAIM = "DOCUMENT_CLAIM"


class Evidence(BaseModel):
    """Represents a persistent forensic fact."""

    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(..., description="Format: {source}_{class}_{index}")
    source: Literal["repo", "docs", "vision"]
    evidence_class: EvidenceClass
    goal: str
    found: bool
    content: Optional[str] = None
    location: str
    rationale: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime


class Commit(BaseModel):
    """Metadata for a single git commit."""

    hash: str
    author: str
    date: datetime
    message: str


class ASTFinding(BaseModel):
    """Metadata for a code structure finding via AST analysis."""

    file: str
    line: int
    node_type: str
    name: str
    details: dict = Field(default_factory=dict)

