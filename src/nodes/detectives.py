import tempfile
import time
from typing import Dict, List, Any
from datetime import datetime
from src.utils.logger import StructuredLogger

logger = StructuredLogger("detectives")

from src.state import AgentState, Evidence, EvidenceClass
from src.tools.repo_tools import clone_repository, get_git_history, analyze_ast_for_patterns, check_tool_safety
from src.config import detective_settings

def repo_investigator(state: AgentState) -> Dict[str, Any]:
    """RepoInvestigator node conforming to Layer 1 specifications."""
    repo_url = state.get("repo_url", "")
    rubric_dimensions = state.get("rubric_dimensions", [])
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    
    logger.log_node_entry("repo_investigator", repo_url=repo_url, correlation_id=correlation_id)
    
    # FR-012: Filter logic - Rubric uses 'target_artifact' instead of 'source'
    repo_dims = [d for d in rubric_dimensions if d.get("target_artifact") == "github_repo"]
    
    if not repo_dims:
        return {}
    
    start_time = time.time()
    evidences = []
    errors = []
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                clone_repository(repo_url, tmpdir, timeout=detective_settings.operation_timeout_seconds)
            except Exception as e:
                # Graceful degradation on clone failure (FR-005)
                errors.append(str(e))
                # Emit found=False for all goals
                for idx, d in enumerate(repo_dims):
                    evidences.append(Evidence(
                        evidence_id=f"repo_clone_failed_{idx}_{int(time.time())}",
                        source="repo",
                        evidence_class=EvidenceClass.GIT_FORENSIC,
                        goal=d.get("criterion_id", "Unknown"),
                        found=False,
                        content=None,
                        location=repo_url,
                        rationale=str(e),
                        confidence=1.0,
                        timestamp=datetime.now()
                    ))
                logger.error("RepoInvestigator clone failed", correlation_id=correlation_id, duration=time.time()-start_time, error=str(e))
                return {"evidences": {"repo": evidences}, "errors": errors}

            # AST Analysis
            ast_findings = analyze_ast_for_patterns(tmpdir)
            safety_findings = check_tool_safety(tmpdir)
            git_history = get_git_history(tmpdir)
            
            # Map standard findings to evidence
            for commit in git_history:
                evidences.append(Evidence(
                    evidence_id=f"repo_git_{commit.hash}",
                    source="repo",
                    evidence_class=EvidenceClass.GIT_FORENSIC,
                    goal="Verify commit history",
                    found=True,
                    content=commit.message,
                    location=commit.hash,
                    rationale="Extracted from git history",
                    confidence=1.0,
                    timestamp=datetime.now()
                ))
            
            for i, f in enumerate(ast_findings):
                evidences.append(Evidence(
                    evidence_id=f"repo_ast_{i}_{int(time.time())}",
                    source="repo",
                    evidence_class=EvidenceClass.ORCHESTRATION_PATTERN,
                    goal="Verify architectural patterns",
                    found=True,
                    content=f"{f.node_type} {f.name}",
                    location=f"{f.file}:{f.line}",
                    rationale="Extracted from AST",
                    confidence=1.0,
                    timestamp=datetime.now()
                ))
                
            for i, f in enumerate(safety_findings):
                evidences.append(Evidence(
                    evidence_id=f"repo_safety_{i}_{int(time.time())}",
                    source="repo",
                    evidence_class=EvidenceClass.SECURITY_VIOLATION,
                    goal="Check tool safety",
                    found=True,
                    content=f"Found unsafe call: {f.name}",
                    location=f"{f.file}:{f.line}",
                    rationale="Unsafe function detected in AST",
                    confidence=1.0,
                    timestamp=datetime.now()
                ))

            if not git_history and not ast_findings:
                errors.append("Repository contains no detectable code files")
                evidences.append(Evidence(
                    evidence_id=f"repo_empty_{int(time.time())}",
                    source="repo",
                    evidence_class=EvidenceClass.GIT_FORENSIC,
                    goal="Inspect repository",
                    found=False,
                    content=None,
                    location=repo_url,
                    rationale="Repository contains no detectable code files",
                    confidence=1.0,
                    timestamp=datetime.now()
                ))

    except Exception as e:
        # Catch-all graceful failure (FR-004)
        errors.append(str(e))
        evidences.append(Evidence(
            evidence_id=f"repo_fatal_{int(time.time())}",
            source="repo",
            evidence_class=EvidenceClass.GIT_FORENSIC,
            goal="Analyze codebase",
            found=False,
            content=None,
            location=repo_url,
            rationale=str(e),
            confidence=1.0,
            timestamp=datetime.now()
        ))
        
    duration = time.time() - start_time
    # Logging for Observability (FR-009)
    logger.info("RepoInvestigator complete", correlation_id=correlation_id, duration=duration, artifacts=len(evidences), source="repo")

    return {"evidences": {"repo": evidences}, "errors": errors}

def doc_analyst(state: AgentState) -> Dict[str, Any]:
    """DocAnalyst node conforming to Layer 1 specifications."""
    pdf_path = state.get("pdf_path", "")
    rubric_dimensions = state.get("rubric_dimensions", [])
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    
    logger.log_node_entry("doc_analyst", pdf_path=pdf_path, correlation_id=correlation_id)
    
    # FR-012: Filter logic - Rubric uses 'target_artifact' instead of 'source'
    doc_dims = [d for d in rubric_dimensions if d.get("target_artifact") == "pdf_report"]
    
    if not doc_dims:
        return {}
    
    start_time = time.time()
    evidences = []
    errors = []
    
    from src.tools.doc_tools import extract_pdf_markdown, find_architectural_claims, extract_file_paths

    try:
        markdown_text = extract_pdf_markdown(pdf_path, timeout=detective_settings.operation_timeout_seconds)
        
        claims = find_architectural_claims(markdown_text)
        paths = extract_file_paths(markdown_text)
        
        # Mapping claims to evidence
        for i, c in enumerate(claims):
            evidences.append(Evidence(
                evidence_id=f"docs_claim_{i}_{int(time.time())}",
                source="docs",
                evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                goal="Verify architectural claims",
                found=True,
                content=f"Found keyword '{c['keyword']}': {c['chunk']}",
                location=c['location'],
                rationale="Structural matching against keywords",
                confidence=0.9,
                timestamp=datetime.now()
            ))
            
        for i, p in enumerate(paths):
            evidences.append(Evidence(
                 evidence_id=f"docs_path_{i}_{int(time.time())}",
                 source="docs",
                 evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                 goal="Extract claimed file paths",
                 found=True,
                 content=p,
                 location="extracted_path",
                 rationale="Regex path matching against Markdown text",
                 confidence=0.8,
                 timestamp=datetime.now()
            ))

    except Exception as e:
        errors.append(str(e))
        # Emit found=False
        for idx, d in enumerate(doc_dims):
            evidences.append(Evidence(
                evidence_id=f"docs_failed_{idx}_{int(time.time())}",
                source="docs",
                evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                goal=d.get("criterion_id", "Unknown"),
                found=False,
                content=None,
                location=pdf_path,
                rationale=str(e),
                confidence=1.0,
                timestamp=datetime.now()
            ))
            
    duration = time.time() - start_time
    logger.info("DocAnalyst complete", correlation_id=correlation_id, duration=duration, artifacts=len(evidences), source="docs")

    return {"evidences": {"docs": evidences}, "errors": errors}

def vision_inspector(state: AgentState) -> Dict[str, Any]:
    """VisionInspector node conforming to Layer 1 specifications."""
    pdf_path = state.get("pdf_path", "")
    rubric_dimensions = state.get("rubric_dimensions", [])
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    
    logger.log_node_entry("vision_inspector", pdf_path=pdf_path, correlation_id=correlation_id)
    
    # FR-012: Filter logic - Rubric uses 'target_artifact' instead of 'source'
    vision_dims = [d for d in rubric_dimensions if d.get("target_artifact") == "pdf_images"]
    
    if not vision_dims:
        return {}
    
    start_time = time.time()
    evidences = []
    errors = []
    
    from src.tools.vision_tools import run_vision_classification

    try:
        classifications = run_vision_classification(pdf_path, timeout=detective_settings.operation_timeout_seconds)
        
        for c in classifications:
            evidences.append(Evidence(
                 evidence_id=f"vision_img_{c['image_index']}_{int(time.time())}",
                 source="vision",
                 evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                 goal="Classify architectural diagrams",
                 found=True,
                 content=c['classification'],
                 location=f"page_index_{c['page']}",
                 rationale="LLM-based classification of diagram",
                 confidence=0.85,
                 timestamp=datetime.now()
            ))

    except Exception as e:
        errors.append(str(e))
        # Emit found=False
        for idx, d in enumerate(vision_dims):
            evidences.append(Evidence(
                evidence_id=f"vision_failed_{idx}_{int(time.time())}",
                source="vision",
                evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                goal=d.get("criterion_id", "Unknown"),
                found=False,
                content=None,
                location=pdf_path,
                rationale=str(e),
                confidence=1.0,
                timestamp=datetime.now()
            ))
            
    duration = time.time() - start_time
    logger.info("VisionInspector complete", correlation_id=correlation_id, duration=duration, artifacts=len(evidences), source="vision")

    return {"evidences": {"vision": evidences}, "errors": errors}

