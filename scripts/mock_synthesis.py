"""
Mock Synthesis Script for Layer 3 Verification
"""

from datetime import datetime

from src.nodes.justice import chief_justice_node
from src.state import AgentState, Evidence, EvidenceClass, JudicialOpinion


def run_mock():
    print("--- Digital Courtroom: Chief Justice Mock Synthesis ---")

    # 1. Setup Mock State
    op1 = JudicialOpinion(
        opinion_id="p1",
        judge="Prosecutor",
        criterion_id="security_01",
        score=5,
        argument="Looks fine to me.",
        cited_evidence=[],
    )
    op2 = JudicialOpinion(
        opinion_id="d1",
        judge="Defense",
        criterion_id="security_01",
        score=5,
        argument="Everything is safe.",
        cited_evidence=[],
    )
    op3 = JudicialOpinion(
        opinion_id="t1",
        judge="TechLead",
        criterion_id="security_01",
        score=5,
        argument="Solid.",
        cited_evidence=[],
    )

    # Add a verified security violation evidence
    ev1 = Evidence(
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

    state: AgentState = {
        "repo_url": "mock://test",
        "pdf_path": "mock.pdf",
        "rubric_path": "mock.json",
        "rubric_dimensions": [],
        "synthesis_rules": {},
        "evidences": {"repo": [ev1]},
        "opinions": [op1, op2, op3],
        "criterion_results": {},
        "errors": [],
        "opinion_text": "",
    }

    # 2. Run Synthesis
    print("\n[Action] Running Chief Justice Node...")
    final_state = chief_justice_node(state)
    result = final_state["criterion_results"]["security_01"]

    # 3. Report
    print("\n[Result] Synthesis Complete:")
    print(f"  Criterion: {result.criterion_id}")
    print(
        f"  Final Score: {result.numeric_score} (Original was 5, but Security Override applied)"
    )
    print(f"  Applied Rules: {result.applied_rules}")
    print(f"  Security Violation Found: {result.security_violation_found}")
    print(f"  Execution Log Events: {result.execution_log['events']}")


if __name__ == "__main__":
    run_mock()
