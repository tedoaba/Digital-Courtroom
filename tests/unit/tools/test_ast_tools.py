import pytest
import os
import tempfile
from pathlib import Path
from src.tools.ast_tools import scan_repository
from src.models.forensic import ASTFinding

@pytest.fixture
def mock_repo_with_code():
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)
        
        # Valid Python file
        valid_py = repo_path / "models.py"
        valid_py.write_text("""
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(...)
    age: int

def get_user():
    pass
""")

        # File with syntax error
        invalid_py = repo_path / "invalid.py"
        invalid_py.write_text("""
class Broken
    def broken_func()
""")

        # Poisonous file (os.system)
        poison_py = repo_path / "poison.py"
        poison_py.write_text("""
import os
os.system("echo 'POISON EXECUTED'")

class GraphManager:
    def build_graph(self):
        # Fake StateGraph pattern
        graph = StateGraph(State)
        graph.add_node("node1", func)
        return graph.compile()
""")

        yield repo_path

def test_scan_repository_valid_syntax(mock_repo_with_code):
    result = scan_repository(mock_repo_with_code)
    assert result.status == "success"
    
    findings = result.data
    assert findings is not None
    
    # Check for User class
    class_findings = [f for f in findings if f.node_type == "ClassDef" and f.name == "User"]
    assert len(class_findings) == 1
    assert "BaseModel" in class_findings[0].details.get("bases", [])
    
    # Check for function
    func_findings = [f for f in findings if f.node_type == "FunctionDef" and f.name == "get_user"]
    assert len(func_findings) == 1

def test_scan_repository_invalid_syntax(mock_repo_with_code):
    result = scan_repository(mock_repo_with_code)
    assert result.status == "success"
    
    findings = result.data
    assert findings is not None
    
    # Needs to report syntax error as a finding or gracefully handle
    syntax_errors = [f for f in findings if f.node_type == "SyntaxError"]
    assert len(syntax_errors) == 1
    assert "invalid.py" in syntax_errors[0].file

def test_scan_repository_zero_execution(mock_repo_with_code, capsys, monkeypatch):
    """
    Ensure the code is NEVER EXECUTED. We can check if 'POISON EXECUTED' is printed.
    """
    # Just in case, try to mock os.system to fail the test if called
    def mock_system(*args, **kwargs):
        pytest.fail("os.system was called! Code was executed!")
        
    monkeypatch.setattr(os, "system", mock_system)
    
    result = scan_repository(mock_repo_with_code)
    assert result.status == "success"
    
    findings = result.data
    assert findings is not None
    
    # Verify StateGraph is detected
    stategraph_findings = [f for f in findings if f.name.startswith("StateGraph")]
    assert len(stategraph_findings) > 0

    out, err = capsys.readouterr()
    assert "POISON EXECUTED" not in out
