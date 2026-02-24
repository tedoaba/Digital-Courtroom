import pytest


@pytest.fixture
def mock_env_keys(monkeypatch):
    """Fixture to provide mock API keys for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345678901234567890")
    monkeypatch.setenv("LANGCHAIN_API_KEY", "ls-test-key-12345678901234567890")
    return {
        "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
        "LANGCHAIN_API_KEY": "ls-test-key-12345678901234567890",
    }
