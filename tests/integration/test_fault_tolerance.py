"""
Integration tests for fault tolerance and partial report generation.
Verifies that the system handles node failures gracefully.
"""

import importlib
import os
import pathlib
import shutil
import sys

import pytest

from src.utils.orchestration import sanitize_repo_name


@pytest.fixture
def mock_initial_state():
    """Initial state for a simplified audit run."""
    rubric_content = {
        "dimensions": [
            {"id": "typing", "description": "Type hints usage", "source": "repo"},
        ],
        "synthesis_rules": {},
    }
    rubric_path = "tests/fault_rubric.json"
    with open(rubric_path, "w") as f:
        import json

        json.dump(rubric_content, f)

    yield {
        "repo_url": "https://github.com/test/fault-repo",
        "pdf_path": "tests/mock.pdf",
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


@pytest.mark.asyncio
async def test_detective_failure_partial_report(mock_initial_state, mocker):
    """
    US2: Verifies that if a detective fails, the system continues to ErrorHandler
    and produces a partial report.
    """
    # Create a mock PDF file to avoid ContextBuilder validation error
    with open("tests/mock.pdf", "w") as f:
        f.write("mock")

    # 1. Mock the node functions at their source
    repo_mock = mocker.patch(
        "src.nodes.detectives.repo_investigator",
        new_callable=mocker.AsyncMock,
        return_value={"errors": ["Simulated RepoInvestigator Failure"]},
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
        return_value={"opinions": []},
    )
    judge_mock.__name__ = "evaluate_criterion"

    # 2. Import graph AFTER patching
    if "src.graph" in sys.modules:
        importlib.reload(sys.modules["src.graph"])
    from src.graph import courtroom_swarm

    # Run the swarm
    final_state = await courtroom_swarm.ainvoke(mock_initial_state)

    # 3. Assertions
    assert any("Simulated RepoInvestigator Failure" in err for err in final_state["errors"])
    # final_state["errors"] might contain multiple errors (like missing PDF if not fixed)
    # Verify report was generated
    repo_name = sanitize_repo_name(mock_initial_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name

    assert report_root.exists()

    # Cleanup
    shutil.rmtree(report_root)
    if os.path.exists("tests/mock.pdf"):
        os.remove("tests/mock.pdf")


@pytest.mark.asyncio
async def test_empty_repository_handling(mock_initial_state, mocker):
    """
    US2: Verifies handling of an empty repository (missing sources).
    """
    # Create a mock PDF file
    with open("tests/mock.pdf", "w") as f:
        f.write("mock")

    # 1. Mock detectives to return empty evidence
    repo_mock = mocker.patch(
        "src.nodes.detectives.repo_investigator",
        new_callable=mocker.AsyncMock,
        return_value={"evidences": {"repo": []}},
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
        return_value={"opinions": []},
    )
    judge_mock.__name__ = "evaluate_criterion"

    from src.graph import courtroom_swarm

    # 2. Run the swarm
    final_state = await courtroom_swarm.ainvoke(mock_initial_state)

    # 3. Assertions
    assert any("FORENSIC_SOURCE_MISSING" in err for err in final_state["errors"])

    repo_name = sanitize_repo_name(mock_initial_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name
    assert report_root.exists()

    # Cleanup
    shutil.rmtree(report_root)
    if os.path.exists("tests/mock.pdf"):
        os.remove("tests/mock.pdf")
