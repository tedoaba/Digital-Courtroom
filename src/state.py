import operator
from typing import Annotated, TypedDict

from pydantic import BaseModel


class Evidence(BaseModel):
    """Represents a single piece of forensic evidence."""

    fact_id: str
    description: str
    source: str
    confidence: float


class JudicialOpinion(BaseModel):
    """Represents a judgment on a specific rule or standard."""

    rule_id: str
    score: float
    reasoning: str


class AppState(TypedDict):
    """
    Initial state manifest for the Digital Courtroom's LangGraph orchestration.
    Follows Constitution Principle IV (Merging state via reducers).
    """

    repo_url: str
    pdf_path: str

    # Reducers for merging results from multiple parallel nodes
    evidences: Annotated[dict[str, list[Evidence]], operator.ior]
    opinions: Annotated[list[JudicialOpinion], operator.add]
