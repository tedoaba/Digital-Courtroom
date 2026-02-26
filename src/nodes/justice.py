import re
import pathlib
from datetime import datetime
from typing import Any, Dict, List, Optional
import math
from decimal import Decimal, ROUND_HALF_UP
from jinja2 import Environment, FileSystemLoader
from src.state import CriterionResult, JudicialOpinion, Evidence, AgentState, AuditReport
from src.utils.logger import StructuredLogger
from src.utils.orchestration import (
    sanitize_repo_name, 
    get_report_workspace, 
    round_half_up, 
    round_score, 
    SynthesisError
)

logger = StructuredLogger("justice_node")




def chief_justice_node(state: AgentState) -> AgentState:
    """
    Consolidates varying judicial opinions deterministically using strict precedence rules.
    (FR-001, FR-002, FR-008, FR-009)
    """
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    logger.log_node_entry("chief_justice_node", correlation_id=correlation_id)
    
    opinions = state.get("opinions", [])
    evidences = state.get("evidences", {})
    
    # 1. Group opinions by criterion
    grouped_opinions: Dict[str, List[JudicialOpinion]] = {}
    for op in opinions:
        if op.criterion_id not in grouped_opinions:
            grouped_opinions[op.criterion_id] = []
        grouped_opinions[op.criterion_id].append(op)
    
    criterion_results: Dict[str, CriterionResult] = {}
    
    # 2. Process each criterion
    for criterion_id, ops in grouped_opinions.items():
        criterion_results[criterion_id] = synthesize_criterion(criterion_id, ops, evidences)
    
    # 3. Calculate Re-evaluation Needed (FR-005)
    re_eval_needed = any(res.re_evaluation_required for res in criterion_results.values())
    
    # 4. Limit cycles (max 1)
    current_re_eval_count = state.get("re_eval_count", 0)
    if re_eval_needed and current_re_eval_count < 1:
        state["re_eval_needed"] = True
        state["re_eval_count"] = current_re_eval_count + 1
        logger.info(f"Re-evaluation triggered (cycle {state['re_eval_count']})", correlation_id=correlation_id)
    else:
        state["re_eval_needed"] = False
    
    # 5. Update state
    state["criterion_results"] = criterion_results
    
    return state


def route_after_justice(state: AgentState) -> str:
    """
    Conditional edge routing after Chief Justice synthesis.
    Routes back to Judges if re-evaluation is needed, or proceed to Report.
    """
    if state.get("re_eval_needed", False):
        return "judges"
    return "report"


def synthesize_criterion(
    criterion_id: str, 
    opinions: List[JudicialOpinion], 
    evidences: Dict[str, List[Evidence]]
) -> CriterionResult:
    """
    Performs deterministic synthesis for a single rubric dimension.
    Hierarchy: 1. Security Override, 2. Fact Supremacy, 3. FunctionALITY Weight
    """
    applied_rules = []
    execution_log = {"criterion_id": criterion_id, "penalties": [], "events": []}
    
    # Pre-process evidence for fast lookup
    evidence_pool = {}
    for source_list in evidences.values():
        for e in source_list:
            evidence_pool[e.evidence_id] = e

    # --- FR-009: Missing Judge Fallback ---
    num_judges = len(opinions)
    if num_judges == 0:
        raise SynthesisError(f"Zero judges for {criterion_id}")
    elif num_judges < 3:
        applied_rules.append("DEGRADED_SYNTHESIS")

    # --- FR-003: Raw Variance Calculation ---
    raw_scores = [op.score for op in opinions]
    variance = max(raw_scores) - min(raw_scores)
    execution_log["raw_scores"] = {op.judge: op.score for op in opinions}
    execution_log["raw_variance"] = variance

    # --- FR-005: Fact Supremacy Penalty ---
    adjusted_opinions = []
    for op in opinions:
        score = op.score
        found_hallucination = False
        for eid in op.cited_evidence:
            ev = evidence_pool.get(eid)
            if not ev or not ev.found:
                found_hallucination = True
                break
        
        if found_hallucination:
            score = max(1, score - 2)
            applied_rules.append("FACT_SUPREMACY_PENALTY")
            execution_log["penalties"].append(f"{op.judge} penalized for invalid evidence citation.")
        
        adjusted_opinions.append({"judge": op.judge, "score": score, "original_op": op})

    # --- FR-006: Functionality Weighting ---
    weights = {"Prosecutor": 1.0, "Defense": 1.0, "TechLead": 2.0}
    total_weighted_score = 0.0
    total_weight = 0.0
    
    for adj in adjusted_opinions:
        w = weights.get(adj["judge"], 1.0)
        total_weighted_score += adj["score"] * w
        total_weight += w
    
    final_float = total_weighted_score / total_weight
    execution_log["weighted_calc"] = {
        "final_float": final_float
    }

    # --- FR-004: Security Override ---
    security_violation = False
    
    # 1. Evidence-based override
    from src.state import EvidenceClass
    for ev in evidence_pool.values():
        if ev.found and ev.evidence_class == EvidenceClass.SECURITY_VIOLATION:
            security_violation = True
            execution_log["events"].append(f"Security override: verified violation {ev.evidence_id}")
            break
            
    # 2. Prosecutor keyword override
    if not security_violation:
        sec_keywords = {
            "shell injection", "rce", "hardcoded credentials", 
            "path traversal", "sql injection", "xss", "insecure deserialization"
        }
        for op in opinions:
            if op.judge == "Prosecutor" and op.charges:
                for charge in op.charges:
                    if any(kw in charge.lower() for kw in sec_keywords):
                        security_violation = True
                        execution_log["events"].append(f"Security override: Prosecutor signal in charges: {charge}")
                        break
    
    if security_violation:
        final_float = min(final_float, 3.0)
        applied_rules.append("SECURITY_OVERRIDE")

    final_int = round_score(final_float)
    execution_log["final_int"] = final_int

    # --- FR-007, FR-010, FR-015: Results Generation ---
    re_evaluation = variance > 2
    dissent = None
    if variance > 0:
        # Template-based summary (Research §Decision: Deterministic Dissent Summary)
        p_op = next((op for op in opinions if op.judge == "Prosecutor"), None)
        d_op = next((op for op in opinions if op.judge == "Defense"), None)
        t_op = next((op for op in opinions if op.judge == "TechLead"), None)
        
        prefix = "Major conflict detected" if variance > 2 else "Nuanced consensus"
        dissent = f"{prefix} (variance={variance}). "
        if t_op:
            dissent += f"Tech Lead assessed {t_op.score}. "
        if p_op and p_op.score != t_op.score:
            dissent += f"Prosecutor argued for {p_op.score}. "
        if d_op and d_op.score != t_op.score:
            dissent += f"Defense highlighted factors for {d_op.score}. "

    # Aggregate remediation
    remediations = []
    for op in opinions:
        if op.remediation:
            remediations.append(op.remediation)
    
    # --- FR-010: Final Narrative Reasoning (SC-004) ---
    p_op = next((op for op in opinions if op.judge == "Prosecutor"), None)
    d_op = next((op for op in opinions if op.judge == "Defense"), None)
    t_op = next((op for op in opinions if op.judge == "TechLead"), None)
    
    reasoning_parts = []
    
    # Prefix based on consensus
    if variance == 0:
        reasoning_parts.append(f"Unanimous consensus at {final_int}/5.")
    elif variance <= 2:
        reasoning_parts.append(f"Nuanced consensus reached at {final_int}/5.")
    else:
        reasoning_parts.append(f"Significant judicial conflict detected (Variance: {variance}).")

    # Add specific judge signals
    if p_op and p_op.score < 3 and p_op.charges:
        reasoning_parts.append(f"Prosecutor flagged critical risks: {'; '.join(p_op.charges[:2])}.")
    
    if d_op and d_op.score > 3 and d_op.mitigations:
        reasoning_parts.append(f"Defense highlighted mitigating factors: {'; '.join(d_op.mitigations[:2])}.")
        
    if security_violation:
        reasoning_parts.append("CRITICAL: Score capped due to verified security violations.")
    
    if t_op:
        reasoning_parts.append(f"Tech Lead weighted synthesis prioritized architectural { 'stability' if t_op.score >= 3 else 'risks' }.")

    final_reasoning = " ".join(reasoning_parts)

    return CriterionResult(
        criterion_id=criterion_id,
        numeric_score=final_int,
        reasoning=final_reasoning,
        relevance_confidence=1.0,
        judge_opinions=opinions,
        dissent_summary=dissent,
        remediation=" | ".join(remediations) if remediations else None,
        applied_rules=list(set(applied_rules)),
        execution_log=execution_log,
        security_violation_found=security_violation,
        re_evaluation_required=re_evaluation
    )



def fallback_render(state: AgentState, error: Exception) -> AgentState:
    """FR-007: Generates a basic error report if the main generator fails."""
    # This logic will be moved to report_generator.py in next task
    return state
