import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from src.state import AgentState, Evidence, EvidenceClass, JudicialOpinion
from src.nodes.judges import execute_judicial_layer, evaluate_criterion
import datetime
from typing import Any

from langgraph.graph import StateGraph, START, END

def dummy_evaluate(state: AgentState, config: Any) -> dict:
    pass # Real node would be evaluate_criterion

@patch("src.nodes.judges.get_llm")
def test_full_judicial_workflow(mock_get_llm):
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    
    # Return different mock results based on the judge parsing
    def mock_invoke(messages):
        sys_msg = messages[0].content
        if "Prosecutor" in sys_msg:
            return JudicialOpinion(
                opinion_id="Prosecutor_test_1",
                judge="Prosecutor",
                criterion_id="test_1",
                score=2,
                argument="Critical view",
                cited_evidence=["e1"],
                charges=["Bad code"]
            )
        elif "Defense" in sys_msg:
            return JudicialOpinion(
                opinion_id="Defense_test_1",
                judge="Defense",
                criterion_id="test_1",
                score=4,
                argument="Optimistic view",
                cited_evidence=["e1"],
                mitigations=["Tried hard"]
            )
        else: # TechLead
            return JudicialOpinion(
                opinion_id="TechLead_test_1",
                judge="TechLead",
                criterion_id="test_1",
                score=3,
                argument="Pragmatic view",
                cited_evidence=["e1"],
                remediation="Fix it"
            )
            
    mock_llm.with_structured_output.return_value.invoke.side_effect = mock_invoke
    
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
                    timestamp=datetime.datetime.now()
                )
            ]
        },
        opinions=[],
        criterion_results={},
        errors=[],
        repo_url="",
        pdf_path="",
        rubric_path="",
        synthesis_rules={},
        opinion_text=""
    )
    
    final_state = graph.invoke(init_state)
    
    # Check outcomes
    opinions = final_state.get("opinions", [])
    assert len(opinions) == 3
    judges_seen = {op.judge for op in opinions}
    assert judges_seen == {"Prosecutor", "Defense", "TechLead"}
    
    for op in opinions:
        assert op.criterion_id == "test_1"
        assert "e1" in op.cited_evidence
        
