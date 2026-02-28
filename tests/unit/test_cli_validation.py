import pytest
from pydantic import ValidationError

from src.state import AuditRequest


def test_valid_audit_request():
    """Test that a basic compliant AuditRequest passes validation."""
    req = AuditRequest(
        repo="https://github.com/my/project",
        spec="requirements.pdf",
        rubric="rubric.json",
    )
    assert req.repo == "https://github.com/my/project"
    assert req.spec == "requirements.pdf"
    assert req.rubric == "rubric.json"
    assert req.dashboard is False
    assert req.output == "audit/reports/"


def test_audit_request_invalid_url():
    """Test that non-HTTP/HTTPS URLs are rejected by regex validation."""
    with pytest.raises(ValidationError) as exc:
        AuditRequest(
            repo="ftp://github.com/my/project",  # Invalid protocol
            spec="requirements.pdf",
            rubric="rubric.json",
        )
    assert "String should match pattern" in str(exc.value)

    with pytest.raises(ValidationError) as exc2:
        AuditRequest(
            repo="just-a-string",  # Invalid format
            spec="reqs.pdf",
            rubric="rubric.json",
        )
    assert "String should match pattern" in str(exc2.value)


def test_audit_request_missing_required_fields():
    """Test that omitting required fields raises validation error."""
    with pytest.raises(ValidationError) as exc:
        AuditRequest()
    assert "Field required" in str(exc.value)

    with pytest.raises(ValidationError) as exc2:
        AuditRequest(repo="https://github.com/my/project")
    assert "Field required" in str(exc2.value)


def test_audit_request_extra_fields_forbidden():
    """Test that unexpected/extra CLI arguments are rejected to prevent injection."""
    with pytest.raises(ValidationError) as exc:
        AuditRequest(
            repo="https://github.com/my/project",
            spec="req.pdf",
            malicious_payload="rm -rf /",
        )
    assert "Extra inputs are not permitted" in str(exc.value)
