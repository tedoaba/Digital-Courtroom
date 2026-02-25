from typing import Any, Dict, List, Optional
import math
from decimal import Decimal, ROUND_HALF_UP
from src.state import CriterionResult, JudicialOpinion, Evidence, AgentState, AuditReport

class SynthesisError(Exception):
    """Raised when synthesis fails due to missing inputs."""
    pass


def round_half_up(n: float, decimals: int = 0) -> float:
    """
    Standard "round half up" logic (2.5 -> 3, 2.49 -> 2).
    Python's native round() uses "round half to even".
    """
    multiplier = 10**decimals
    return float(math.floor(n * multiplier + 0.5) / multiplier)


def round_score(score: float) -> int:
    """
    Deterministic score rounding to nearest integer (int 1-5).
    Uses Decimal for absolute precision as per Principle XXIV.
    """
    return int(
        Decimal(str(score)).quantize(Decimal("1"), rounding=ROUND_HALF_UP),
    )


def chief_justice_node(state: AgentState) -> AgentState:
    """
    Consolidates varying judicial opinions deterministically using strict precedence rules.
    (FR-001, FR-002, FR-008, FR-009)
    """
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
    
    # 3. Calculate Global Audit Report (T004)
    # Note: Report generation might be Phase 7, but we can do a preliminary one or just update state
    state["criterion_results"] = criterion_results
    
    return state


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

    # --- FR-007, FR-010: Results Generation ---
    re_evaluation = variance > 2
    dissent = None
    if re_evaluation:
        # Template-based dissent summary (Research §Decision: Deterministic Dissent Summary)
        p_op = next((op for op in opinions if op.judge == "Prosecutor"), None)
        d_op = next((op for op in opinions if op.judge == "Defense"), None)
        t_op = next((op for op in opinions if op.judge == "TechLead"), None)
        
        dissent = f"Major conflict detected (variance={variance}). "
        if p_op:
            dissent += f"The Prosecutor argued for {p_op.score} citing {', '.join(p_op.cited_evidence) or 'no evidence'}. "
        if d_op:
            dissent += f"The Defense argued for {d_op.score} highlighting {', '.join(d_op.mitigations) if d_op.mitigations else 'no mitigations'}. "
        if t_op:
            dissent += f"The Tech Lead's pragmatic assessment of {t_op.score} was used as the primary anchor."

    # Aggregate remediation
    remediations = []
    for op in opinions:
        if op.remediation:
            remediations.append(op.remediation)
    
    return CriterionResult(
        criterion_id=criterion_id,
        numeric_score=final_int,
        reasoning="Synthesis report generated deterministically.",
        relevance_confidence=1.0,
        judge_opinions=opinions,
        dissent_summary=dissent,
        remediation=" | ".join(remediations) if remediations else None,
        applied_rules=list(set(applied_rules)),
        execution_log=execution_log,
        security_violation_found=security_violation,
        re_evaluation_required=re_evaluation
    )
