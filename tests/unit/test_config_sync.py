"""
Unit tests for JudicialSettings configuration sync.
Covers: Environment variable loading, validation (range 1–50), rejection of invalid values.
Spec: FR-003, FR-001
"""
import pytest
from pydantic import ValidationError
from src.config import JudicialSettings


class TestJudicialSettingsValidation:
    """Tests for config validation and sync."""

    def test_default_values(self):
        """Verify default values are correct."""
        settings = JudicialSettings()
        assert settings.max_concurrent_llm_calls == 5
        assert settings.retry_initial_delay == 1.0
        assert settings.retry_max_delay == 60.0
        assert settings.retry_max_attempts == 3
        assert settings.llm_call_timeout == 120.0
        assert settings.batching_enabled is False

    def test_valid_concurrency_range(self):
        """FR-001: 1-50 is valid."""
        assert JudicialSettings(max_concurrent_llm_calls=1).max_concurrent_llm_calls == 1
        assert JudicialSettings(max_concurrent_llm_calls=50).max_concurrent_llm_calls == 50

    def test_invalid_concurrency_too_low(self):
        """FR-001: < 1 should raise ValueError."""
        with pytest.raises(ValidationError) as excinfo:
            JudicialSettings(max_concurrent_llm_calls=0)
        assert "MAX_CONCURRENT_LLM_CALLS must be >= 1" in str(excinfo.value)

    def test_invalid_concurrency_too_high(self):
        """FR-001: > 50 should raise ValueError."""
        with pytest.raises(ValidationError) as excinfo:
            JudicialSettings(max_concurrent_llm_calls=51)
        assert "MAX_CONCURRENT_LLM_CALLS must be <= 50" in str(excinfo.value)

    def test_custom_values_respected(self):
        """Verify custom values are correctly applied."""
        settings = JudicialSettings(
            max_concurrent_llm_calls=10,
            retry_initial_delay=2.0,
            retry_max_delay=30.0,
            retry_max_attempts=5,
            llm_call_timeout=60.0,
            batching_enabled=True
        )
        assert settings.max_concurrent_llm_calls == 10
        assert settings.retry_initial_delay == 2.0
        assert settings.retry_max_delay == 30.0
        assert settings.retry_max_attempts == 5
        assert settings.llm_call_timeout == 60.0
        assert settings.batching_enabled is True
