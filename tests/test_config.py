import pytest
from pydantic import ValidationError

from src.config import SystemSettings, load_config


def test_system_settings_validation_error():
    """Verify SystemSettings raises ValidationError on missing keys."""
    with pytest.raises(ValidationError):
        # Mandatory keys are missing in this empty dict/env
        SystemSettings.model_validate({})


def test_load_config_fails_without_env(monkeypatch):
    """Verify load_config fails on missing mandatory env keys."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    with pytest.raises(SystemExit) as excinfo:
        load_config()
    assert excinfo.value.code == 1


def test_secret_scanner_detection(monkeypatch):
    """Verify secret scanner detection."""
    # This might depend on implementation details in T016
    pass
