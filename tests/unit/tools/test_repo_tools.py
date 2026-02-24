import pytest
import shutil
import tempfile
import time
from pathlib import Path
from datetime import datetime, timezone
import subprocess
from unittest.mock import patch, MagicMock
from src.tools.repo_tools import clone_repo, extract_git_history
from src.tools.utils import TimeoutException
from src.tools.base import ToolResult


@pytest.fixture
def mock_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "repo"
        repo_path.mkdir()
        
        # Initialize git rules
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)
        
        # Create a file and commit
        (repo_path / "test.txt").write_text("Hello, World!")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        
        env = {"GIT_AUTHOR_DATE": "2023-01-01T12:00:00+0000", "GIT_COMMITTER_DATE": "2023-01-01T12:00:00+0000"}
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, env=env, check=True)
        
        yield str(repo_path)


def test_clone_repo_success(mock_git_repo):
    """Test successful cloning of a repository."""
    # Since mock_git_repo is just a local folder, it will fail the whitelist check.
    # Let's mock validate_source_url for this test just to test cloning logic
    with patch("src.tools.repo_tools.validate_source_url", return_value=True):
        repo_url = Path(mock_git_repo).as_uri()
        with clone_repo(repo_url) as result:
            print("ERROR", result.error)
            assert result.status == "success"
            assert result.data is not None
            assert len(result.data) == 1
            
            # Check that temp dir exists and is valid
            cloned_path = result.data[0]
            assert Path(cloned_path).exists()
            assert (Path(cloned_path) / "test.txt").exists()


def test_clone_repo_invalid_url():
    """Test cloning with an invalid URL protocol."""
    with clone_repo("http://github.com/test/test") as result:
        assert result.status == "access_denied"
        assert "Invalid protocol" in result.error or "Invalid or unapproved URL" in result.error


def test_clone_repo_injection_attempt():
    """Test cloning with a shell injection attempt."""
    with clone_repo("https://github.com/test/test; rm -rf /") as result:
        assert result.status == "failure"


@patch("subprocess.run")
def test_clone_repo_timeout(mock_run):
    """Test timeout during repository clone."""
    def timeout_func(*args, **kwargs):
        from src.tools.utils import TimeoutException
        raise TimeoutException("timeout")
        
    mock_run.side_effect = timeout_func
    
    with patch("src.tools.repo_tools.validate_source_url", return_value=True):
        with clone_repo("https://github.com/test/test") as result:
            assert result.status == "timeout"


def test_extract_git_history(mock_git_repo):
    """Test extracting git history."""
    result = extract_git_history(mock_git_repo)
    
    assert result.status == "success"
    assert result.data is not None
    assert len(result.data) == 1
    
    commit = result.data[0]
    assert commit.author == "Test User"
    assert commit.message == "Initial commit"
    assert commit.date.tzinfo == timezone.utc
