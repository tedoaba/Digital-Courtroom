from datetime import datetime
from enum import Enum
import hashlib
import operator
from typing import Annotated, Literal, Optional, TypedDict

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """
    Base model for all state entities with strict validation.
    - frozen=True: Standard immutability for processed evidence and results.
    - extra='forbid': No non-defined fields allowed.
    - strict=True: No type coercion (e.g., "5" will not be coerced to 5).
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )


class EvidenceClass(str, Enum):
    """Forensic classes for evidence categorisation."""

    GIT_FORENSIC = "GIT_FORENSIC"
    STATE_MANAGEMENT = "STATE_MANAGEMENT"
    ORCHESTRATION_PATTERN = "ORCHESTRATION_PATTERN"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    MODEL_DEFINITIONS = "MODEL_DEFINITIONS"
    DOCUMENT_CLAIM = "DOCUMENT_CLAIM"


class Evidence(StrictModel):
    """
    Represents a persistent forensic fact captured by a detective.
    Aligned with Principle XVI and FR-002.
    """

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


class JudicialOpinion(StrictModel):
    """
    The primary source document or a judge's summarized evaluation.
    """

    text: str
    case_id: str = "Unknown"
    court_name: str = "Unknown"
    metadata: dict = Field(default_factory=dict)


class CriterionResult(StrictModel):
    """
    The outcome for a single rubric criterion.
    """

    criterion_id: str
    numeric_score: int = Field(ge=1, le=5)
    reasoning: str
    relevance_confidence: float = Field(ge=0.0, le=1.0)
    security_violation_found: bool = False


class Commit(StrictModel):
    """Metadata for a single git commit."""

    hash: str
    author: str
    date: datetime
    message: str


class ASTFinding(StrictModel):
    """Metadata for a code structure finding via AST analysis."""

    file: str
    line: int
    node_type: str
    name: str
    details: dict = Field(default_factory=dict)


class AuditReport(StrictModel):
    """
    The final aggregated output of the judicial audit process.
    """

    results: dict[str, CriterionResult]
    summary: str

    @property
    def global_score(self) -> float:
        """
        Derived global audit score calculated using a weighted average.
        Per Constitution XI: Architecture (1.5), Security (2.0),
        Performance (1.2), Documentation (1.0).
        - Security Override: If violation found, score capped at 3.
        - Precision: One decimal place.
        """
        if not self.results:
            return 0.0

        weights_map = {
            "architecture": 1.5,
            "security": 2.0,
            "performance": 1.2,
            "documentation": 1.0,
        }
        default_weight = 1.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for crit_id, result in self.results.items():
            # Determine weight based on prefix
            weight = default_weight
            for prefix, w in weights_map.items():
                if crit_id.lower().startswith(prefix):
                    weight = w
                    break

            # Apply Security Override capping
            score = result.numeric_score
            if result.security_violation_found:
                score = min(score, 3)

            total_weighted_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(total_weighted_score / total_weight, 1)


# --- Reducers ---


def merge_evidences(
    left: dict[str, list[Evidence]],
    right: dict[str, list[Evidence]],
) -> dict[str, list[Evidence]]:
    """
    Dict-based merge with evidence_id deduplication.
    Aligned with Principle VI.1.
    """
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise TypeError("merge_evidences expects dicts for left and right operands")

    merged = left.copy()
    for key, evidence_list in right.items():
        if key not in merged:
            merged[key] = list(evidence_list)
        else:
            existing_ids = {e.evidence_id for e in merged[key]}
            for e in evidence_list:
                if e.evidence_id not in existing_ids:
                    merged[key].append(e)
                    existing_ids.add(e.evidence_id)
    return merged


def merge_criterion_results(
    left: dict[str, CriterionResult],
    right: dict[str, CriterionResult],
) -> dict[str, CriterionResult]:
    """
    Highest confidence wins resolution for collisions.
    """
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise TypeError(
            "merge_criterion_results expects dicts for left and right operands",
        )

    merged = left.copy()
    for k, v in right.items():
        if k not in merged or v.relevance_confidence > merged[k].relevance_confidence:
            merged[k] = v
    return merged


# --- Agent State ---


class AgentState(TypedDict):
    """
    LangGraph state definition for the Digital Courtroom.
    """

    # --- ContextBuilder Input Fields ---

    # Repository URL to audit (validated by ContextBuilder).
    repo_url: str

    # Path to the PDF report for analysis.
    pdf_path: str

    # Path to the rubric JSON file (defaults to rubric/week2_rubric.json).
    rubric_path: str

    # --- ContextBuilder Output Fields ---

    # Loaded rubric dimensions from the JSON file.
    rubric_dimensions: list[dict]

    # Loaded synthesis rules from the JSON file.
    synthesis_rules: dict[str, str]

    # --- Parallel-Safe Collections (Const. VI) ---

    # Plural per Const. VI.1; Dict-based; Fatal on mismatch.
    evidences: Annotated[dict[str, list[Evidence]], merge_evidences]

    # Plural per Const. VI.2; Collection of judge outputs.
    opinions: Annotated[list[JudicialOpinion], operator.add]

    # Best confidence results; Fatal on structural mismatch.
    criterion_results: Annotated[dict[str, CriterionResult], merge_criterion_results]

    # Traceable execution errors.
    errors: Annotated[list[str], operator.add]

    # The raw source text of the opinion.
    opinion_text: str
