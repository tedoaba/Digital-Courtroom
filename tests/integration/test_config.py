import pytest
import os
import json
from src.config import HardenedConfig

def test_hardened_config_loading_from_env():
    """T011: Test HardenedConfig loads variables from environment."""
    # Mock environment variables
    os.environ["COURTROOM_MODELS"] = json.dumps({"search": "gpt-4o", "judge": "claude-3-5-sonnet"})
    os.environ["COURTROOM_ENDPOINTS"] = json.dumps({"github": "https://api.github.com"})
    os.environ["COURTROOM_TIMEOUTS"] = json.dumps({"short": 5, "long": 60})
    os.environ["COURTROOM_VAULT_KEY"] = "32-byte-base64-fernet-key-here"
    
    config = HardenedConfig()
    
    assert config.models["search"] == "gpt-4o"
    assert config.models["judge"] == "claude-3-5-sonnet"
    assert config.endpoints["github"] == "https://api.github.com"
    assert config.timeouts["short"] == 5
    assert config.timeouts["long"] == 60
    assert config.vault_key.get_secret_value() == "32-byte-base64-fernet-key-here"

def test_hardened_config_validation_failure():
    """CHK001: Test HardenedConfig data type and range validation."""
    # Invalid timeout range
    os.environ["COURTROOM_TIMEOUTS"] = json.dumps({"invalid": 1000}) # Max 300
    
    with pytest.raises(Exception):
        HardenedConfig()
    
    # Empty model name (unsupported based on our validator)
    os.environ["COURTROOM_MODELS"] = json.dumps({"researcher": ""})
    with pytest.raises(Exception):
        HardenedConfig()
