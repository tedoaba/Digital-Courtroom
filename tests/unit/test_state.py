from datetime import datetime

import pytest
from pydantic import ValidationError

from src.state import (
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

    class MyModelExtra(StrictModel):
        name: str

    with pytest.raises(ValidationError) as exc_info:
        MyModelExtra(name="test", extra="field")  # type: ignore

    assert "extra inputs are not permitted" in str(exc_info.value).lower()


def test_strict_model_strict_types():
    """Test that type coercion is forbidden in StrictModel."""

    class MyModelType(StrictModel):
        count: int

    with pytest.raises(ValidationError) as exc_info:
        MyModelType(count="5")  # type: ignore

    assert "input should be a valid integer" in str(exc_info.value).lower()


def test_strict_model_frozen():
    """Test that models are immutable (frozen)."""

    class MyModelFrozen(StrictModel):
        name: str

    obj = MyModelFrozen(name="original")
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


def test_judicial_opinion_required_fields():
    """Test that JudicialOpinion requires all its core fields."""
    opinion = JudicialOpinion(
        opinion_id="test_op_1",
        judge="Prosecutor",
        criterion_id="crit_1",
        score=3,
        argument="Test argument",
        cited_evidence=["ev1"],
    )
    assert opinion.opinion_id == "test_op_1"
    assert opinion.judge == "Prosecutor"
    assert opinion.score == 3


def test_judicial_opinion_optional_fields():
    """Test that JudicialOpinion optional fields default to None."""
    opinion = JudicialOpinion(
        opinion_id="test_op_2",
        judge="Defense",
        criterion_id="crit_1",
        score=4,
        argument="Good work",
        cited_evidence=[],
    )
    assert opinion.mitigations is None
    assert opinion.charges is None
    assert opinion.remediation is None


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


def test_merge_evidences_non_dict_input():
    """Test that merge_evidences handles non-dict inputs gracefully."""
    result = merge_evidences("not a dict", {"k": []})
    assert result == {"k": []}


def test_merge_criterion_results_confidence():
    """Test that merge_criterion_results picks the one with highest confidence."""
    r1 = CriterionResult(
        criterion_id="crit",
        dimension_name="Test Dim",
        numeric_score=3,
        reasoning="low conf",
        relevance_confidence=0.4,
        judge_opinions=[],
    )
    r2 = CriterionResult(
        criterion_id="crit",
        dimension_name="Test Dim",
        numeric_score=5,
        reasoning="high conf",
        relevance_confidence=0.9,
        judge_opinions=[],
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
        dimension_name="Test Dim",
        numeric_score=1,
        reasoning="r",
        relevance_confidence=0.5,
        judge_opinions=[],
    )
    CriterionResult(
        criterion_id="c",
        dimension_name="Test Dim",
        numeric_score=5,
        reasoning="r",
        relevance_confidence=0.5,
        judge_opinions=[],
    )

    # Invalid - high
    with pytest.raises(ValidationError) as exc_info:
        CriterionResult(
            criterion_id="c",
            dimension_name="Test Dim",
            numeric_score=6,
            reasoning="r",
            relevance_confidence=0.5,
            judge_opinions=[],
        )
    assert "numeric_score" in str(exc_info.value)

    # Invalid - low
    with pytest.raises(ValidationError) as exc_info:
        CriterionResult(
            criterion_id="c",
            dimension_name="Test Dim",
            numeric_score=0,
            reasoning="r",
            relevance_confidence=0.5,
            judge_opinions=[],
        )
    assert "numeric_score" in str(exc_info.value)


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


def test_merge_criterion_results_non_dict_input():
    """Test that merge_criterion_results handles non-dict inputs gracefully."""
    result = merge_criterion_results({}, "not a dict")
    assert result == {}
