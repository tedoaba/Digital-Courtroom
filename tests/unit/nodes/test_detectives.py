import pytest
from datetime import datetime

from src.nodes.detectives import repo_investigator
from src.state import EvidenceClass, Commit, ASTFinding

def test_repo_investigator_no_dims(mocker):
    state = {
        "repo_url": "https://example.com/repo",
        "rubric_dimensions": [{"source": "docs", "criterion_id": "dim_1"}],
    }
    result = repo_investigator(state)
    assert result == {}

def test_repo_investigator_clone_failure(mocker):
    mocker.patch("src.nodes.detectives.clone_repository", side_effect=Exception("Network error"))
    state = {
        "repo_url": "https://example.com/repo.git",
        "rubric_dimensions": [{"source": "repo", "criterion_id": "dim_1"}],
    }
    result = repo_investigator(state)
    assert "evidences" in result
    assert "repo" in result["evidences"]
    evidences = result["evidences"]["repo"]
    assert len(evidences) == 1
    assert evidences[0].found is False
    assert evidences[0].rationale == "Network error"
    assert "Network error" in result["errors"]

def test_repo_investigator_success_empty(mocker, tmp_path):
    mocker.patch("src.nodes.detectives.clone_repository", return_value=None)
    mocker.patch("src.nodes.detectives.get_git_history", return_value=[])
    mocker.patch("src.nodes.detectives.analyze_ast_for_patterns", return_value=[])
    mocker.patch("src.nodes.detectives.check_tool_safety", return_value=[])
    
    state = {
        "repo_url": "https://example.com/repo.git",
        "rubric_dimensions": [{"source": "repo", "criterion_id": "dim_1"}],
    }
    
    result = repo_investigator(state)
    evidences = result["evidences"]["repo"]
    
    # Should flag as empty repo
    assert len(evidences) == 1
    assert evidences[0].found is False
    assert evidences[0].rationale == "Repository contains no detectable code files"

def test_repo_investigator_success_with_findings(mocker):
    mocker.patch("src.nodes.detectives.clone_repository", return_value=None)
    
    commit = Commit(hash="abc", author="test", date=datetime.now(), message="test")
    ast_finding = ASTFinding(file="app.py", line=10, node_type="ClassDef", name="MyModel")
    safety_finding = ASTFinding(file="bad.py", line=5, node_type="Call", name="os.system")
    
    mocker.patch("src.nodes.detectives.get_git_history", return_value=[commit])
    mocker.patch("src.nodes.detectives.analyze_ast_for_patterns", return_value=[ast_finding])
    mocker.patch("src.nodes.detectives.check_tool_safety", return_value=[safety_finding])
    
    state = {
        "repo_url": "https://example.com/repo.git",
        "rubric_dimensions": [{"source": "repo", "criterion_id": "dim_1"}],
    }
    
    result = repo_investigator(state)
    evidences = result["evidences"]["repo"]
    
    assert len(evidences) == 3
    assert all(e.found for e in evidences)
    
    classes = {e.evidence_class for e in evidences}
    assert EvidenceClass.GIT_FORENSIC in classes
    assert EvidenceClass.ORCHESTRATION_PATTERN in classes
    assert EvidenceClass.SECURITY_VIOLATION in classes

from src.nodes.detectives import doc_analyst

def test_doc_analyst_no_dims():
    state = {
        "pdf_path": "fake.pdf",
        "rubric_dimensions": [{"source": "repo", "criterion_id": "dim_1"}],
    }
    result = doc_analyst(state)
    assert result == {}

def test_doc_analyst_failure(mocker):
    mocker.patch("src.tools.doc_tools.extract_pdf_markdown", side_effect=Exception("Unparseable PDF"))
    state = {
        "pdf_path": "fake.pdf",
        "rubric_dimensions": [{"source": "docs", "criterion_id": "dim_1"}],
    }
    result = doc_analyst(state)
    assert "evidences" in result
    assert "docs" in result["evidences"]
    evidences = result["evidences"]["docs"]
    assert len(evidences) == 1
    assert evidences[0].found is False
    assert evidences[0].rationale == "Unparseable PDF"
    assert "Unparseable PDF" in result["errors"]

def test_doc_analyst_success(mocker):
    mocker.patch("src.tools.doc_tools.extract_pdf_markdown", return_value="Some markdown")
    mocker.patch("src.tools.doc_tools.find_architectural_claims", return_value=[{"keyword": "Gemini", "chunk": "...", "location": "chunk_0"}])
    mocker.patch("src.tools.doc_tools.extract_file_paths", return_value=["src/app.py"])
    
    state = {
        "pdf_path": "fake.pdf",
        "rubric_dimensions": [{"source": "docs", "criterion_id": "dim_1"}],
    }
    
    result = doc_analyst(state)
    evidences = result["evidences"]["docs"]
    assert len(evidences) == 2
    assert all(e.found for e in evidences)
    assert any("src/app.py" in e.content for e in evidences)

from src.nodes.detectives import vision_inspector

def test_vision_inspector_no_dims():
    state = {
        "pdf_path": "fake.pdf",
        "rubric_dimensions": [{"source": "repo", "criterion_id": "dim_1"}],
    }
    result = vision_inspector(state)
    assert result == {}

def test_vision_inspector_failure(mocker):
    mocker.patch("src.tools.vision_tools.run_vision_classification", side_effect=Exception("API Error"))
    state = {
        "pdf_path": "fake.pdf",
        "rubric_dimensions": [{"source": "vision", "criterion_id": "dim_1"}],
    }
    result = vision_inspector(state)
    assert "evidences" in result
    assert "vision" in result["evidences"]
    evidences = result["evidences"]["vision"]
    assert len(evidences) == 1
    assert evidences[0].found is False
    assert evidences[0].rationale == "API Error"
    assert "API Error" in result["errors"]

def test_vision_inspector_success(mocker):
    mocker.patch("src.tools.vision_tools.run_vision_classification", return_value=[{"image_index": 0, "page": 1, "classification": "Parallel"}])
    
    state = {
        "pdf_path": "fake.pdf",
        "rubric_dimensions": [{"source": "vision", "criterion_id": "dim_1"}],
    }
    
    result = vision_inspector(state)
    evidences = result["evidences"]["vision"]
    assert len(evidences) == 1
    assert evidences[0].found is True
    assert evidences[0].content == "Parallel"


