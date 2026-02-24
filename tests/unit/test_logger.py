import json
import logging
import io
from datetime import datetime
import pytest
from src.utils.logger import StructuredLogger, PIIRedactionFilter

def test_logger_json_structure():
    """Verify that the logger emits valid JSON and contains required fields."""
    log_capture = io.StringIO()
    logger = StructuredLogger("test_json", stream=log_capture)
    
    logger.info("Test message", event_type="test_event", correlation_id="123")
    
    log_output = log_capture.getvalue().strip()
    log_json = json.loads(log_output)
    
    assert "timestamp" in log_json
    assert "event_type" in log_json
    assert "severity" in log_json
    assert "correlation_id" in log_json
    assert "payload" in log_json
    assert log_json["payload"]["message"] == "Test message"
    assert log_json["event_type"] == "test_event"
    assert log_json["correlation_id"] == "123"

def test_timestamp_format():
    """Verify that timestamp is in RFC 3339 format with millisecond precision."""
    log_capture = io.StringIO()
    logger = StructuredLogger("test_ts", stream=log_capture)
    
    logger.info("Test timestamp")
    
    log_output = log_capture.getvalue().strip()
    log_json = json.loads(log_output)
    ts_str = log_json["timestamp"]
    
    # RFC 3339: YYYY-MM-DDTHH:MM:SS.mmmZ or offset
    # millisecond precision usually means .mmm
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        pytest.fail(f"Timestamp {ts_str} is not valid ISO format")
    
    # Check if there are some fractions of a second
    assert "." in ts_str

def test_pii_redaction_email():
    """Verify that emails are redacted from the log payload."""
    log_capture = io.StringIO()
    logger = StructuredLogger("test_pii", stream=log_capture)
    
    logger.info("User details", payload={"email": "user@example.com", "msg": "hello"})
    
    log_output = log_capture.getvalue().strip()
    assert "user@example.com" not in log_output
    assert "[REDACTED]" in log_output or "redacted" in log_output.lower()

def test_pii_redaction_api_token():
    """Verify that API tokens are redacted."""
    log_capture = io.StringIO()
    logger = StructuredLogger("test_token", stream=log_capture)
    
    logger.info("Auth event", api_key="sk-1234567890abcdef")
    
    log_output = log_capture.getvalue().strip()
    assert "sk-1234567890abcdef" not in log_output

def test_node_lifecycle_methods():
    """Verify dedicated node lifestyle methods include correct event types."""
    log_capture = io.StringIO()
    logger = StructuredLogger("test_node", stream=log_capture)
    
    logger.log_node_entry("research_node", task_id="T1")
    log_json = json.loads(log_capture.getvalue().splitlines()[-1])
    assert log_json["event_type"] == "node_entry"
    assert log_json["payload"]["node_name"] == "research_node"
    
    logger.log_evidence_created("E001", source="web")
    log_json = json.loads(log_capture.getvalue().splitlines()[-1])
    assert log_json["event_type"] == "evidence_created"
    
    logger.log_opinion_rendered("Guilty", confidence=0.9)
    log_json = json.loads(log_capture.getvalue().splitlines()[-1])
    assert log_json["event_type"] == "opinion_rendered"
    
    logger.log_verdict_delivered("Final Verdict", case_id="C100")
    log_json = json.loads(log_capture.getvalue().splitlines()[-1])
    assert log_json["event_type"] == "verdict_delivered"

def test_exception_severity_mapping():
    """Verify that exceptions are mapped to the correct log severity."""
    from src.exceptions import FatalException, RetryableException
    
    log_capture = io.StringIO()
    logger = StructuredLogger("test_severity", stream=log_capture)
    
    # Fatal Exception -> CRITICAL
    try:
        raise FatalException("Permanent failure")
    except FatalException as e:
        logger.error("Caught error", exc=e)
    
    log_json = json.loads(log_capture.getvalue().splitlines()[-1])
    # The requirement is mapping fatal to CRITICAL
    assert log_json["severity"] == "CRITICAL"
    
    # Retryable Exception -> WARNING
    try:
        raise RetryableException("Transient failure")
    except RetryableException as e:
        logger.error("Caught error", exc=e)
        
    log_json = json.loads(log_capture.getvalue().splitlines()[-1])
    assert log_json["severity"] == "WARNING"
