import pathlib
import shutil
import time

from src.graph import create_graph
from src.nodes.report_generator import report_generator_node as report_generator
from src.utils.orchestration import sanitize_repo_name
from src.state import CriterionResult, Evidence, EvidenceClass, JudicialOpinion

def test_report_generation_speed():
    """T025: Verifies that report generation stays under 5 seconds for a typical audit."""
    # Setup mock state
    results = {
        "logic": CriterionResult(
            criterion_id="logic",
            dimension_name="Core Logic",
            numeric_score=5,
            reasoning="Perfect score.",
            relevance_confidence=1.0,
        )
    }
    
    state = {
        "repo_url": "https://github.com/org/speed-test",
        "criterion_results": results,
        "evidences": {},
        "metadata": {"correlation_id": "speed-test"},
    }
    
    start_time = time.time()
    report_generator(state)
    end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 5.0, f"Report generation took too long: {duration:.2f}s"
    
    # Cleanup
    repo_name = sanitize_repo_name("speed-test")
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name
    if report_root.exists():
        shutil.rmtree(report_root)
