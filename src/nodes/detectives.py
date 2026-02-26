import tempfile
import time
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from src.utils.logger import StructuredLogger
from src.state import AgentState, Evidence, EvidenceClass
from src.tools.repo_tools import clone_repository, get_git_history, analyze_ast_for_patterns, check_tool_safety
from src.config import detective_settings
from src.utils.security import SandboxEnvironment
from src.utils.observability import node_traceable

logger = StructuredLogger("detectives")

@node_traceable
def repo_investigator(state: AgentState) -> Dict[str, Any]:
    """RepoInvestigator node conforming to Layer 1 specifications."""
    repo_url = state.get("repo_url", "")
    rubric_dimensions = state.get("rubric_dimensions", [])
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    
    logger.log_node_entry("repo_investigator", repo_url=repo_url, correlation_id=correlation_id)
    
    repo_dims = [d for d in rubric_dimensions if d.get("target_artifact") == "github_repo"]
    if not repo_dims:
        return {}
    
    start_time = time.time()
    evidences = []
    errors = []
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = SandboxEnvironment(
                root_path=Path(tmpdir),
                memory_limit_mb=512,
                cpu_limit_cores=1,
                timeout_seconds=detective_settings.operation_timeout_seconds
            )
            
            try:
                clone_repository(repo_url, tmpdir, sandbox=sandbox)
            except Exception as e:
                errors.append(str(e))
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
                return {"evidences": {"repo": evidences}, "errors": errors}

            ast_findings = analyze_ast_for_patterns(tmpdir)
            safety_findings = check_tool_safety(tmpdir)
            git_history = get_git_history(tmpdir, sandbox=sandbox)
            
            for commit in git_history:
                evidences.append(Evidence(
                    evidence_id=f"repo_git_{commit.hash}",
                    source="repo",
                    evidence_class=EvidenceClass.GIT_FORENSIC,
                    goal="Verify repository history for forensic patterns",
                    found=True,
                    content=commit.message,
                    location=commit.hash,
                    rationale="Extracted from git history in sandbox",
                    confidence=1.0,
                    timestamp=datetime.now()
                ))
            
            for i, f in enumerate(ast_findings):
                evidences.append(Evidence(
                    evidence_id=f"repo_ast_{i}_{int(time.time())}",
                    source="repo",
                    evidence_class=EvidenceClass.ORCHESTRATION_PATTERN,
                    goal="Audit architectural patterns in source code",
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
                    goal="Scan for unauthorized tool executions",
                    found=True,
                    content=f"Found: {f.name}",
                    location=f"{f.file}:{f.line}",
                    rationale="Security audit of detected patterns",
                    confidence=1.0,
                    timestamp=datetime.now()
                ))

    except Exception as e:
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
    logger.info("RepoInvestigator complete", correlation_id=correlation_id, duration=duration, artifacts=len(evidences), source="repo")
    return {"evidences": {"repo": evidences}, "errors": errors}

@node_traceable
def doc_analyst(state: AgentState) -> Dict[str, Any]:
    """DocAnalyst node conforming to Layer 1 specifications."""
    pdf_path = state.get("pdf_path", "")
    rubric_dimensions = state.get("rubric_dimensions", [])
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    
    logger.log_node_entry("doc_analyst", pdf_path=pdf_path, correlation_id=correlation_id)
    doc_dims = [d for d in rubric_dimensions if d.get("target_artifact") == "pdf_report"]
    if not doc_dims:
        return {}
    
    start_time = time.time()
    evidences = []
    errors = []
    from src.tools.doc_tools import extract_pdf_markdown, find_architectural_claims, extract_file_paths

    try:
        # doc_tools might need sandbox update if they run shell commands (like docling or pandoc)
        markdown_text = extract_pdf_markdown(pdf_path, timeout=detective_settings.operation_timeout_seconds)
        claims = find_architectural_claims(markdown_text)
        paths = extract_file_paths(markdown_text)
        
        for i, c in enumerate(claims):
            evidences.append(Evidence(
                evidence_id=f"docs_claim_{i}_{int(time.time())}",
                source="docs",
                evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                goal="Extract claims from architecture report",
                found=True,
                content=c['chunk'],
                location=c['location'],
                rationale="Structural claim identification",
                confidence=0.9,
                timestamp=datetime.now()
            ))

    except Exception as e:
        errors.append(str(e))
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

@node_traceable
def vision_inspector(state: AgentState) -> Dict[str, Any]:
    """VisionInspector node conforming to Layer 1 specifications."""
    pdf_path = state.get("pdf_path", "")
    rubric_dimensions = state.get("rubric_dimensions", [])
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    
    logger.log_node_entry("vision_inspector", pdf_path=pdf_path, correlation_id=correlation_id)
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
                 goal="Analyze visual diagrams for architecture",
                 found=True,
                 content=c['classification'],
                 location=f"page {c['page']}",
                 rationale="Visual classification of diagrams",
                 confidence=0.85,
                 timestamp=datetime.now()
            ))

    except Exception as e:
        errors.append(str(e))
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
