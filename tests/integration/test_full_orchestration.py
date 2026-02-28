"""
Integration test for the full LangGraph orchestration.
Verifies that all nodes execute in the correct order and produce artifacts.
"""

import importlib
import os
import pathlib
import shutil
import sys
from datetime import datetime

import pytest

# Remove top-level import to allow mocking before use
# from src.graph import courtroom_swarm
from src.state import Evidence, EvidenceClass, JudicialOpinion
from src.utils.orchestration import sanitize_repo_name


@pytest.fixture
def mock_initial_state():
    """Initial state for a simplified audit run."""
    # Note: We need a real-ish rubric file if context_builder is to succeed
    rubric_content = {
        "dimensions": [
            {"id": "typing", "description": "Type hints usage", "source": "repo"},
        ],
        "synthesis_rules": {},
    }
    rubric_path = "tests/mock_rubric.json"
    with open(rubric_path, "w") as f:
        import json

        json.dump(rubric_content, f)

    # Create mock.pdf to satisfy ContextBuilder validation
    with open("tests/mock.pdf", "w") as f:
        f.write("mock")

    yield {
        "repo_url": "https://github.com/orchestration/test-repo",
        "pdf_path": "tests/mock.pdf",  # Doesn't need to exist if we mock nodes
        "rubric_path": rubric_path,
        "evidences": {},
        "opinions": [],
        "criterion_results": {},
        "errors": [],
        "re_eval_count": 0,
        "re_eval_needed": False,
        "metadata": {"run_status": "STARTED"},
    }

    if os.path.exists(rubric_path):
        os.remove(rubric_path)
    if os.path.exists("tests/mock.pdf"):
        os.remove("tests/mock.pdf")


@pytest.mark.asyncio
async def test_full_swarm_execution(mock_initial_state, mocker):
    """
    Tests that the full LangGraph swarm executes correctly.
    We mock the detective and judge tools to avoid actual network/LLM calls.
    """
    # 1. Mock the node functions at their source before importing graph
    repo_mock = mocker.patch(
        "src.nodes.detectives.repo_investigator",
        new_callable=mocker.AsyncMock,
        return_value={
            "evidences": {
                "repo": [
                    Evidence(
                        evidence_id="repo_1",
                        source="repo",
                        evidence_class=EvidenceClass.GIT_FORENSIC,
                        goal="typing",
                        found=True,
                        content="typed",
                        location="main.py",
                        rationale="found types",
                        confidence=1.0,
                        timestamp=datetime.now(),
                    ),
                ],
            },
        },
    )
    repo_mock.__name__ = "repo_investigator"

    doc_mock = mocker.patch(
        "src.nodes.detectives.doc_analyst",
        new_callable=mocker.AsyncMock,
        return_value={"evidences": {"docs": []}},
    )
    doc_mock.__name__ = "doc_analyst"

    vis_mock = mocker.patch(
        "src.nodes.detectives.vision_inspector",
        new_callable=mocker.AsyncMock,
        return_value={"evidences": {"vision": []}},
    )
    vis_mock.__name__ = "vision_inspector"

    judge_mock = mocker.patch(
        "src.nodes.judges.evaluate_criterion",
        new_callable=mocker.AsyncMock,
        return_value={
            "opinions": [
                JudicialOpinion(
                    opinion_id="judge_1",
                    judge="TechLead",
                    criterion_id="typing",
                    score=5,
                    argument="Excellent",
                    cited_evidence=["repo_1"],
                ),
            ],
        },
    )
    judge_mock.__name__ = "evaluate_criterion"

    # 2. Import graph AFTER patching
    # 2. Import graph AFTER patching
    if "src.graph" in sys.modules:
        importlib.reload(sys.modules["src.graph"])
    from src.graph import courtroom_swarm

    # Run the swarm
    final_state = await courtroom_swarm.ainvoke(mock_initial_state)

    # Assertions
    assert "criterion_results" in final_state
    assert "typing" in final_state["criterion_results"]
    assert final_state["criterion_results"]["typing"].numeric_score == 5

    # Verify report was generated
    repo_name = sanitize_repo_name(mock_initial_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name

    assert report_root.exists()

    # Cleanup
    shutil.rmtree(report_root)
