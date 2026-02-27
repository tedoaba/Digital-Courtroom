from datetime import UTC, datetime

from src.nodes.evidence_aggregator import aggregator_node, sanitize_path
from src.state import Evidence, EvidenceClass


def create_mock_evidence(
    id: str, source: str = "repo", location: str = "file.py"
) -> Evidence:
    return Evidence(
        evidence_id=id,
        source=source,
        evidence_class=EvidenceClass.GIT_FORENSIC,
        goal="Test",
        found=True,
        content="Test content",
        location=location,
        rationale="Test rationale",
        confidence=1.0,
        timestamp=datetime.now(UTC),
    )


def test_sanitize_path():
    # Valid relative paths
    assert sanitize_path("src/main.py") == "src/main.py"
    assert sanitize_path("./src/main.py") == "src/main.py"
    assert sanitize_path("file.py") == "file.py"

    # Absolute paths (REJECT)
    assert sanitize_path("/etc/passwd") is None
    assert sanitize_path("C:/Users/test.txt") is None

    # Traversal (REJECT)
    assert sanitize_path("../../etc/passwd") is None
    # Path that resolve back to root are okay if they stay within root
    # But for simplicity, we reject any '..' that goes above current root.
    # In my implementation, I check if it starts with the base.
    assert sanitize_path("src/../file.py") == "file.py"


def test_aggregator_node_basic_merge():
    # Setup state with some evidence
    # Note: In LangGraph, the reducer has already merged the dicts.
    # The aggregator node receives the merged state.
    state = {
        "evidences": {
            "repo": [create_mock_evidence("repo_1")],
            "docs": [create_mock_evidence("docs_1", source="docs")],
        },
        "errors": [],
    }

    result = aggregator_node(state)

    # Basic check - evidence should still be there
    assert "repo" in result["evidences"]
    assert "docs" in result["evidences"]
    assert len(result["evidences"]["repo"]) == 1
    assert result["evidences"]["repo"][0].evidence_id == "repo_1"


def test_aggregator_node_deduplication():
    # Setup state with duplicate evidence IDs in the same source
    state = {
        "evidences": {
            "repo": [
                create_mock_evidence("repo_1"),
                create_mock_evidence("repo_1"),  # Duplicate
            ],
        },
        "errors": [],
    }

    result = aggregator_node(state)

    # FR-006: Deduplicate by evidence_id
    assert len(result["evidences"]["repo"]) == 1


def test_aggregator_node_cross_reference():
    # US2: Cross-reference file paths
    state = {
        "evidences": {
            "repo": [
                create_mock_evidence("repo_1", location="src/existing.py"),
            ],
            "docs": [
                # One real file, one hallucination
                create_mock_evidence(
                    "docs_1", source="docs", location="src/existing.py"
                ),
                create_mock_evidence(
                    "docs_2", source="docs", location="src/hallucination.py"
                ),
            ],
        },
        "errors": [],
    }

    result = aggregator_node(state)

    # Check docs evidence list
    docs_evidences = result["evidences"]["docs"]
    # Should have docs_1, docs_2, and a NEW hallucination entry for docs_2
    # Wait, docs_1 is linked to src/existing.py which is in repo.
    # docs_2 is linked to src/hallucination.py which is NOT in repo.

    # The aggregator adds a new Evidence object for hallucinated paths
    hallucinations = [
        e
        for e in docs_evidences
        if e.evidence_class == EvidenceClass.DOCUMENT_CLAIM and not e.found
    ]
    assert len(hallucinations) == 1
    assert hallucinations[0].location == "src/hallucination.py"
    assert "Path cited in documentation does not exist" in hallucinations[0].rationale


def test_aggregator_node_missing_sources():
    # US3: Missing source handling
    # Case 1: Repo missing
    state = {
        "evidences": {
            "docs": [create_mock_evidence("docs_1", source="docs")],
        },
        "errors": [],
    }

    result = aggregator_node(state)
    assert "FORENSIC_SOURCE_MISSING: 'repo'" in result["errors"][0]
    assert result["metadata"]["pipeline_integrity"] == "FAILED"

    # Case 2: Vision missing (Warning only)
    state = {
        "evidences": {
            "repo": [create_mock_evidence("repo_1")],
            "docs": [create_mock_evidence("docs_1", source="docs")],
        },
        "errors": [],
    }
    result = aggregator_node(state)
    assert len(result["errors"]) == 0
    assert result["metadata"]["pipeline_integrity"] == "SUCCESS"


def test_aggregator_performance_benchmark():
    import time

    # SC-002: <50ms for datasets < 1000 items
    # Create 500 repo items and 500 doc items
    repo_items = [
        create_mock_evidence(f"repo_{i}", location=f"src/file_{i}.py")
        for i in range(500)
    ]
    doc_items = [
        create_mock_evidence(f"docs_{i}", source="docs", location=f"src/file_{i}.py")
        for i in range(500)
    ]

    state = {
        "evidences": {
            "repo": repo_items,
            "docs": doc_items,
        },
        "errors": [],
    }

    start_time = time.perf_counter()
    result = aggregator_node(state)
    end_time = time.perf_counter()

    duration_ms = (end_time - start_time) * 1000
    print(f"\nAggregation duration for 1000 items: {duration_ms:.2f}ms")
    assert duration_ms < 50, f"Performance budget exceeded: {duration_ms:.2f}ms > 50ms"


def test_integration_simulated_graph_flow():
    # US1 + US2 + US3 combined
    # Simulated detective returns
    state = {
        "evidences": {
            "repo": [create_mock_evidence("r1", location="valid.py")],
            "docs": [create_mock_evidence("d1", source="docs", location="hallu.py")],
            "vision": [
                create_mock_evidence("v1", source="vision", location="image.png")
            ],
        },
        "errors": [],
    }

    # 1. Detectives return (LangGraph merges via operator.ior/merge_evidences)
    # 2. Aggregator runs
    result = aggregator_node(state)

    # Verify consolidated output
    assert len(result["evidences"]["repo"]) == 1
    assert len(result["evidences"]["docs"]) == 2  # 1 original + 1 hallucination flag
    assert len(result["evidences"]["vision"]) == 1
    assert result["metadata"]["pipeline_integrity"] == "SUCCESS"
