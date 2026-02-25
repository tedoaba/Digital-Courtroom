import pytest
import os
import tempfile
from pathlib import Path
from src.tools.repo_tools import clone_repo, extract_git_history
from src.models.forensic import Commit

@pytest.fixture
def test_workspace():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

def test_secure_evidence_collection_scenario(test_workspace):
    """
    Integration test matching User Story 1 (Secure External Evidence Collection).
    Scenario: Valid URL cloning, structural metadata extraction, and isolation.
    """
    
    # 1. Provide a valid Git URL
    test_url = "https://github.com/octocat/Hello-World"
    
    # 2. Collect evidence
    with clone_repo(test_url) as clone_result:
        assert clone_result.status == "success"
        assert clone_result.data is not None
        assert len(clone_result.data) == 1
        
        repo_path = Path(clone_result.data[0])
        assert repo_path.exists()
        assert (repo_path / "README").exists() or (repo_path / "README.md").exists()
        
        # Check max disk limit isn't exceeded
        assert clone_result.status != "disk_limit_exceeded"
        
        # 3. Extract history
        history_result = extract_git_history(repo_path)
        assert history_result.status == "success"
        
        commits = history_result.data
        assert commits is not None
        assert len(commits) > 0
        assert isinstance(commits[0], Commit)
        
        # Verification of git timestamp in UTC
        assert commits[0].date.tzinfo is not None
