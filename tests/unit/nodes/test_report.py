import pathlib
import shutil
from datetime import datetime

import pytest

from src.nodes.report_generator import report_generator_node as report_generator
from src.state import (
    CriterionResult,
    Evidence,
    EvidenceClass,
    JudicialOpinion,
)
from src.utils.orchestration import get_report_workspace, sanitize_repo_name


@pytest.fixture
def mock_agent_state():
    """Provides a minimal AgentState for report generation testing."""
    evidence = Evidence(
        evidence_id="repo_git_001",
        source="repo",
        evidence_class=EvidenceClass.GIT_FORENSIC,
        goal="check types",
        found=True,
        content="def foo(a: int): pass",
        location="src/main.py",
        rationale="Type hints found",
        confidence=1.0,
        timestamp=datetime.now(),
    )

    opinion = JudicialOpinion(
        opinion_id="TechLead_typing_2026",
        judge="TechLead",
        criterion_id="typing",
        score=5,
        argument="Excellent use of types.",
        cited_evidence=["repo_git_001"],
        remediation="None",
    )

    result = CriterionResult(
        criterion_id="typing",
        dimension_name="Type Safety",
        numeric_score=5,
        reasoning="Synthesis report generated deterministically.",
        relevance_confidence=1.0,
        judge_opinions=[opinion],
        remediation="src/main.py:1 - Keep using types",
    )

    return {
        "repo_url": "https://github.com/user/test-repo",
        "evidences": {"repo": [evidence]},
        "criterion_results": {"typing": result},
        "opinions": [opinion],
        "rubric_path": "rubric.json",
        "errors": [],
        "summary": "This is a test summary.",
    }


def test_sanitize_repo_name():
    """Validates OS-agnostic repository name sanitization (FR-014, FR-016)."""
    assert sanitize_repo_name("my/repo") == "my_repo"
    assert sanitize_repo_name("my..repo") == "my_repo"
    assert sanitize_repo_name("repo<>|:*?") == "repo______"
    assert sanitize_repo_name("../forbidden") == "forbidden"


def test_get_report_workspace():
    """Verifies creation of timestamped audit workspace (FR-009)."""
    path = get_report_workspace("test-repo")
    try:
        assert "audit" in str(path)
        assert "test-repo" in str(path)
        assert path.exists()
        assert path.is_dir()
    finally:
        # Cleanup specific timestamp dir
        if path.exists():
            shutil.rmtree(path)


def test_report_generator_creates_files(mock_agent_state):
    """
    US1/US2: Verifies that the report_generator node creates the
    required Markdown and JSON artifacts.
    """
    # This will initially fail until report_generator is implemented
    state = report_generator(mock_agent_state)

    repo_name = sanitize_repo_name(mock_agent_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name

    assert report_root.exists()

    # Get the latest timestamped folder
    subdirs = list(report_root.iterdir())
    assert len(subdirs) > 0
    latest_run = max(subdirs, key=lambda p: p.name)

    report_file = latest_run / "report.md"
    manifest_file = latest_run / "run_manifest.json"

    assert report_file.exists(), f"Report file not found in {latest_run}"
    # US2 requirement
    assert manifest_file.exists(), f"Manifest file not found in {latest_run}"

    content = report_file.read_text()
    assert "# ⚖️ Audit Report: test-repo" in content
    assert "## 📝 Executive Summary" in content
    assert "test-repo" in content
    assert "Full automated audit completed by Digital Courtroom swarm." in content

    # US2: Manifest and Checks
    assert "## 🔍 Forensic Evidence Manifest" in content
    assert "repo_git_001" in content
    assert "Repo" in content

    # US2: Checksum Log
    assert "## 🔒 Post-Mortem & Checksum" in content
    assert "<details>" in content
    assert "repo_git_001" in content  # Should be in the raw JSON

    # Scorebox check
    assert "**5.0 / 5.0**" in content

    # Cleanup
    shutil.rmtree(report_root)


def test_evidence_truncation(mock_agent_state):
    """FR-011: Verifies that long evidence content is truncated."""
    long_content = "X" * 6000
    mock_agent_state["evidences"]["repo"][0] = mock_agent_state["evidences"]["repo"][
        0
    ].model_copy(
        update={"content": long_content},
    )

    state = report_generator(mock_agent_state)

    repo_name = sanitize_repo_name(mock_agent_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name
    latest_run = max(list(report_root.iterdir()), key=lambda p: p.name)
    report_file = latest_run / "report.md"

    content = report_file.read_text()

    # Check that truncation happened in the display manifest
    assert "[TRUNCATED]" in content

    # Check that the raw JSON log still contains the full content (Principle: reproducibility)
    assert long_content in content

    # Cleanup
    shutil.rmtree(report_root)


def test_report_generator_determinism(mock_agent_state):
    """SC-006: Verifies 100% byte-for-byte identity for identical inputs."""
    # We'll need a way to fix the timestamp for this test or ignore the timestamped dir name
    # For now, we check the content of two generated reports from the same state
    import time

    state1 = report_generator(mock_agent_state)
    time.sleep(1.1)  # Ensure unique timestamp (second resolution)
    state2 = report_generator(mock_agent_state)

    # Extract contents (ignoring the timestamped paths)
    repo_name = sanitize_repo_name(mock_agent_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name

    runs = sorted(list(report_root.iterdir()), key=lambda p: p.name)
    assert len(runs) >= 2

    content1 = (runs[-2] / "report.md").read_text()
    content2 = (runs[-1] / "report.md").read_text()

    # The "Run Date" in metadata table will differ unless we mock it
    # We'll check if they are identical after stripping the Run Date line
    lines1 = [l for l in content1.splitlines() if "Run Date" not in l]
    lines2 = [l for l in content2.splitlines() if "Run Date" not in l]

    assert lines1 == lines2

    # Cleanup
    shutil.rmtree(report_root)


def test_partial_failure_resilience(mock_agent_state):
    """US3: Verifies that the generator handles missing/empty data gracefully."""
    # Scenario: Empty criterion results
    mock_agent_state["criterion_results"] = {}
    mock_agent_state["summary"] = "Audit failed partially."

    state = report_generator(mock_agent_state)

    repo_name = sanitize_repo_name(mock_agent_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name
    latest_run = max(list(report_root.iterdir()), key=lambda p: p.name)
    report_file = latest_run / "report.md"

    content = report_file.read_text()
    assert "Overall Rating** | **0.0 / 5.0**" in content
    assert "Full automated audit completed by Digital Courtroom swarm." in content

    # Check that it didn't crash on empty loop
    assert "## 🏛️ Criterion Breakdown" in content

    # Cleanup
    shutil.rmtree(report_root)
