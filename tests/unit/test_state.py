from datetime import datetime

import pytest
from pydantic import ValidationError

from src.state import (
    AuditReport,
    CriterionResult,
    Evidence,
    EvidenceClass,
    JudicialOpinion,
    StrictModel,
    merge_criterion_results,
    merge_evidences,
)


def test_strict_model_extra_fields():
    """Test that extra fields are forbidden in StrictModel."""

    class MyModel(StrictModel):
        name: str

    with pytest.raises(ValidationError) as exc_info:
        MyModel(name="test", extra="field")  # type: ignore

    assert "extra inputs are not permitted" in str(exc_info.value).lower()


def test_strict_model_strict_types():
    """Test that type coercion is forbidden in StrictModel."""

    class MyModel(StrictModel):
        count: int

    with pytest.raises(ValidationError) as exc_info:
        MyModel(count="5")  # type: ignore

    assert "input should be a valid integer" in str(exc_info.value).lower()


def test_strict_model_frozen():
    """Test that models are immutable (frozen)."""

    class MyModel(StrictModel):
        name: str

    obj = MyModel(name="original")
    with pytest.raises(ValidationError):
        obj.name = "changed"  # type: ignore


# --- Evidence Validation ---


def test_evidence_validation_bounds():
    """Test that Evidence confidence is constrained to [0, 1]."""
    common = {
        "evidence_id": "repo_ast_1",
        "source": "repo",
        "evidence_class": EvidenceClass.GIT_FORENSIC,
        "goal": "Verify goal",
        "found": True,
        "content": "content",
        "location": "location",
        "rationale": "rationale",
        "timestamp": datetime.now(),
    }

    # Valid bounds
    Evidence(**{**common, "confidence": 0.0})
    Evidence(**{**common, "confidence": 1.0})
    Evidence(**{**common, "confidence": 0.5})

    # Invalid - high
    with pytest.raises(ValidationError) as exc_info:
        Evidence(**{**common, "confidence": 1.1})
    assert "confidence" in str(exc_info.value)

    # Invalid - low
    with pytest.raises(ValidationError) as exc_info:
        Evidence(**{**common, "confidence": -0.1})
    assert "confidence" in str(exc_info.value)


def test_judicial_opinion_defaults():
    """Test that JudicialOpinion has correct defaults for metadata."""
    opinion = JudicialOpinion(text="test opinion")
    assert opinion.case_id == "Unknown"
    assert opinion.court_name == "Unknown"
    assert opinion.text == "test opinion"


def test_judicial_opinion_explicit():
    """Test that JudicialOpinion accepts explicit values."""
    opinion = JudicialOpinion(
        text="test opinion",
        case_id="123",
        court_name="Supreme Court",
        metadata={"key": "value"},
    )
    assert opinion.case_id == "123"
    assert opinion.court_name == "Supreme Court"
    assert opinion.metadata["key"] == "value"


# --- Parallel State Merging ---


def test_merge_evidences_deduplication():
    """Test that merge_evidences deduplicates items based on evidence_id."""
    common = {
        "source": "repo",
        "evidence_class": EvidenceClass.GIT_FORENSIC,
        "goal": "Verify goal",
        "found": True,
        "location": "location",
        "rationale": "rationale",
        "confidence": 0.5,
        "timestamp": datetime.now(),
    }

    e1 = Evidence(evidence_id="id1", content="content1", **common)
    e2 = Evidence(evidence_id="id1", content="content1", **common)
    e3 = Evidence(evidence_id="id2", content="different content", **common)

    left = {"key": [e1]}
    right = {"key": [e2, e3]}

    merged = merge_evidences(left, right)

    # e1 and e2 have same evidence_id, so e2 should be deduplicated
    assert len(merged["key"]) == 2
    assert merged["key"][0].evidence_id == "id1"
    assert merged["key"][1].evidence_id == "id2"


def test_merge_evidences_type_error():
    """Test that merge_evidences raises TypeError on invalid types."""
    with pytest.raises(TypeError) as exc_info:
        merge_evidences("not a dict", {})  # type: ignore
    assert "expects dicts" in str(exc_info.value)


def test_merge_criterion_results_confidence():
    """Test that merge_criterion_results picks the one with highest confidence."""
    r1 = CriterionResult(
        criterion_id="crit",
        numeric_score=3,
        reasoning="low conf",
        relevance_confidence=0.4,
    )
    r2 = CriterionResult(
        criterion_id="crit",
        numeric_score=5,
        reasoning="high conf",
        relevance_confidence=0.9,
    )

    left = {"crit": r1}
    right = {"crit": r2}

    merged = merge_criterion_results(left, right)
    assert merged["crit"].relevance_confidence == 0.9
    assert merged["crit"].numeric_score == 5


# --- Criterion Scoring Constraints ---


def test_criterion_result_score_bounds():
    """Test that CriterionResult score is constrained to [1, 5]."""
    # Valid
    CriterionResult(
        criterion_id="c",
        numeric_score=1,
        reasoning="r",
        relevance_confidence=0.5,
    )
    CriterionResult(
        criterion_id="c",
        numeric_score=5,
        reasoning="r",
        relevance_confidence=0.5,
    )

    # Invalid - high
    with pytest.raises(ValidationError) as exc_info:
        CriterionResult(
            criterion_id="c",
            numeric_score=6,
            reasoning="r",
            relevance_confidence=0.5,
        )
    assert "numeric_score" in str(exc_info.value)

    # Invalid - low
    with pytest.raises(ValidationError) as exc_info:
        CriterionResult(
            criterion_id="c",
            numeric_score=0,
            reasoning="r",
            relevance_confidence=0.5,
        )
    assert "numeric_score" in str(exc_info.value)


def test_audit_report_weighted_score():
    """Test global_score calculation with weights and security overrides."""
    r1 = CriterionResult(
        criterion_id="architecture_1",
        numeric_score=5,
        reasoning="good",
        relevance_confidence=1.0,
    )
    r2 = CriterionResult(
        criterion_id="security_1",
        numeric_score=5,
        reasoning="flaw found",
        relevance_confidence=1.0,
        security_violation_found=True,  # Should be capped at 3
    )

    report = AuditReport(
        results={"architecture_1": r1, "security_1": r2},
        summary="Audit summary",
    )

    # Expected: (5 * 1.5 + 3 * 2.0) / (1.5 + 2.0)
    # (7.5 + 6.0) / 3.5 = 13.5 / 3.5 = 3.857... -> rounded to 3.9
    assert report.global_score == 3.9


def test_audit_report_empty_results():
    """Test global_score for empty results."""
    report = AuditReport(results={}, summary="No results available")
    assert report.global_score == 0.0


def test_merge_evidences_new_key():
    """Test merge_evidences when a new key is added."""
    common = {
        "source": "repo",
        "evidence_class": EvidenceClass.GIT_FORENSIC,
        "goal": "Verify goal",
        "found": True,
        "location": "location",
        "rationale": "rationale",
        "confidence": 0.5,
        "timestamp": datetime.now(),
    }
    e1 = Evidence(evidence_id="id1", content="c1", **common)
    e2 = Evidence(evidence_id="id2", content="c2", **common)

    left = {"k1": [e1]}
    right = {"k2": [e2]}

    merged = merge_evidences(left, right)
    assert "k1" in merged
    assert "k2" in merged
    assert len(merged["k2"]) == 1


def test_merge_criterion_results_type_error():
    """Test that merge_criterion_results raises TypeError on invalid types."""
    with pytest.raises(TypeError) as exc_info:
        merge_criterion_results({}, "not a dict")  # type: ignore
    assert "expects dicts" in str(exc_info.value)
