import pytest
import time
import shutil
import pathlib
from src.nodes.justice import report_generator, sanitize_repo_name
from src.state import CriterionResult, JudicialOpinion, Evidence, EvidenceClass
from datetime import datetime

def generate_large_state(num_criteria=10, opinions_per_criterion=3, evidence_count=50):
    """Creates a stressed AgentState with many objects."""
    evidences = []
    for i in range(evidence_count):
        evidences.append(Evidence(
            evidence_id=f"repo_git_{i:03d}",
            source="repo",
            evidence_class=EvidenceClass.GIT_FORENSIC,
            goal="scaling test",
            found=True,
            content="X" * 1000, # Large content
            location=f"src/file_{i}.py",
            rationale="Performance benchmark",
            confidence=1.0,
            timestamp=datetime.now()
        ))
    
    criterion_results = {}
    for i in range(num_criteria):
        ops = []
        for j in range(opinions_per_criterion):
            ops.append(JudicialOpinion(
                opinion_id=f"Judge_{j}_{i}",
                judge="TechLead" if j == 0 else "Prosecutor" if j == 1 else "Defense",
                criterion_id=f"crit_{i}",
                score=3,
                argument="Lorum ipsum " * 10,
                cited_evidence=[f"repo_git_{k:03d}" for k in range(0, 5)]
            ))
        
        criterion_results[f"crit_{i}"] = CriterionResult(
            criterion_id=f"crit_{i}",
            numeric_score=3,
            reasoning="Performance test result.",
            relevance_confidence=1.0,
            judge_opinions=ops,
            remediation=f"fix/file_{i}.py:10 - Optimization required"
        )
    
    return {
        "repo_url": "https://github.com/perf/scale-test",
        "evidences": {"repo": evidences},
        "criterion_results": criterion_results,
        "summary": "Benchmarking report generation speed."
    }

def test_report_generation_speed():
    """SC-003: Core report generation must be < 500ms."""
    state = generate_large_state()
    
    start_time = time.perf_counter()
    report_generator(state)
    end_time = time.perf_counter()
    
    duration_ms = (end_time - start_time) * 1000
    print(f"\nReport generated in {duration_ms:.2f}ms")
    
    # Requirement is < 500ms
    assert duration_ms < 500
    
    # Cleanup
    repo_name = sanitize_repo_name("scale-test")
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    report_root = root / "audit" / "reports" / repo_name
    if report_root.exists():
        shutil.rmtree(report_root)
