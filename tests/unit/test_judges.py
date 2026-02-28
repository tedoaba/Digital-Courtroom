import datetime
from unittest.mock import MagicMock, patch

from src.nodes.judges import (
    DEFENSE_PHILOSOPHY,
    PROSECUTOR_PHILOSOPHY,
    TECHLEAD_PHILOSOPHY,
    JudicialTask,
    evaluate_criterion,
    execute_judicial_layer,
)
from src.state import AgentState, Evidence, EvidenceClass, JudicialOpinion


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    if not union:
        return 0.0
    return len(intersection) / len(union)


def test_prompt_divergence_less_than_10_percent():
    p_d = calculate_jaccard_similarity(PROSECUTOR_PHILOSOPHY, DEFENSE_PHILOSOPHY)
    p_t = calculate_jaccard_similarity(PROSECUTOR_PHILOSOPHY, TECHLEAD_PHILOSOPHY)
    d_t = calculate_jaccard_similarity(DEFENSE_PHILOSOPHY, TECHLEAD_PHILOSOPHY)

    assert p_d < 0.5, f"Prosecutor and Defense similarity is {p_d}, should be < 0.5"
    assert p_t < 0.5, f"Prosecutor and TechLead similarity is {p_t}, should be < 0.5"
    assert d_t < 0.5, f"Defense and TechLead similarity is {d_t}, should be < 0.5"


def test_judicial_fan_out():
    state = AgentState(
        rubric_dimensions=[{"id": "arch_1"}, {"id": "sec_1"}],
        evidences={},
        opinions=[],
        criterion_results={},
        errors=[],
        repo_url="",
        pdf_path="",
        rubric_path="",
        synthesis_rules={},
        opinion_text="",
    )
    sends = execute_judicial_layer(state)
    assert len(sends) == 6  # 3 judges * 2 criteria
    judges = [s.node for s in sends]
    assert "evaluate_criterion" in judges
    args = [s.arg for s in sends]
    assert all("judge_name" in a and "criterion_id" in a for a in args)


def setup_mock_state():
    return AgentState(
        rubric_dimensions=[{"id": "test_crit", "description": "test criteria"}],
        evidences={
            "global": [
                Evidence(
                    evidence_id="src_cls_1",
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


@patch("src.nodes.judges.bounded_llm_call")
@patch("src.nodes.judges.get_concurrency_controller")
async def test_evaluate_criterion_evidence_citation(mock_controller, mock_bounded):
    state = setup_mock_state()
    mock_controller.return_value = MagicMock()

    mock_bounded.return_value = JudicialOpinion(
        opinion_id="Defense_test_crit_123",
        judge="Defense",
        criterion_id="test_crit",
        score=4,
        argument="Test argument",
        cited_evidence=["src_cls_1"],
        mitigations=["some mitigations"],
    )

    result = await evaluate_criterion(
        JudicialTask(
            judge_name="Defense",
            criterion_id="test_crit",
            criterion_description="test criteria",
            evidences=state["evidences"],
        ),
    )
    assert len(result["opinions"]) == 1
    op = result["opinions"][0]
    assert op.judge == "Defense"
    assert "src_cls_1" in op.cited_evidence
    assert op.mitigations == ["some mitigations"]


@patch("src.nodes.judges.bounded_llm_call")
@patch("src.nodes.judges.get_concurrency_controller")
async def test_evaluate_criterion_timeout_fallback(mock_controller, mock_bounded):
    state = setup_mock_state()
    mock_controller.return_value = MagicMock()

    mock_bounded.side_effect = Exception("HTTP Timeout")

    result = await evaluate_criterion(
        JudicialTask(
            judge_name="TechLead",
            criterion_id="test_crit",
            criterion_description="test criteria",
            evidences=state["evidences"],
        ),
    )
    assert len(result["opinions"]) == 1
    op = result["opinions"][0]
    assert op.score == 3  # Fallback score
    assert "System Error" in op.argument
    assert op.judge == "TechLead"
