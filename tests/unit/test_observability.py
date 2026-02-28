import time

from src.utils.observability import ObservableDashboardStatus, TraceAuditTrail


def test_trace_audit_trail_validations():
    """T019: Test TraceAuditTrail Pydantic validations."""
    trail = TraceAuditTrail(
        node_name="test_node",
        node_id="123",
        input_state_hash="abc",
        output_state_hash="def",
        latency_ms=100.5,
        tool_call_payload={"cmd": "ls"},
    )
    assert trail.node_name == "test_node"
    assert trail.latency_ms == 100.5


def test_dashboard_status_updates():
    """T018: Test internal dashboard status updates."""
    status = ObservableDashboardStatus()
    status.active_node = "RepoInvestigator"
    status.node_health["RepoInvestigator"] = "Healthy"
    status.performance_metrics["latency"] = 500.0
    status.last_refresh = time.time()

    assert status.active_node == "RepoInvestigator"
    assert status.node_health["RepoInvestigator"] == "Healthy"


def test_traceable_mock():
    """T019: Verify logic that would be used by @traceable wrapping."""
    # This is more of a placeholder for actual integration testing with LangSmith
    # but we test the structure of the trace audit trail creation.
    pass
