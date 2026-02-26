import pytest
import os
import time
import psutil
import base64
from pathlib import Path
from pydantic import SecretStr
from cryptography.fernet import Fernet
from src.utils.security import HardenedVault, SandboxEnvironment, sanitize_input, validate_output

def test_vault_encryption_decryption():
    """T009: Test AES-256 vault encryption/decryption."""
    key = Fernet.generate_key()
    vault = HardenedVault(key=SecretStr(key.decode()))
    
    secret_name = "TEST_API_KEY"
    secret_value = "super-secret-123"
    
    vault.set_secret(secret_name, secret_value)
    assert vault.get_secret(secret_name) == secret_value
    assert vault.get_secret("NON_EXISTENT") is None

def test_sandbox_resource_limiting():
    """T010: Test sandbox RAM and CPU limiting using a heavy process."""
    sandbox = SandboxEnvironment(
        root_path=Path("./tmp_sandbox"),
        memory_limit_mb=10, # Very low to trigger kill fast
        cpu_limit_cores=1,
        timeout_seconds=5
    )
    
    # Use a script that actively keeps memory in use to trigger the monitor
    heavy_script = "import time; x = bytearray(100 * 1024 * 1024); time.sleep(1)" # 100MB
    
    result = sandbox.execute_tool(["python", "-c", heavy_script])
    assert result["success"] is False
    assert "Memory limit exceeded" in result["error"]

def test_sandbox_timeout():
    """T010: Test sandbox timeout limiting."""
    sandbox = SandboxEnvironment(
        root_path=Path("./tmp_sandbox"),
        timeout_seconds=1
    )
    
    result = sandbox.execute_tool(["python", "-c", "import time; time.sleep(5)"])
    assert result["success"] is False
    assert "Timeout" in result["error"]

def test_input_sanitization():
    """FR-003: Test input sanitization logic."""
    dirty_input = "https://example.com; rm -rf /"
    clean_input = sanitize_input(dirty_input)
    assert ";" not in clean_input
    assert "rm" not in clean_input

def test_evidence_hash_chain():
    """T025: Verify sequential SHA-256 hashing."""
    from src.utils.security import EvidenceChainManager
    
    manager = EvidenceChainManager()
    h1 = manager.add_evidence("data1")
    h2 = manager.add_evidence("data2")
    
    assert h1 != h2
    assert manager.verify_chain() is True
    
    # Corrupt chain
    manager.chain[0].content_hash = "corrupted"
    assert manager.verify_chain() is False

def test_crypto_performance():
    """T046: Verify cryptographic operations are < 50ms (SC-001)."""
    import time
    from src.utils.security import HardenedVault
    key = Fernet.generate_key()
    vault = HardenedVault(key=SecretStr(key.decode()))
    
    start = time.perf_counter()
    vault.set_secret("perf_test", "content")
    vault.get_secret("perf_test")
    duration = (time.perf_counter() - start) * 1000
    
    # 50ms requirement (usually < 1ms on modern systems)
    assert duration < 50
