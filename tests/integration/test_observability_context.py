from langsmith import get_current_run_tree, traceable, tracing_context


@traceable(name="parent_function")
def parent_function(x: int):
    # This should have a parent run tree
    return child_function(x + 1)


@traceable(name="child_function")
def child_function(y: int):
    # Check if we are inside a run
    run_tree = get_current_run_tree()
    return run_tree, y * 2


def test_tracing_context_propagation(monkeypatch):
    """
    Verify that tracing context propagates correctly across functions.
    We enable tracing via environment variables for this test.
    """
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.setenv("LANGCHAIN_API_KEY", "test-key")

    with tracing_context(enabled=True):
        run_tree, result = parent_function(5)

    assert result == 12
    # If tracing is working, run_tree should not be None
    assert run_tree is not None
    assert run_tree.name == "child_function"
    # The parent should be 'parent_function'
    assert run_tree.parent_run is not None or getattr(run_tree, "parent_run_id", None) is not None
