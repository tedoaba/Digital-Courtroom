from datetime import datetime
from enum import Enum
import hashlib
import operator
from typing import Annotated, Any, Literal, Optional, TypedDict

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    A Pydantic model representing a single judge's verdict on a single criterion.
    """

    opinion_id: str = Field(..., description="Unique ID (format: {judge}_{criterion_id}_{timestamp})")
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str = Field(..., description="ID from the rubric")
    score: int = Field(..., ge=1, le=5)
    argument: str = Field(..., description="Detailed reasoning text")
    cited_evidence: list[str] = Field(..., description="List of evidence_id strings")
    mitigations: Optional[list[str]] = Field(default=None, description="Optional list of strings (Defense only)")
    charges: Optional[list[str]] = Field(default=None, description="Optional list of strings (Prosecutor only)")
    remediation: Optional[str] = Field(default=None, description="Optional string recommendation (TechLead only)")
    
    @model_validator(mode="before")
    @classmethod
    def unwrap_judicial_opinion_keys(cls, data: Any) -> Any:
        """
        Robustly unwrap keys like 'judicial_opinion', 'opinion', 'judicial_opinion_result'
        that some LLMs add even when asked for raw JSON.
        """
        if not isinstance(data, dict):
            return data
            
        # Common wrapper keys
        wrappers = ["judicial_opinion", "opinion", "judicial_opinion_result", "result", "evaluation"]
        
        # Check if only ONE key exists and it's in our wrapper list
        if len(data) == 1:
            key = list(data.keys())[0]
            if key in wrappers and isinstance(data[key], dict):
                return data[key]
            
        # Check if criterion_id or score is missing at top level but present in a nested dict
        if "score" not in data or "criterion_id" not in data:
            for val in data.values():
                if isinstance(val, dict) and "score" in val and "criterion_id" in val:
                    return val
                    
        return data


class CriterionResult(StrictModel):
    """
    The final verdict for a specific rubric dimension, synthesized from multiple judicial opinions.
    """

    criterion_id: str
    numeric_score: int = Field(ge=1, le=5)
    reasoning: str
    relevance_confidence: float = Field(ge=0.0, le=1.0)
    judge_opinions: list[JudicialOpinion] = Field(description="The opinions used for synthesis (1-3)")
    dissent_summary: Optional[str] = Field(default=None, description="Markdown summary of conflict if variance > 2")
    remediation: Optional[str] = Field(default=None, description="Combined unique technical fix instructions")
    applied_rules: list[str] = Field(default_factory=list, description="Rules triggered (e.g., SECURITY_OVERRIDE)")
    execution_log: dict[str, Any] = Field(default_factory=dict, description="Data trace of calculation steps")
    security_violation_found: bool = False
    re_evaluation_required: bool = False


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

    repo_name: str
    run_date: str
    git_hash: str
    rubric_version: str
    results: dict[str, CriterionResult]
    summary: str
    remediation_plan: Optional[str] = None
    global_score: float = Field(ge=0.0, le=5.0, description="Weighted average score (1 decimal)")


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

    # --- Orchestration Fields (E2E Wiring) ---

    # Metadata manifest data (merged dictionary).
    metadata: Annotated[dict[str, Any], operator.ior]

    # Final report object.
    final_report: AuditReport

    # Re-evaluation tracking.
    re_eval_count: int
    re_eval_needed: bool
