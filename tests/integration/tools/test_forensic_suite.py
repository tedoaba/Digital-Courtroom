import tempfile
from pathlib import Path

import pytest

from src.state import Commit
from src.tools.repo_tools import clone_repository, get_git_history

@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

def test_clone_repository(temp_repo):
    """T015: Verifies that a public repository can be cloned safely."""
    # Using a small, stable repo for integration testing
    url = "https://github.com/astral-sh/uv"
    res = clone_repository(url, str(temp_repo), timeout=30)
    assert res is True
    assert (temp_repo / ".git").exists()

def test_get_git_history(temp_repo):
    """T016: Verifies that git history is correctly extracted into Commit objects."""
    # First clone
    url = "https://github.com/astral-sh/uv"
    clone_repository(url, str(temp_repo), timeout=30)
    
    history = get_git_history(str(temp_repo), depth=5)
    assert len(history) > 0
    assert isinstance(history[0], Commit)
    assert len(history[0].hash) > 0
    assert history[0].author != ""
    assert history[0].message != ""
