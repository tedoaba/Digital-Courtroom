import logging
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from src.state import AgentState, Evidence, EvidenceClass

from src.utils.logger import StructuredLogger

logger = StructuredLogger("evidence_aggregator")

def sanitize_path(path_str: str) -> Optional[str]:
    """
    Sanitizes and validates a file path from documentation.
    - Rejects absolute paths.
    - Rejects paths escaping the repository root (..).
    - Normalizes to POSIX format (forward slashes).
    
    Returns:
        Normalized relative path string if valid, None if security violation.
    """
    if not path_str:
        return None
        
    try:
        # Use normpath for faster string-based normalization without system calls
        import os
        
        # Check for absolute paths
        if os.path.isabs(path_str) or (len(path_str) > 1 and path_str[1] == ':'):
            logger.warning(f"SECURITY_VIOLATION: Absolute path rejected: {path_str}")
            return None
            
        # Normalize path (handles both / and \ -> current OS style)
        normalized = os.path.normpath(path_str)
        
        # Check for traversal above root
        # After normpath, '..' will only remain at the start if it escapes
        if normalized.startswith(".."):
            logger.warning(f"SECURITY_VIOLATION: Path traversal detected: {path_str}")
            return None
            
        # Convert to POSIX style (forward slashes)
        return normalized.replace(os.sep, '/')
    except Exception as e:
        logger.error(f"Error sanitizing path {path_str}: {e}")
        return None

def generate_hallucination_id(path: str) -> str:
    """Generates a unique evidence_id for a hallucinated path claim."""
    path_hash = hashlib.sha256(path.encode()).hexdigest()[:8]
    return f"docs_DOCUMENT_CLAIM_{path_hash}"

def aggregator_node(state: AgentState) -> dict:
    """
    Evidence Aggregator Node (Layer 1.5).
    Syncs, deduplicates, and cross-references evidence from detectives.
    """
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    logger.log_node_entry("aggregator_node", correlation_id=correlation_id)
    
    evidences = state.get("evidences", {})
    if not isinstance(evidences, dict):
        # FR-005 error handling if malformed state
        return {"errors": ["CRITICAL_STATE_ERROR: evidences field is not a dictionary"]}

    # 1. Deduplication (FR-006)
    clean_evidences = {}
    for source, items in evidences.items():
        if not items:
            clean_evidences[source] = []
            continue
            
        seen_ids = set()
        deduped = []
        for item in items:
            if item.evidence_id not in seen_ids:
                deduped.append(item)
                seen_ids.add(item.evidence_id)
            else:
                logger.warning(f"Deduplicating evidence {item.evidence_id} in source {source}")
        clean_evidences[source] = deduped

    # 2. Missing Source Handling (FR-005)
    new_errors = []
    if not clean_evidences.get("repo"):
        new_errors.append("FORENSIC_SOURCE_MISSING: 'repo' source is missing or empty.")
    if not clean_evidences.get("docs"):
        new_errors.append("FORENSIC_SOURCE_MISSING: 'docs' source is missing or empty.")
    
    if "vision" not in clean_evidences:
        logger.warning("Missing 'vision' source in evidences.")

    # 3. Cross-Reference File Paths (FR-003, FR-004)
    if "repo" in clean_evidences and "docs" in clean_evidences:
        # Build repo manifest (Set for O(1) lookup)
        repo_manifest = {e.location for e in clean_evidences["repo"]}
        
        hallucinations = []
        hallu_ids = set()
        for e in clean_evidences["docs"]:
            # Sanitize documentation path
            raw_path = e.location
                
            # If evidence_class is already DOCUMENT_CLAIM and found=False,
            # it might be a previously flagged hallucination or a re-run.
            if e.evidence_class == EvidenceClass.DOCUMENT_CLAIM and not e.found:
                continue

            sanitized = sanitize_path(raw_path)
            
            if not sanitized:
                # Security violation or bad path
                hallu_id = generate_hallucination_id(raw_path)
                if hallu_id not in hallu_ids:
                    hallucinations.append(Evidence(
                        evidence_id=hallu_id,
                        source="docs",
                        evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                        goal="Sanitize documentation path",
                        found=False,
                        location=raw_path,
                        rationale="SECURITY_VIOLATION: Path outside root or invalid format.",
                        confidence=1.0,
                        timestamp=datetime.now(timezone.utc)
                    ))
                    hallu_ids.add(hallu_id)
                continue

            # Check existence in manifest
            if sanitized not in repo_manifest:
                hallu_id = generate_hallucination_id(sanitized)
                # Avoid duplicates if multiple docs cite the same missing file
                if hallu_id not in hallu_ids:
                    hallucinations.append(Evidence(
                        evidence_id=hallu_id,
                        source="docs",
                        evidence_class=EvidenceClass.DOCUMENT_CLAIM,
                        goal="Cross-reference documentation path",
                        found=False,
                        location=sanitized,
                        rationale="Path cited in documentation does not exist in the repository manifest.",
                        confidence=1.0,
                        timestamp=datetime.now(timezone.utc)
                    ))
                    hallu_ids.add(hallu_id)
        
        # Append hallucinations to docs source
        clean_evidences["docs"].extend(hallucinations)

    # 4. Polish (FR-007, FR-008) - Summary log
    hallucination_count = sum(1 for e in clean_evidences.get("docs", []) 
                             if e.evidence_class == EvidenceClass.DOCUMENT_CLAIM and not e.found)
    
    logger.info("Aggregation complete", 
                correlation_id=correlation_id,
                counts={k: len(v) for k, v in clean_evidences.items()},
                hallucinations=hallucination_count)

    return {
        "evidences": clean_evidences,
        "errors": new_errors,
        # FR-005: If integrity failed, judges should technically know
        "metadata": {"pipeline_integrity": "FAILED" if new_errors else "SUCCESS"}
    }
