from datetime import datetime

from src.nodes.justice import chief_justice_node
from src.state import AgentState, Evidence, EvidenceClass, JudicialOpinion


def test_full_synthesis_workflow():
    """T023: Verify integration of multiple criteria and rules in AgentState."""
    op1 = JudicialOpinion(
        opinion_id="p_arch_1",
        judge="Prosecutor",
        criterion_id="architecture_01",
        score=2,
        argument="Bad structure",
        cited_evidence=["repo_01"],
    )
    op2 = JudicialOpinion(
        opinion_id="d_arch_1",
        judge="Defense",
        criterion_id="architecture_01",
        score=5,
        argument="It's perfect",
        cited_evidence=[],
    )
    op3 = JudicialOpinion(
        opinion_id="t_arch_1",
        judge="TechLead",
        criterion_id="architecture_01",
        score=3,
        argument="Average",
        cited_evidence=[],
    )

    # Security violation in another criterion
    op4 = JudicialOpinion(
        opinion_id="p_sec_1",
        judge="Prosecutor",
        criterion_id="security_01",
        score=1,
        argument="Critical RCE",
        cited_evidence=[],
        charges=["Security Violation: rce"],
    )
    op5 = JudicialOpinion(
        opinion_id="t_sec_1",
        judge="TechLead",
        criterion_id="security_01",
        score=5,
        argument="Functional",
        cited_evidence=[],
    )

    ev1 = Evidence(
        evidence_id="repo_01",
        source="repo",
        evidence_class=EvidenceClass.GIT_FORENSIC,
        goal="check arch",
        found=True,
        location="main.py",
        rationale="exists",
        confidence=1.0,
        timestamp=datetime.now(),
    )

    state: AgentState = {
        "repo_url": "http://test.com",
        "pdf_path": "test.pdf",
        "rubric_path": "rubric.json",
        "rubric_dimensions": [],
        "synthesis_rules": {},
        "evidences": {"repo": [ev1]},
        "opinions": [op1, op2, op3, op4, op5],
        "criterion_results": {},
        "errors": [],
        "opinion_text": "",
    }

    final_state = chief_justice_node(state)
    results = final_state["criterion_results"]

    # Architecture 01: (2*1 + 5*1 + 3*2) / 4 = 13 / 4 = 3.25 -> round 3
    assert results["architecture_01"].numeric_score == 3

    # Security 01: (1*1 + 5*2) / 3 = 11 / 3 = 3.66 -> rounded would be 4, but capped at 3
    assert results["security_01"].numeric_score == 3
    assert "SECURITY_OVERRIDE" in results["security_01"].applied_rules
