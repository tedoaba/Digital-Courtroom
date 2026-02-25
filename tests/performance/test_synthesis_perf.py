import time
import pytest
from src.nodes.justice import synthesize_criterion
from src.state import JudicialOpinion

def test_synthesis_performance():
    """T024: Verify processing time for the synthesis node is < 50ms."""
    op1 = JudicialOpinion(
        opinion_id="p1", judge="Prosecutor", criterion_id="crit1", 
        score=2, argument="Bad", cited_evidence=[]
    )
    op2 = JudicialOpinion(
        opinion_id="d1", judge="Defense", criterion_id="crit1", 
        score=4, argument="Good", cited_evidence=[]
    )
    op3 = JudicialOpinion(
        opinion_id="t1", judge="TechLead", criterion_id="crit1", 
        score=3, argument="Mid", cited_evidence=[]
    )
    
    start_time = time.perf_counter()
    # Run 100 times to get a stable average
    iterations = 100
    for _ in range(iterations):
        synthesize_criterion("crit1", [op1, op2, op3], {})
    end_time = time.perf_counter()
    
    avg_duration_ms = ((end_time - start_time) / iterations) * 1000
    print(f"\nAverage synthesis duration: {avg_duration_ms:.4f}ms")
    
    assert avg_duration_ms < 50, f"Performance failed: {avg_duration_ms}ms >= 50ms"
