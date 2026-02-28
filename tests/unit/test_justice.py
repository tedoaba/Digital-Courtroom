from src.nodes.justice import chief_justice_node, synthesize_criterion
from src.utils.orchestration import round_half_up, round_score


def test_round_half_up():
    """Verify standard round half up logic."""
    assert round_half_up(2.5) == 3.0
    assert round_half_up(2.49) == 2.0
    assert round_half_up(3.5) == 4.0
    assert round_half_up(2.51) == 3.0
    assert round_half_up(2.49999) == 2.0


from src.state import JudicialOpinion


def test_functionality_weight_calculation():
    """T006: Verify Tech Lead (2x) weighted average logic."""
    # (P:2*1 + D:4*1 + T:3*2) / 4 = (2 + 4 + 6) / 4 = 12 / 4 = 3.0
    scores = {"Prosecutor": 2, "Defense": 4, "TechLead": 3}
    weights = {"Prosecutor": 1.0, "Defense": 1.0, "TechLead": 2.0}

    total_weighted = sum(scores[j] * weights[j] for j in scores)
    total_weight = sum(weights[j] for j in scores)

    final_float = total_weighted / total_weight
    assert final_float == 3.0
    assert round_score(final_float) == 3

    # (P:1*1 + D:1*1 + T:5*2) / 4 = (1 + 1 + 10) / 4 = 12 / 4 = 3.0
    scores = {"Prosecutor": 1, "Defense": 1, "TechLead": 5}
    total_weighted = sum(scores[j] * weights[j] for j in scores)
    final_float = total_weighted / total_weight
    assert final_float == 3.0


def test_missing_judge_fallback():
    """T007: Verify mean calculation when a judge is missing."""
    # 2 judges: (2 + 4) / 2 = 3.0
    scores = [2, 4]
    final_float = sum(scores) / len(scores)
    assert final_float == 3.0
    assert round_score(final_float) == 3


def test_synthesize_criterion_basic():
    """Verify basic synthesis with functional weighting."""
    op1 = JudicialOpinion(
        opinion_id="p1",
        judge="Prosecutor",
        criterion_id="crit1",
        score=2,
        argument="Bad",
        cited_evidence=[],
    )
    op2 = JudicialOpinion(
        opinion_id="d1",
        judge="Defense",
        criterion_id="crit1",
        score=4,
        argument="Good",
        cited_evidence=[],
    )
    op3 = JudicialOpinion(
        opinion_id="t1",
        judge="TechLead",
        criterion_id="crit1",
        score=3,
        argument="Mid",
        cited_evidence=[],
    )

    from src.nodes.justice import synthesize_criterion

    result = synthesize_criterion("crit1", [op1, op2, op3], {})

    # (2*1 + 4*1 + 3*2) / 4 = 12 / 4 = 3
    assert result.numeric_score == 3
    assert result.re_evaluation_required is False
    assert result.dissent_summary is None


def test_synthesize_criterion_high_variance():
    """Verify high variance trigger."""
    op1 = JudicialOpinion(
        opinion_id="p1",
        judge="Prosecutor",
        criterion_id="crit1",
        score=1,
        argument="Very Bad",
        cited_evidence=[],
    )
    op2 = JudicialOpinion(
        opinion_id="d1",
        judge="Defense",
        criterion_id="crit1",
        score=5,
        argument="Very Good",
        cited_evidence=[],
    )
    op3 = JudicialOpinion(
        opinion_id="t1",
        judge="TechLead",
        criterion_id="crit1",
        score=2,
        argument="Bad",
        cited_evidence=[],
    )

    from src.nodes.justice import synthesize_criterion

    result = synthesize_criterion("crit1", [op1, op2, op3], {})

    # max(1,5,2) - min(1,5,2) = 4 > 2
    assert result.re_evaluation_required is True
    assert "Major conflict detected" in result.dissent_summary


def test_security_override_prosecutor_trigger():
    """Verify security override triggered by Prosecutor keywords."""
    op1 = JudicialOpinion(
        opinion_id="p1",
        judge="Prosecutor",
        criterion_id="crit1",
        score=1,
        argument="Potential shell injection detected.",
        cited_evidence=[],
        charges=["Security Violation: shell injection"],
    )
    op2 = JudicialOpinion(
        opinion_id="d1",
        judge="Defense",
        criterion_id="crit1",
        score=5,
        argument="It's fine.",
        cited_evidence=[],
    )
    op3 = JudicialOpinion(
        opinion_id="t1",
        judge="TechLead",
        criterion_id="crit1",
        score=5,
        argument="Works.",
        cited_evidence=[],
    )

    from src.nodes.justice import synthesize_criterion

    result = synthesize_criterion("crit1", [op1, op2, op3], {})

    # Weighted avg would be (1*1 + 5*1 + 5*2) / 4 = 16 / 4 = 4.0
    # But security override should cap it at 3.0
    assert result.numeric_score == 3
    assert "SECURITY_OVERRIDE" in result.applied_rules
    assert result.security_violation_found is True


def test_security_override_evidence_trigger():
    """Verify security override triggered by verified forensic evidence."""
    op1 = JudicialOpinion(
        opinion_id="p1",
        judge="Prosecutor",
        criterion_id="crit1",
        score=5,
        argument="Looks good",
        cited_evidence=[],
    )
    op2 = JudicialOpinion(
        opinion_id="d1",
        judge="Defense",
        criterion_id="crit1",
        score=5,
        argument="Perfect",
        cited_evidence=[],
    )
    op3 = JudicialOpinion(
        opinion_id="t1",
        judge="TechLead",
        criterion_id="crit1",
        score=5,
        argument="Solid",
        cited_evidence=[],
    )

    from datetime import datetime

    from src.state import Evidence, EvidenceClass

    # Verified security evidence
    # We need to map it in the evidences dict, usually grouped by source but here we check how justice.py looks
    sec_evidence = Evidence(
        evidence_id="repo_sec_01",
        source="repo",
        evidence_class=EvidenceClass.SECURITY_VIOLATION,
        goal="check security",
        found=True,
        location="test.py",
        rationale="os.system used",
        confidence=1.0,
        timestamp=datetime.now(),
        content="os.system('rm -rf /')",
    )

    evidences = {"repo": [sec_evidence]}

    from src.nodes.justice import synthesize_criterion

    result = synthesize_criterion("crit1", [op1, op2, op3], evidences)

    assert result.numeric_score == 3
    assert "SECURITY_OVERRIDE" in result.applied_rules


def test_fact_supremacy_penalty():
    """Verify judge score penalty for citing non-existent evidence."""
    # Defense cites 'missing_01' which is not in the evidence pool
    op1 = JudicialOpinion(
        opinion_id="p1",
        judge="Prosecutor",
        criterion_id="crit1",
        score=3,
        argument="Mid",
        cited_evidence=[],
    )
    op2 = JudicialOpinion(
        opinion_id="d1",
        judge="Defense",
        criterion_id="crit1",
        score=5,
        argument="It's fine because of X.",
        cited_evidence=["missing_01"],
    )
    op3 = JudicialOpinion(
        opinion_id="t1",
        judge="TechLead",
        criterion_id="crit1",
        score=3,
        argument="Mid",
        cited_evidence=[],
    )

    from src.nodes.justice import synthesize_criterion

    # Evidence pool is empty or does not contain 'missing_01'
    result = synthesize_criterion("crit1", [op1, op2, op3], {})

    # Original scores: P=3, D=5, T=3
    # Adjusted scores: P=3, D=5-2=3, T=3
    # Weighted avg: (3*1 + 3*1 + 3*2) / 4 = 12 / 4 = 3.0
    assert result.numeric_score == 3
    assert "FACT_SUPREMACY_PENALTY" in result.applied_rules
