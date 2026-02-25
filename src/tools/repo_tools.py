import subprocess
import os
import shutil
import time
from pathlib import Path
from typing import List, Optional, Tuple, ContextManager
from contextlib import contextmanager
from datetime import datetime, timezone

from src.models.forensic import Commit
from src.tools.base import ToolResult
from src.tools.utils import validate_source_url, check_disk_limit, DISK_LIMIT_BYTES, TimeoutException, with_timeout


import tempfile
from typing import Generator, Union

@contextmanager
def clone_repo(url: str) -> Generator[ToolResult[str], None, None]:
    """
    Clones a git repository into a temporary workspace.
    Ref: FR-001 (shell=False), FR-002 (timeout), FR-003 (isolation), FR-006 (whitelist), FR-009 (disk limit), FR-011 (partial clone cleanup).
    """
    start_time = time.time()
    
    if not validate_source_url(url):
        yield ToolResult(
            status="access_denied",
            error=f"Invalid or unapproved URL: {url}",
            execution_time=time.time() - start_time
        )
        return

    tmp_dir = tempfile.TemporaryDirectory()
    workspace = Path(tmp_dir.name)
        
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    target_path = workspace / repo_name
    
    # Check disk space before clone
    if not check_disk_limit(workspace):
        yield ToolResult(status="disk_limit_exceeded", error="Workspace disk limit reached.")
        tmp_dir.cleanup()
        return

    try:
        cmd = ["git", "clone", "--depth", "100", url, str(target_path)]
        
        @with_timeout(seconds=60)
        def run_clone():
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                check=True
            )
            
        run_clone()
        
        if not check_disk_limit(target_path):
            yield ToolResult(status="disk_limit_exceeded", error="Repository clone exceeded disk limit.")
            return

        yield ToolResult(
            status="success",
            data=[str(target_path)],
            execution_time=time.time() - start_time
        )
        
    except TimeoutException:
        yield ToolResult(status="timeout", error="Repository cloning timed out.", execution_time=time.time() - start_time)
        
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.decode('utf-8') if e.stderr else "Unknown error"
        if "Could not resolve host" in stderr_msg or "Connection timed out" in stderr_msg:
             yield ToolResult(status="network_failure", error=f"Network error during clone: {stderr_msg}", execution_time=time.time() - start_time)
        else:
             yield ToolResult(status="failure", error=f"Git clone failed: {stderr_msg}", execution_time=time.time() - start_time)
        
    except Exception as e:
        yield ToolResult(status="failure", error=f"Unexpected error: {str(e)}", execution_time=time.time() - start_time)
        
    finally:
        tmp_dir.cleanup()


@with_timeout(seconds=60)
def extract_git_history(repo_path: Union[str, Path]) -> ToolResult[Commit]:
    """
    Extracts metadata for commits in the cloned repository.
    Ref: Protocol A, FR-008 (timestamps).
    """
    start_time = time.time()
    repo_path = Path(repo_path)

    
    if not repo_path.exists() or not (repo_path / ".git").exists():
        return ToolResult(status="failure", error="Invalid repository path.")

    try:
        # Format: Hash|Author|UnixTimestamp|Message
        # Using %ct for unix timestamp, which we'll convert to UTC
        cmd = ["git", "log", "--pretty=format:%H|%an|%ct|%s"]
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            check=True,
            timeout=30,
            encoding="utf-8"
        )
        
        commits: List[Commit] = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
                
            parts = line.split("|", 3)
            if len(parts) != 4:
                continue
                
            commit_hash, author, timestamp_str, message = parts
            
            try:
                # FR-008/SC-005: UTC Deterministic Timestamp
                dt = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)
                
                commits.append(Commit(
                    hash=commit_hash,
                    author=author,
                    date=dt,
                    message=message
                ))
            except ValueError:
                continue
                
        return ToolResult(
            status="success",
            data=commits,
            execution_time=time.time() - start_time
        )
        
    except subprocess.TimeoutExpired:
        return ToolResult(status="timeout", error="Git log extraction timed out.", execution_time=time.time() - start_time)
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr if e.stderr else "Unknown error"
        return ToolResult(status="failure", error=f"Git log failed: {stderr_msg}", execution_time=time.time() - start_time)
    except Exception as e:
         return ToolResult(status="failure", error=f"Unexpected error: {str(e)}", execution_time=time.time() - start_time)
