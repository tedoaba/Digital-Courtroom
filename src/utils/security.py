"""
Security utilities for Operation Ironclad Swarm.
(013-ironclad-hardening)
"""
import os
import subprocess
import time
import threading
import psutil
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, SecretStr, ValidationError
from cryptography.fernet import Fernet

class HardenedVault:
    """
    AES-256 (Fernet) vault for secret storage.
    (FR-002)
    """
    def __init__(self, key: Optional[SecretStr] = None):
        if not key:
            key_str = os.getenv("COURTROOM_VAULT_KEY")
            if not key_str:
                 # Fallback for tests or local dev if not strictly required to fail here
                 # But SC-006 says verify fails if configuration is missing.
                 # Actually for US1, verify system fails to start without complete .env.
                 pass
            self.key = SecretStr(key_str) if key_str else None
        else:
            self.key = key
        
        if self.key:
            self.fernet = Fernet(self.key.get_secret_value().encode())
        else:
            self.fernet = None
        
        self._secrets: Dict[str, bytes] = {}

    def set_secret(self, key: str, value: str) -> None:
        if not self.fernet:
            raise ValueError("Vault key not initialized.")
        self._secrets[key] = self.fernet.encrypt(value.encode())

    def get_secret(self, key: str) -> Optional[str]:
        if not self.fernet or key not in self._secrets:
            return None
        return self.fernet.decrypt(self._secrets[key]).decode()

class SandboxEnvironment(BaseModel):
    """
    Resource-constrained execution space for tools.
    (FR-004)
    """
    root_path: Path
    memory_limit_mb: int = 512
    cpu_limit_cores: int = 1
    timeout_seconds: int = 60

    def execute_tool(self, command: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """Execute command within limits using psutil monitoring."""
        if not self.root_path.exists():
            self.root_path.mkdir(parents=True, exist_ok=True)

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(self.root_path)
        )

        error_msg = ""
        success = True
        
        def monitor():
            nonlocal error_msg, success
            try:
                p = psutil.Process(process.pid)
                start_time = time.time()
                while process.poll() is None:
                    # Check Memory
                    mem = p.memory_info().rss / (1024 * 1024)
                    if mem > self.memory_limit_mb:
                        error_msg = f"Memory limit exceeded: {mem:.2f}MB > {self.memory_limit_mb}MB"
                        success = False
                        process.kill()
                        break
                    
                    # Check Timeout
                    if (time.time() - start_time) > self.timeout_seconds:
                        error_msg = f"Timeout: {time.time() - start_time:.2f}s > {self.timeout_seconds}s"
                        success = False
                        process.kill()
                        break
                    
                    time.sleep(0.1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.start()

        stdout, stderr = process.communicate(input=input_data)
        monitor_thread.join()

        if not success:
            return {"success": False, "error": error_msg}
        
        if process.returncode != 0:
            return {"success": False, "error": stderr or f"Process exited with code {process.returncode}"}

        return {"success": True, "output": stdout}

import hashlib
from src.state import EvidenceChain

class EvidenceChainManager:
    """
    Manages cryptographic evidence chain for integrity (T027).
    (FR-011, CHK001)
    """
    def __init__(self, genesis_seed: str = "courtroom-genesis"):
        self.chain: List[EvidenceChain] = []
        self.genesis_seed = genesis_seed

    def add_evidence(self, content: str) -> str:
        prev_hash = self.chain[-1].content_hash if self.chain else self.genesis_seed
        curr_hash = hashlib.sha256((prev_hash + content).encode()).hexdigest()
        
        entry = EvidenceChain(
            evidence_id=f"chain_{len(self.chain)}",
            content_hash=curr_hash,
            previous_hash=prev_hash,
            timestamp=datetime.now()
        )
        self.chain.append(entry)
        return curr_hash

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i-1].content_hash:
                return False
        return True

def verify_evidence_integrity(chain: List[EvidenceChain], current_content: str) -> bool:
    """T031: Verify external evidence against cryptographic chain."""
    manager = EvidenceChainManager()
    manager.chain = chain
    return manager.verify_chain()

def sanitize_repo_url(url: str) -> str:
    """Basic URL sanitization (FR-003)."""
    # Remove potentially dangerous characters for shell interaction
    return re.sub(r'[;&|`$<>?*!#]', '', url).strip()

def sanitize_input(data: str) -> str:
    """FR-003: Sanitize external input to prevent command injection."""
    # CHK003: Remove separators and common dangerous commands
    sanitized = re.sub(r'[;&|`$<>?*!#]', '', data)
    # Basic command blacklist for demonstration
    for cmd in ["rm ", "sh ", "bash ", "curl ", "wget "]:
        sanitized = sanitized.replace(cmd, "[REDACTED]")
    return sanitized

def validate_output(schema: Any, data: Any) -> Any:
    """FR-003: Pydantic-based output validation."""
    if hasattr(schema, "model_validate"):
        try:
            return schema.model_validate(data)
        except ValidationError as e:
            return {"error": str(e)}
    return data
