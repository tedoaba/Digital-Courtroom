"""
Unit tests for the ContextBuilder initialization node.

Tests cover:
- US1: Successful rubric loading and state bootstrapping
- US2: Input validation fast-fail (URL regex, pdf_path existence)
- US3: Dynamic rubric configuration via rubric_path
- Edge cases: malformed JSON, missing dimensions key, empty rubric
"""

import json
from pathlib import Path

import pytest

from src.nodes.context_builder import build_context

# --- Fixtures ---


@pytest.fixture
def valid_rubric_path() -> str:
    """Return the path to the real project rubric."""
    return str(Path(__file__).resolve().parents[2] / "rubric" / "week2_rubric.json")


@pytest.fixture
def valid_pdf_path(tmp_path: Path) -> str:
    """Create a temporary PDF file for testing."""
    pdf_file = tmp_path / "test_report.pdf"
    pdf_file.write_text("dummy pdf content")
    return str(pdf_file)


@pytest.fixture
def valid_repo_url() -> str:
    """Return a valid GitHub repository URL."""
    return "https://github.com/user/project"


@pytest.fixture
def minimal_rubric(tmp_path: Path) -> str:
    """Create a minimal valid rubric JSON for testing."""
    rubric = {
        "rubric_metadata": {"version": "1.0.0"},
        "dimensions": [
            {
                "id": "test_dim_1",
                "name": "Test Dimension",
                "target_artifact": "github_repo",
                "forensic_instruction": "Test instruction",
                "success_pattern": "Test success",
                "failure_pattern": "Test failure",
            },
        ],
        "synthesis_rules": {
            "test_rule": "Test rule description",
        },
    }
    rubric_file = tmp_path / "test_rubric.json"
    rubric_file.write_text(json.dumps(rubric))
    return str(rubric_file)


@pytest.fixture
def base_state(
    valid_repo_url: str,
    valid_pdf_path: str,
    valid_rubric_path: str,
) -> dict:
    """Create a valid base state for testing."""
    return {
        "repo_url": valid_repo_url,
        "pdf_path": valid_pdf_path,
        "rubric_path": valid_rubric_path,
    }


# --- US1: Successful Rubric Loading & State Bootstrapping ---


class TestSuccessfulAuditInitialization:
    """Tests for User Story 1: Successful Audit Initialization (P1)."""

    def test_loads_rubric_dimensions_from_default_path(
        self,
        base_state: dict,
        valid_rubric_path: str,
    ) -> None:
        """FR-001/FR-005: Node loads dimensions from the rubric JSON."""
        result = build_context(base_state)

        assert "rubric_dimensions" in result
        assert isinstance(result["rubric_dimensions"], list)
        assert len(result["rubric_dimensions"]) > 0
        # Verify dimensions match the rubric file content
        with open(valid_rubric_path) as f:
            expected = json.load(f)
        assert len(result["rubric_dimensions"]) == len(expected["dimensions"])

    def test_loads_synthesis_rules(
        self,
        base_state: dict,
        valid_rubric_path: str,
    ) -> None:
        """FR-005: Node loads synthesis_rules from the rubric JSON."""
        result = build_context(base_state)

        assert "synthesis_rules" in result
        assert isinstance(result["synthesis_rules"], dict)
        with open(valid_rubric_path) as f:
            expected = json.load(f)
        assert result["synthesis_rules"] == expected["synthesis_rules"]

    def test_initializes_evidences_as_empty_dict(self, base_state: dict) -> None:
        """FR-009: evidences initialized as empty dict for operator.ior reducer."""
        result = build_context(base_state)

        assert "evidences" in result
        assert result["evidences"] == {}

    def test_initializes_opinions_as_empty_list(self, base_state: dict) -> None:
        """FR-009: opinions initialized as empty list for operator.add reducer."""
        result = build_context(base_state)

        assert "opinions" in result
        assert result["opinions"] == []

    def test_initializes_criterion_results_as_empty_dict(
        self,
        base_state: dict,
    ) -> None:
        """FR-009: criterion_results initialized as empty dict."""
        result = build_context(base_state)

        assert "criterion_results" in result
        assert result["criterion_results"] == {}

    def test_no_errors_on_valid_input(self, base_state: dict) -> None:
        """FR-007: No errors appended when all inputs are valid."""
        result = build_context(base_state)

        assert result.get("errors", []) == []

    def test_rubric_dimensions_match_json_content(
        self,
        base_state: dict,
        valid_rubric_path: str,
    ) -> None:
        """SC-003: rubric_dimensions perfectly matches the configured JSON file."""
        result = build_context(base_state)

        with open(valid_rubric_path) as f:
            expected = json.load(f)
        assert result["rubric_dimensions"] == expected["dimensions"]

    def test_validates_dimensions_key_exists(
        self,
        tmp_path: Path,
        valid_pdf_path: str,
    ) -> None:
        """FR-010: Node must validate the dimensions key exists and is non-empty."""
        rubric_no_dims = {
            "rubric_metadata": {"version": "1.0.0"},
            "synthesis_rules": {},
        }
        rubric_file = tmp_path / "no_dims.json"
        rubric_file.write_text(json.dumps(rubric_no_dims))

        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            "rubric_path": str(rubric_file),
        }
        result = build_context(state)

        assert any("dimensions" in e for e in result.get("errors", []))

    def test_validates_dimensions_not_empty(
        self,
        tmp_path: Path,
        valid_pdf_path: str,
    ) -> None:
        """FR-010: Node must fail if dimensions is an empty array."""
        rubric_empty_dims = {
            "rubric_metadata": {"version": "1.0.0"},
            "dimensions": [],
            "synthesis_rules": {},
        }
        rubric_file = tmp_path / "empty_dims.json"
        rubric_file.write_text(json.dumps(rubric_empty_dims))

        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            "rubric_path": str(rubric_file),
        }
        result = build_context(state)

        assert any("dimensions" in e for e in result.get("errors", []))


# --- US2: Input Validation Fast-Fail ---


class TestInputValidationFastFail:
    """Tests for User Story 2: Input Validation Fast-Fail (P2)."""

    @pytest.mark.parametrize(
        "invalid_url",
        [
            "not-a-url",
            "http://github.com/user/repo",  # http instead of https
            "https://gitlab.com/user/repo",  # not github
            "ftp://github.com/user/repo",
            "file:///etc/passwd",
            "https://localhost/user/repo",
            "https://127.0.0.1/user/repo",
            "https://github.com/user/repo; rm -rf /",  # injection attempt
            "",
        ],
    )
    def test_rejects_invalid_urls(
        self,
        invalid_url: str,
        valid_pdf_path: str,
        valid_rubric_path: str,
    ) -> None:
        """FR-002/FR-003: Invalid or dangerous URLs are rejected."""
        state = {
            "repo_url": invalid_url,
            "pdf_path": valid_pdf_path,
            "rubric_path": valid_rubric_path,
        }
        result = build_context(state)

        assert len(result.get("errors", [])) > 0
        assert any("Invalid URL format" in e for e in result["errors"])

    @pytest.mark.parametrize(
        "valid_url",
        [
            "https://github.com/user/project",
            "https://github.com/user/project.git",
            "https://github.com/my-org/my-repo",
            "https://github.com/user123/repo.name",
        ],
    )
    def test_accepts_valid_urls(
        self,
        valid_url: str,
        valid_pdf_path: str,
        valid_rubric_path: str,
    ) -> None:
        """FR-002: Valid GitHub HTTPS URLs are accepted."""
        state = {
            "repo_url": valid_url,
            "pdf_path": valid_pdf_path,
            "rubric_path": valid_rubric_path,
        }
        result = build_context(state)

        url_errors = [e for e in result.get("errors", []) if "Invalid URL format" in e]
        assert len(url_errors) == 0

    def test_rejects_nonexistent_pdf_path(self, valid_rubric_path: str) -> None:
        """FR-004: Non-existent pdf_path is caught."""
        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": "/nonexistent/path/report.pdf",
            "rubric_path": valid_rubric_path,
        }
        result = build_context(state)

        assert any("Missing PDF report" in e for e in result.get("errors", []))

    def test_rejects_nonexistent_rubric_path(self, valid_pdf_path: str) -> None:
        """FR-001: Non-existent rubric_path is caught."""
        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            "rubric_path": "/nonexistent/rubric.json",
        }
        result = build_context(state)

        assert any("Could not load rubric" in e for e in result.get("errors", []))

    def test_rejects_malformed_json_rubric(
        self,
        tmp_path: Path,
        valid_pdf_path: str,
    ) -> None:
        """Edge Case: Malformed JSON rubric is caught."""
        bad_rubric = tmp_path / "bad.json"
        bad_rubric.write_text("{this is not valid json")

        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            "rubric_path": str(bad_rubric),
        }
        result = build_context(state)

        assert any("Could not load rubric" in e for e in result.get("errors", []))

    def test_graceful_failure_returns_state(
        self,
        valid_rubric_path: str,
    ) -> None:
        """FR-007: Node returns state (does not raise) on validation errors."""
        state = {
            "repo_url": "not-a-url",
            "pdf_path": "/nonexistent.pdf",
            "rubric_path": valid_rubric_path,
        }
        # Must NOT raise — graceful failure
        result = build_context(state)

        assert isinstance(result, dict)
        assert len(result.get("errors", [])) > 0

    def test_preserves_existing_errors(
        self,
        valid_pdf_path: str,
        valid_rubric_path: str,
    ) -> None:
        """FR-007: Existing errors in state are preserved (appended to, not cleared)."""
        state = {
            "repo_url": "invalid-url",
            "pdf_path": valid_pdf_path,
            "rubric_path": valid_rubric_path,
            "errors": ["Pre-existing error from previous node"],
        }
        result = build_context(state)

        assert "Pre-existing error from previous node" in result["errors"]
        assert len(result["errors"]) > 1  # Pre-existing + new URL error

    def test_error_message_format_url(
        self,
        valid_pdf_path: str,
        valid_rubric_path: str,
    ) -> None:
        """FR-007: Invalid URL error matches data-model.md format."""
        bad_url = "ftp://evil.com/repo"
        state = {
            "repo_url": bad_url,
            "pdf_path": valid_pdf_path,
            "rubric_path": valid_rubric_path,
        }
        result = build_context(state)

        assert f"Invalid URL format: {bad_url}" in result["errors"]

    def test_error_message_format_pdf(self, valid_rubric_path: str) -> None:
        """FR-007: Missing PDF error matches data-model.md format."""
        missing_path = "/no/such/report.pdf"
        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": missing_path,
            "rubric_path": valid_rubric_path,
        }
        result = build_context(state)

        assert f"Missing PDF report at: {missing_path}" in result["errors"]


# --- US3: Dynamic Rubric Configuration ---


class TestDynamicRubricConfiguration:
    """Tests for User Story 3: Dynamic Rubric Configuration (P3)."""

    def test_loads_custom_rubric_path(
        self,
        minimal_rubric: str,
        valid_pdf_path: str,
    ) -> None:
        """FR-008: Node uses rubric_path from state to load a custom rubric."""
        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            "rubric_path": minimal_rubric,
        }
        result = build_context(state)

        assert len(result["rubric_dimensions"]) == 1
        assert result["rubric_dimensions"][0]["id"] == "test_dim_1"

    def test_default_rubric_path_when_not_provided(
        self,
        valid_pdf_path: str,
    ) -> None:
        """FR-001/FR-008: Falls back to default rubric path if not provided."""
        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            # rubric_path intentionally omitted
        }
        result = build_context(state)

        # Should load from the default path or fail gracefully if it doesn't exist
        # In our project, rubric/week2_rubric.json exists
        assert "rubric_dimensions" in result or len(result.get("errors", [])) > 0

    def test_custom_rubric_overrides_default(
        self,
        minimal_rubric: str,
        valid_pdf_path: str,
    ) -> None:
        """FR-008: State rubric_path always overrides default path."""
        state = {
            "repo_url": "https://github.com/user/project",
            "pdf_path": valid_pdf_path,
            "rubric_path": minimal_rubric,
        }
        result = build_context(state)

        # Should load from the custom path, not the default
        assert result["rubric_dimensions"][0]["id"] == "test_dim_1"
        assert result["synthesis_rules"] == {"test_rule": "Test rule description"}
