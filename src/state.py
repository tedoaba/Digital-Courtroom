import operator
import re
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """
    Base model for all state entities with strict validation.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )


class AuditRequest(StrictModel):
    """External Interface Schema for validating incoming CLI/API arguments."""

    repo: str = Field(
        ...,
        pattern=r"^https?://",
        description="Must be a valid HTTP/HTTPS URL.",
    )
    spec: str = Field(..., description="Must be a valid path to the specification PDF.")
    rubric: str = Field(
        default="rubric/week2_rubric.json",
        description="Must be a valid path to the rubric JSON.",
    )
    output: str = Field(default="audit/reports/", description="Output directory.")
    dashboard: bool = Field(default=False, description="Enable real-time TUI dashboard.")


class EvidenceClass(str, Enum):
    """Forensic classes for evidence categorisation."""

    GIT_FORENSIC = "GIT_FORENSIC"
    STATE_MANAGEMENT = "STATE_MANAGEMENT"
    ORCHESTRATION_PATTERN = "ORCHESTRATION_PATTERN"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    MODEL_DEFINITIONS = "MODEL_DEFINITIONS"
    DOCUMENT_CLAIM = "DOCUMENT_CLAIM"


class Evidence(StrictModel):
    """Represents a persistent forensic fact captured by a detective."""

    evidence_id: str = Field(..., description="Format: {source}_{class}_{index}")
    source: Literal["repo", "docs", "vision"]
    evidence_class: EvidenceClass
    goal: str
    found: bool
    content: str | None = None
    location: str
    rationale: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime


class JudicialOutcome(BaseModel):
    """Schema for LLM output ONLY."""

    criterion_id: str
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    score: int = Field(..., ge=1, le=5)
    argument: str
    cited_evidence: list[str] = Field(default_factory=list)
    mitigations: list[str] | None = Field(default=None)
    charges: list[str] | None = Field(default=None)
    remediation: str | None = Field(default=None)


class JudicialOpinion(StrictModel):
    """INTERNAL state model for a judge's verdict."""

    opinion_id: str
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str
    score: int = Field(..., ge=1, le=5)
    argument: str
    cited_evidence: list[str]
    mitigations: list[str] | None = Field(default=None)
    charges: list[str] | None = Field(default=None)
    remediation: str | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def unwrap_judicial_opinion_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # 1. Handle common wrapper keys or single-key dicts
        wrappers = [
            "judicial_opinion",
            "opinion",
            "judicial_opinion_result",
            "result",
            "evaluation",
        ]
        if len(data) == 1:
            key = list(data.keys())[0]
            if (key in wrappers or "_" in key) and isinstance(data[key], dict):
                data = data[key]

        # 2. Map synonyms for critical fields
        field_mappings = {
            "criterion_id": [
                "criteria",
                "criterion",
                "dimension",
                "criterion_id",
                "criterion_name",
            ],
            "argument": [
                "rationale",
                "reasoning",
                "explanation",
                "justification",
                "analysis",
                "argument",
                "verdict_text",
            ],
            "score": ["rating", "verdict", "numeric_score", "point", "score", "grade"],
            "cited_evidence": [
                "cited_evidence_ids",
                "citations",
                "evidence_cited",
                "relevant_evidence",
                "cited_evidence",
                "evidence",
            ],
        }

        normalized_data = data.copy()
        for target, synonyms in field_mappings.items():
            if target not in normalized_data or normalized_data[target] is None:
                for syn in synonyms:
                    if syn in data and data[syn] is not None:
                        normalized_data[target] = data[syn]
                        break

        # 3. Normalize Score
        if "score" in normalized_data:
            val = normalized_data["score"]
            try:
                if isinstance(val, str):
                    match = re.search(r"(\d+)", val)
                    if match:
                        val = int(match.group(1))
                if isinstance(val, (float, int)) and float(val) <= 1.0 and float(val) > 0:
                    normalized_data["score"] = int(round(float(val) * 4 + 1))
                else:
                    normalized_data["score"] = int(float(val))
                normalized_data["score"] = max(1, min(5, normalized_data["score"]))
            except (ValueError, TypeError):
                normalized_data["score"] = 3

        # 4. Filter out extra fields
        allowed_fields = cls.model_fields.keys()
        final_data = {k: v for k, v in normalized_data.items() if k in allowed_fields}
        return final_data


class CriterionResult(StrictModel):
    """Final synthesized verdict."""

    criterion_id: str
    dimension_name: str
    numeric_score: int = Field(ge=1, le=5)
    reasoning: str
    relevance_confidence: float = Field(ge=0.0, le=1.0)
    judge_opinions: list[JudicialOpinion] = Field(default_factory=list)
    dissent_summary: str | None = None
    remediation: str | None = None
    applied_rules: list[str] = Field(default_factory=list)
    execution_log: dict[str, Any] = Field(default_factory=dict)
    security_violation_found: bool = False
    re_evaluation_required: bool = False


class CircuitBreakerStatus(str, Enum):
    """(013-ironclad-hardening) Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerState(StrictModel):
    """Tracks health of external API integrations."""

    resource_name: str
    status: CircuitBreakerStatus
    failure_count: int
    last_failure_time: datetime | None = None
    open_until: datetime | None = None


class EvidenceChain(BaseModel):
    """Cryptographic linkage for forensic integrity (T027)."""

    evidence_id: str
    content_hash: str
    previous_hash: str
    timestamp: datetime


class ASTFinding(StrictModel):
    """Metadata for a code structure finding via AST analysis."""

    file: str
    line: int
    node_type: str
    name: str
    details: dict = Field(default_factory=dict)


class Commit(StrictModel):
    """Metadata for a single git commit."""

    hash: str
    author: str
    date: datetime
    message: str


class AuditReport(StrictModel):
    """Final aggregated output."""

    repo_name: str
    run_date: str
    git_hash: str
    rubric_version: str
    results: dict[str, CriterionResult]
    summary: str
    remediation_plan: str | None = None
    global_score: float = Field(ge=0.0, le=5.0)


def merge_evidences(left, right):
    if not isinstance(left, dict):
        return right
    if not isinstance(right, dict):
        return left
    merged = left.copy()
    for key, val in right.items():
        if key not in merged:
            merged[key] = val
        else:
            ids = {e.evidence_id for e in merged[key]}
            merged[key].extend([e for e in val if e.evidence_id not in ids])
    return merged


def merge_criterion_results(left, right):
    if not isinstance(left, dict):
        return right
    if not isinstance(right, dict):
        return left
    merged = left.copy()
    for k, v in right.items():
        if k not in merged or v.relevance_confidence > merged[k].relevance_confidence:
            merged[k] = v
    return merged


class AgentState(TypedDict):
    repo_url: str
    pdf_path: str
    rubric_path: str
    rubric_dimensions: list[dict]
    synthesis_rules: dict[str, str]
    evidences: Annotated[dict[str, list[Evidence]], merge_evidences]
    opinions: Annotated[list[JudicialOpinion], operator.add]
    criterion_results: Annotated[dict[str, CriterionResult], merge_criterion_results]
    errors: Annotated[list[str], operator.add]
    metadata: Annotated[dict[str, Any], operator.ior]
    final_report: AuditReport
    re_eval_count: int
    re_eval_needed: bool
