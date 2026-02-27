import asyncio
import datetime

from langgraph.graph import END, START, StateGraph

from src.nodes.judges import evaluate_criterion, execute_judicial_layer
from src.state import AgentState, Evidence, EvidenceClass


# Mock state setup
async def main():
    print("🚀 Starting Judicial Layer Mock Harness...")

    # Define state
    state = AgentState(
        repo_url="https://github.com/mock/repo",
        pdf_path="mock.pdf",
        rubric_path="rubric/week2_rubric.json",
        rubric_dimensions=[
            {
                "id": "arch_001",
                "description": "System uses a modular architecture with clear separation of concerns.",
            },
            {
                "id": "sec_001",
                "description": "Sensitive data is properly handled and redacted.",
            },
        ],
        synthesis_rules={},
        evidences={
            "architecture": [
                Evidence(
                    evidence_id="repo_arch_1",
                    source="repo",
                    evidence_class=EvidenceClass.ORCHESTRATION_PATTERN,
                    goal="Check modularity",
                    found=True,
                    content="Found modules in src/nodes and src/state.py",
                    location="src/",
                    rationale="Files are structured by responsibility.",
                    confidence=0.9,
                    timestamp=datetime.datetime.now(),
                ),
            ],
            "security": [
                Evidence(
                    evidence_id="repo_sec_1",
                    source="repo",
                    evidence_class=EvidenceClass.SECURITY_VIOLATION,
                    goal="Check PII redaction",
                    found=False,
                    content="No redaction logic found in logger.",
                    location="src/logger.py",
                    rationale="Logging raw dictionary objects without filtering.",
                    confidence=0.8,
                    timestamp=datetime.datetime.now(),
                ),
            ],
        },
        opinions=[],
        criterion_results={},
        errors=[],
        opinion_text="",
    )

    # Build graph
    builder = StateGraph(AgentState)
    builder.add_node("evaluate_criterion", evaluate_criterion)
    builder.add_conditional_edges(START, execute_judicial_layer, ["evaluate_criterion"])
    builder.add_edge("evaluate_criterion", END)
    graph = builder.compile()

    print("📊 Executing parallel judicial evaluations (6 calls)...")
    try:
        # Note: This requires API keys to actually run if not mocked.
        # For the purpose of the harness, we just want to see it run or fail with 'no API key'.
        # In a real environment, the user would provide keys.
        result = await graph.ainvoke(state)

        print(f"\n✅ Audit Complete. Generated {len(result['opinions'])} opinions.")
        for op in result["opinions"]:
            print(f"- [{op.judge}] {op.criterion_id}: Score {op.score}")
            print(f"  Reasoning: {op.argument[:100]}...")
            if op.cited_evidence:
                print(f"  Citations: {op.cited_evidence}")
    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        print("Note: Ensure GOOGLE_API_KEY is set in your .env if using Gemini.")


if __name__ == "__main__":
    asyncio.run(main())
