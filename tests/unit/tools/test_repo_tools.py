import subprocess

import pytest

from src.tools.repo_tools import (
    analyze_ast_for_patterns,
    check_tool_safety,
    clone_repository,
    get_git_history,
)


def test_clone_repository_success(mocker, tmp_path):
    mocker.patch("subprocess.run")
    clone_repository("https://example.com/repo.git", str(tmp_path))
    subprocess.run.assert_called_once()


def test_clone_repository_timeout(mocker, tmp_path):
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="git", timeout=60),
    )
    with pytest.raises(TimeoutError, match="timed out"):
        clone_repository("https://example.com/repo.git", str(tmp_path), timeout=60)


def test_clone_repository_failure(mocker, tmp_path):
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(
            returncode=1,
            cmd="git",
            stderr="Not found",
        ),
    )
    with pytest.raises(RuntimeError, match="Cloning failed"):
        clone_repository("https://example.com/repo.git", str(tmp_path))


def test_get_git_history(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = "abc1234|John Doe|1672531200|Initial commit"
    commits = get_git_history("/repo")
    assert len(commits) == 1
    assert commits[0].hash == "abc1234"
    assert commits[0].author == "John Doe"
    assert commits[0].message == "Initial commit"


def test_get_git_history_empty(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.stdout = ""
    commits = get_git_history("/repo")
    assert len(commits) == 0


def test_analyze_ast_for_patterns(tmp_path):
    # Setup test file
    test_file = tmp_path / "test.py"
    test_file.write_text(
        "from pydantic import BaseModel\nclass MyModel(BaseModel):\n    pass\n",
        encoding="utf-8",
    )

    findings = analyze_ast_for_patterns(str(tmp_path))
    assert len(findings) == 1
    assert findings[0].name == "MyModel"
    assert findings[0].node_type == "ClassDef"


def test_check_tool_safety(tmp_path):
    # Setup test file
    test_file = tmp_path / "unsafe.py"
    test_file.write_text(
        "import os\nos.system('echo hi')\neval('1+1')\n",
        encoding="utf-8",
    )

    findings = check_tool_safety(str(tmp_path))
    assert len(findings) == 2
    names = {f.name for f in findings}
    assert names == {"os.system", "eval"}
