import datetime
from unittest.mock import AsyncMock, patch

import pytest
from langgraph.graph import END, START, StateGraph

from src.nodes.judges import evaluate_criterion, execute_judicial_layer
from src.state import AgentState, Evidence, EvidenceClass, JudicialOpinion


@pytest.mark.asyncio
@patch("src.nodes.judges.bounded_llm_call", new_callable=AsyncMock)
@patch("src.nodes.judges.get_concurrency_controller")
async def test_full_judicial_workflow(mock_controller, mock_bounded_llm_call):
    # Determine the return value inside the bounded_llm_call side_effect
    async def mock_call(**kwargs):
        agent = kwargs.get("agent", "")
        if agent == "Prosecutor":
            return JudicialOpinion(
                opinion_id="Prosecutor_test_1",
                judge="Prosecutor",
                criterion_id="test_1",
                score=2,
                argument="Critical view",
                cited_evidence=["e1"],
                charges=["Bad code"],
            )
        if agent == "Defense":
            return JudicialOpinion(
                opinion_id="Defense_test_1",
                judge="Defense",
                criterion_id="test_1",
                score=4,
                argument="Optimistic view",
                cited_evidence=["e1"],
                mitigations=["Tried hard"],
            )
        return JudicialOpinion(
            opinion_id="TechLead_test_1",
            judge="TechLead",
            criterion_id="test_1",
            score=3,
            argument="Pragmatic view",
            cited_evidence=["e1"],
            remediation="Fix it",
        )

    mock_bounded_llm_call.side_effect = mock_call

    # Build LangGraph
    builder = StateGraph(AgentState)
    builder.add_node("evaluate_criterion", evaluate_criterion)

    builder.add_conditional_edges(START, execute_judicial_layer, ["evaluate_criterion"])
    builder.add_edge("evaluate_criterion", END)

    graph = builder.compile()

    init_state = AgentState(
        rubric_dimensions=[{"id": "test_1", "description": "test criteria"}],
        evidences={
            "global": [
                Evidence(
                    evidence_id="e1",
                    source="repo",
                    evidence_class=EvidenceClass.GIT_FORENSIC,
                    goal="x",
                    found=True,
                    location="x",
                    rationale="x",
                    confidence=0.9,
                    timestamp=datetime.datetime.now(),
                ),
            ],
        },
        opinions=[],
        criterion_results={},
        errors=[],
        repo_url="",
        pdf_path="",
        rubric_path="",
        synthesis_rules={},
        opinion_text="",
    )

    final_state = await graph.ainvoke(init_state)

    # Check outcomes
    opinions = final_state.get("opinions", [])
    assert len(opinions) == 3
    judges_seen = {op.judge for op in opinions}
    assert judges_seen == {"Prosecutor", "Defense", "TechLead"}

    for op in opinions:
        assert op.criterion_id == "test_1"
        assert "e1" in op.cited_evidence
