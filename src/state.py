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
        Robustly unwrap and normalize LLM outputs.
        Handles:
        - Common wrapper keys ('judicial_opinion', 'opinion', etc.)
        - Field name synonyms (rationale -> argument, criteria -> criterion_id)
        - Score normalization (0-1 float -> 1-5 int)
        - Missing optional fields
        """
        if not isinstance(data, dict):
            return data

        # 1. Handle common wrapper keys
        wrappers = ["judicial_opinion", "opinion", "judicial_opinion_result", "result", "evaluation"]
        if len(data) == 1:
            key = list(data.keys())[0]
            # If the only key is in wrappers OR it matches a likely criterion name (e.g. 'state_management_rigor')
            if (key in wrappers or "_" in key) and isinstance(data[key], dict):
                data = data[key]

        # 2. Map synonyms for critical fields
        field_mappings = {
            "criterion_id": ["criteria", "criterion", "dimension", "criterion_id", "criterion_name"],
            "argument": ["rationale", "reasoning", "explanation", "justification", "analysis", "argument"],
            "score": ["rating", "verdict", "numeric_score", "point", "score"],
            "cited_evidence": ["cited_evidence_ids", "citations", "evidence_cited", "relevant_evidence", "cited_evidence"]
        }

        normalized_data = data.copy()
        for target, synonyms in field_mappings.items():
            if target not in normalized_data or normalized_data[target] is None:
                for syn in synonyms:
                    if syn in data and data[syn] is not None:
                        normalized_data[target] = data[syn]
                        break

        # 3. Normalize Score (handle 0-1 float or strings)
        if "score" in normalized_data:
            val = normalized_data["score"]
            try:
                # If it's a float like 0.6 or 0.85
                if isinstance(val, (float, str)) and float(val) <= 1.0 and float(val) >= 0:
                    # Scale 0-1 to 1-5: round(val * 4 + 1)
                    normalized_data["score"] = int(round(float(val) * 4 + 1))
                else:
                    normalized_data["score"] = int(float(val))
                
                # Clamp to 1-5
                normalized_data["score"] = max(1, min(5, normalized_data["score"]))
            except (ValueError, TypeError):
                normalized_data["score"] = 3 # Neutral fallback for unparseable scores

        # 4. Ensure cited_evidence is a list
        if "cited_evidence" in normalized_data:
            if isinstance(normalized_data["cited_evidence"], str):
                normalized_data["cited_evidence"] = [normalized_data["cited_evidence"]]
            elif not isinstance(normalized_data["cited_evidence"], list):
                normalized_data["cited_evidence"] = []

        # 5. Filter out extra fields to prevent 'extra="forbid"' errors if LLM added stuff
        # We only keep fields defined in the model
        allowed_fields = cls.model_fields.keys()
        final_data = {k: v for k, v in normalized_data.items() if k in allowed_fields}
        
        return final_data


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
