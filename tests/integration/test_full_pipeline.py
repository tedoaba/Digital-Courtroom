import pathlib
import shutil
from datetime import datetime

import pytest

from src.nodes.justice import chief_justice_node
from src.nodes.report_generator import report_generator_node as report_generator
from src.state import Evidence, EvidenceClass, JudicialOpinion
from src.utils.orchestration import sanitize_repo_name


@pytest.fixture
def complex_agent_state():
    """Provides a multi-opinion state to test node-to-node handoff."""
    ev1 = Evidence(
        evidence_id="repo_git_001",
        source="repo",
        evidence_class=EvidenceClass.GIT_FORENSIC,
        goal="check types",
        found=True,
        content="def add(a: int, b: int) -> int: return a + b",
        location="src/math.py",
        rationale="Strong typing used",
        confidence=1.0,
        timestamp=datetime.now(),
    )

    op1 = JudicialOpinion(
        opinion_id="Prosecutor_typing_1",
        judge="Prosecutor",
        criterion_id="typing",
        score=2,
        argument="Only one function has types.",
        cited_evidence=["repo_git_001"],
    )

    op2 = JudicialOpinion(
        opinion_id="TechLead_typing_1",
        judge="TechLead",
        criterion_id="typing",
        score=5,
        argument="Core logic is fully typed.",
        cited_evidence=["repo_git_001"],
        remediation="src/math.py:1 - Keep standard",
    )

    return {
        "repo_url": "https://github.com/org/complex-repo",
        "evidences": {"repo": [ev1]},
        "opinions": [op1, op2],
        "rubric_path": "rubric.json",
        "errors": [],
        "summary": "Full pipeline integration test.",
    }


def test_full_report_pipeline(complex_agent_state):
    """
    T024: Verifies the flow from Chief Justice synthesis to Report Generation.
    Checks that variance-based dissent summary is generated and rendered.
    """
    # 1. Run Chief Justice Node
    state_after_synthesis = chief_justice_node(complex_agent_state)

    assert "criterion_results" in state_after_synthesis
    assert "typing" in state_after_synthesis["criterion_results"]

    # Check that synthesis logic worked (TechLead weight 2.0, Prosecutor 1.0)
    # (2*1 + 5*2) / 3 = 12 / 3 = 4.0
    assert state_after_synthesis["criterion_results"]["typing"].numeric_score == 4

    # 2. Run Report Generator Node
    state_after_report = report_generator(state_after_synthesis)

    # 3. Verify Filesystem Artifacts
    repo_name = sanitize_repo_name(complex_agent_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name

    assert report_root.exists()

    subdirs = list(report_root.iterdir())
    latest_run = max(subdirs, key=lambda p: p.name)

    report_file = latest_run / "report.md"
    manifest_file = latest_run / "run_manifest.json"

    assert report_file.exists()
    assert manifest_file.exists()

    content = report_file.read_text()
    assert "# ⚖️ Audit Report: complex-repo" in content
    assert "4.0 / 5.0" in content
    assert "Core logic is fully typed" in content
    assert "Remediation Dashboard" in content
    assert "src/math.py:1" in content

    # Cleanup
    shutil.rmtree(report_root)


def test_judicial_note_rendering(complex_agent_state):
    """FR-015: Verifies that 'Judicial Note' is rendered for low variance."""
    # Scores 4 and 5 (variance 1)
    complex_agent_state["opinions"][0] = complex_agent_state["opinions"][0].model_copy(
        update={"score": 4},
    )

    state = report_generator(chief_justice_node(complex_agent_state))

    repo_name = sanitize_repo_name(complex_agent_state["repo_url"])
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name
    latest_run = max(list(report_root.iterdir()), key=lambda p: p.name)
    content = (latest_run / "report.md").read_text()

    assert "Judicial Note" in content
    assert "Nuanced consensus" in content
    assert "variance=1" in content

    # Cleanup
    shutil.rmtree(report_root)
