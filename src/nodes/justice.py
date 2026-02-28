from src.state import AgentState, CriterionResult, Evidence, JudicialOpinion
from src.utils.logger import StructuredLogger
from src.utils.observability import node_traceable
from src.utils.orchestration import (
    SynthesisError,
    round_score,
)

logger = StructuredLogger("justice_node")


@node_traceable
def chief_justice_node(state: AgentState) -> AgentState:
    """
    Consolidates varying judicial opinions deterministically using strict precedence rules.
    (FR-001, FR-002, FR-008, FR-009)
    """
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    logger.log_node_entry("chief_justice_node", correlation_id=correlation_id)

    opinions = state.get("opinions", [])
    evidences = state.get("evidences", {})
    rubric_dimensions = state.get("rubric_dimensions", [])

    # Map dimension IDs to names for the result
    dimension_map = {d["id"]: d.get("name", d["id"]) for d in rubric_dimensions}

    # 1. Group opinions by criterion
    grouped_opinions: dict[str, list[JudicialOpinion]] = {}
    for op in opinions:
        if op.criterion_id not in grouped_opinions:
            grouped_opinions[op.criterion_id] = []
        grouped_opinions[op.criterion_id].append(op)

    criterion_results: dict[str, CriterionResult] = {}

    # 2. Process each criterion
    for criterion_id, ops in grouped_opinions.items():
        name = dimension_map.get(criterion_id, criterion_id)
        criterion_results[criterion_id] = synthesize_criterion(
            criterion_id,
            name,
            ops,
            evidences,
        )

    # 3. Calculate Re-evaluation Needed (FR-005)
    re_eval_needed = any(res.re_evaluation_required for res in criterion_results.values())

    # 4. Limit cycles (max 1)
    current_re_eval_count = state.get("re_eval_count", 0)
    if re_eval_needed and current_re_eval_count < 1:
        state["re_eval_needed"] = True
        state["re_eval_count"] = current_re_eval_count + 1
        logger.info(
            f"Re-evaluation triggered (cycle {state['re_eval_count']})",
            correlation_id=correlation_id,
        )
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
    dimension_name: str,
    opinions: list[JudicialOpinion],
    evidences: dict[str, list[Evidence]],
) -> CriterionResult:
    """
    Performs deterministic synthesis for a single rubric dimension.
    Hierarchy: 1. Security Override, 2. Fact Supremacy, 3. FunctionALITY Weight
    """
    applied_rules = []
    execution_log = {
        "criterion_id": criterion_id,
        "dimension_name": dimension_name,
        "penalties": [],
        "events": [],
        "synthesis_path": "STANDARD_WEIGHTED_AVERAGE",
    }

    # Pre-process evidence for fast lookup
    evidence_pool = {}
    for source_list in evidences.values():
        for e in source_list:
            evidence_pool[e.evidence_id] = e

    # --- FR-009: Missing Judge Fallback ---
    num_judges = len(opinions)
    if num_judges == 0:
        raise SynthesisError(f"Zero judges for {criterion_id}")
    if num_judges < 3:
        applied_rules.append("DEGRADED_SYNTHESIS")
        execution_log["synthesis_path"] = "DEGRADED_SYNTHESIS"

    # --- FR-003: Redundancy & Leader Election (013-ironclad-hardening) ---
    judge_groups = {}
    for op in opinions:
        if op.judge not in judge_groups:
            judge_groups[op.judge] = []
        judge_groups[op.judge].append(op)

    elected_opinions = []
    for judge_type, group in judge_groups.items():
        if len(group) == 1:
            elected_opinions.append(group[0])
        else:
            # Leader Election: Select the opinion with the most evidence cited,
            # or the highest score if detail is tied (preferring non-fallback arguments).
            leader = max(
                group,
                key=lambda op: (
                    len(op.cited_evidence) if op.cited_evidence and op.cited_evidence[0] != "NO_EVIDENCE" else 0,
                    op.score if "[PARTIAL_VALIDATION]" not in op.argument else -1,
                    len(op.argument),
                ),
            )
            elected_opinions.append(leader)
            applied_rules.append(f"LEADER_ELECTION_{judge_type.upper()}")
            execution_log["events"].append(
                f"Leader elected for {judge_type} from {len(group)} redundant instances.",
            )

    # Proceed with elected opinions for synthesis
    synthesis_opinions = elected_opinions

    # --- FR-003: Raw Variance Calculation ---
    raw_scores = [op.score for op in synthesis_opinions]
    variance = max(raw_scores) - min(raw_scores)
    execution_log["raw_scores"] = {op.judge: op.score for op in synthesis_opinions}
    execution_log["raw_variance"] = variance

    # --- FR-005: Fact Supremacy Penalty ---
    adjusted_opinions = []
    for op in synthesis_opinions:
        score = op.score
        found_hallucination = False
        invalid_citations = []
        for eid in op.cited_evidence:
            ev = evidence_pool.get(eid)
            if not ev or not ev.found:
                found_hallucination = True
                invalid_citations.append(eid)
                break

        if found_hallucination:
            score = max(1, score - 2)
            applied_rules.append("FACT_SUPREMACY_PENALTY")
            execution_log["penalties"].append(
                f"{op.judge} penalized for invalid evidence citation: {', '.join(invalid_citations)}.",
            )
            execution_log["synthesis_path"] = "FACT_SUPREMACY_OVERRIDE"

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
        "final_float": final_float,
        "weights_applied": weights,
    }

    # --- FR-004: Security Override ---
    security_violation = False

    # 1. Evidence-based override
    from src.state import EvidenceClass

    for ev in evidence_pool.values():
        if ev.found and ev.evidence_class == EvidenceClass.SECURITY_VIOLATION:
            security_violation = True
            execution_log["events"].append(
                f"Security override: verified violation {ev.evidence_id}",
            )
            break

    # 2. Prosecutor keyword override
    if not security_violation:
        sec_keywords = {
            "shell injection",
            "rce",
            "hardcoded credentials",
            "path traversal",
            "sql injection",
            "xss",
            "insecure deserialization",
            "os.system",
            "unsafe clone",
        }
        for op in synthesis_opinions:
            if op.judge == "Prosecutor" and op.charges:
                for charge in op.charges:
                    if any(kw in charge.lower() for kw in sec_keywords):
                        security_violation = True
                        execution_log["events"].append(
                            f"Security override: Prosecutor signal in charges: {charge}",
                        )
                        break

    if security_violation:
        final_float = min(final_float, 3.0)
        applied_rules.append("SECURITY_OVERRIDE")
        execution_log["synthesis_path"] = "SECURITY_SUPREMACY_CAP"

    final_int = round_score(final_float)
    execution_log["final_int"] = final_int

    # --- FR-007, FR-010, FR-015: Results Generation ---
    re_evaluation = variance > 2
    dissent = None
    if variance > 0:
        p_op = next((op for op in synthesis_opinions if op.judge == "Prosecutor"), None)
        d_op = next((op for op in synthesis_opinions if op.judge == "Defense"), None)
        t_op = next((op for op in synthesis_opinions if op.judge == "TechLead"), None)

        prefix = "Major conflict detected" if variance > 2 else "Nuanced consensus"
        dissent = f"{prefix} (variance={variance}). "
        if t_op:
            dissent += f"Tech Lead assessed {t_op.score}. "
        if p_op and (not t_op or p_op.score != t_op.score):
            dissent += f"Prosecutor argued for {p_op.score}. "
        if d_op and (not t_op or d_op.score != t_op.score):
            dissent += f"Defense highlighted factors for {d_op.score}. "

    # Aggregate remediation with unique filtering and cleaning
    unique_remediations = []
    seen = set()
    for op in synthesis_opinions:
        if op.remediation:
            clean = op.remediation.strip()
            if clean and clean.lower() not in seen:
                unique_remediations.append(clean)
                seen.add(clean.lower())

    # --- FR-010: Final Narrative Reasoning (SC-004) ---
    p_op = next((op for op in synthesis_opinions if op.judge == "Prosecutor"), None)
    d_op = next((op for op in synthesis_opinions if op.judge == "Defense"), None)
    t_op = next((op for op in synthesis_opinions if op.judge == "TechLead"), None)

    reasoning_parts = []

    if variance == 0:
        reasoning_parts.append(f"**Unanimous consensus** at {final_int}/5.")
    elif variance <= 2:
        reasoning_parts.append(f"**Nuanced consensus** reached at {final_int}/5.")
    else:
        reasoning_parts.append(
            f"**Significant judicial conflict detected** (Variance: {variance}).",
        )

    if p_op and p_op.score < 3 and p_op.charges:
        # Use first 3 charges for brevity
        charges_text = "; ".join([c.strip() for c in p_op.charges if c.strip()][:3])
        reasoning_parts.append(f"Prosecutor flagged critical risks: _{charges_text}_.")

    if d_op and d_op.score > 3 and d_op.mitigations:
        mits_text = "; ".join([m.strip() for m in d_op.mitigations if m.strip()][:3])
        reasoning_parts.append(
            f"Defense highlighted mitigating factors: _{mits_text}_.",
        )

    if security_violation:
        reasoning_parts.append(
            "**CRITICAL**: Score capped due to verified security violations.",
        )

    if t_op:
        focus = "stability" if t_op.score >= 3 else "risks"
        reasoning_parts.append(
            f"Tech Lead weighted synthesis prioritized architectural {focus}.",
        )

    final_reasoning = " ".join(reasoning_parts)

    return CriterionResult(
        criterion_id=criterion_id,
        dimension_name=dimension_name,
        numeric_score=final_int,
        reasoning=final_reasoning,
        relevance_confidence=1.0,
        judge_opinions=opinions,
        dissent_summary=dissent,
        remediation="\n".join([f"- {r}" for r in unique_remediations]) if unique_remediations else None,
        applied_rules=list(set(applied_rules)),
        execution_log=execution_log,
        security_violation_found=security_violation,
        re_evaluation_required=re_evaluation,
    )


def fallback_render(state: AgentState, _error: Exception) -> AgentState:
    """FR-007: Generates a basic error report if the main generator fails."""
    return state
