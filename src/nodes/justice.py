import re
import pathlib
from datetime import datetime
from typing import Any, Dict, List, Optional
import math
from decimal import Decimal, ROUND_HALF_UP
from jinja2 import Environment, FileSystemLoader
from src.state import CriterionResult, JudicialOpinion, Evidence, AgentState, AuditReport
from src.utils.logger import StructuredLogger

logger = StructuredLogger("justice_node")

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


def sanitize_repo_name(name: str) -> str:
    r"""
    Sanitizes repository name for use in filesystem paths.
    
    Removes traversal sequences (../), Windows reserved characters (\/:*?"<>|),
    and reduces multiple dots to underscores to prevent security risks and 
    ensure cross-platform path stability. (FR-014, FR-016)

    Args:
        name: The raw repository name (e.g., from URL).

    Returns:
        A filesystem-safe string with invalid characters replaced by underscores.
    """
    # Replace common traversal and special chars with underscore
    # Aligned with Windows/Linux reserved character constraints
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', name)
    sanitized = re.sub(r'\.\.+', '_', sanitized)
    return sanitized.lstrip('_')


def get_report_workspace(repo_name: str) -> pathlib.Path:
    """
    Initializes and returns a timestamped workspace directory for audit artifacts.
    
    Creates a directory at `audit/reports/{repo_name}/{YYYYMMDD_HHMMSS}/` relative 
    to the project root. This ensures successive runs for the same repository 
    do not overwrite each other. (FR-009)

    Args:
        repo_name: The name of the repository being audited.

    Returns:
        pathlib.Path: The absolute path to the newly created workspace.
    """
    sanitized_name = sanitize_repo_name(repo_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Root anchoring via pathlib - assumes this file is in src/nodes/
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    workspace = root / "audit" / "reports" / sanitized_name / timestamp

    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def report_generator(state: AgentState) -> AgentState:
    """
    Layer 4 Node: Transforms synthesized AuditReport into human-readable Markdown.
    (FR-001, FR-007, US1)
    """
    logger.log_node_entry("report_generator")

    try:
        # 1. Prepare Metadata
        repo_url = state.get("repo_url", "unknown")
        repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url
        
        # 2. Calculate Global Score
        results = state.get("criterion_results", {})
        scores = [r.numeric_score for r in results.values()]
        global_score = round_half_up(sum(scores) / len(scores), 1) if scores else 0.0
        
        # 3. Create AuditReport Object
        report = AuditReport(
            repo_name=repo_name,
            run_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            git_hash="HEAD", # Placeholder
            rubric_version="1.0",
            results=results,
            summary=state.get("summary", "No summary provided."),
            global_score=global_score,
            remediation_plan=None # Derived in template for now
        )
        
        # 4. Initialize Workspace
        workspace = get_report_workspace(repo_name)
        
        # 5. Render Markdown
        # Root is 3 levels up from src/nodes/justice.py (project root)
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        template_dir = root / "src" / "templates"
        
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template("report.md.j2")
        
        # FR-011: Truncate Evidence content for rendering
        evidences = state.get("evidences", {})
        display_evidences = {}
        full_evidence_list = []
        for src, e_list in evidences.items():
            display_evidences[src] = []
            for e in e_list:
                full_evidence_list.append(e)
                # Clone for display to avoid mutating state
                e_display = e.model_copy()
                if e_display.content and len(e_display.content) > 5000:
                    e_display = e_display.model_copy(
                        update={"content": e_display.content[:5000] + "\n\n[TRUNCATED]"}
                    )
                display_evidences[src].append(e_display)

        # Prepare context for template
        context = report.model_dump()
        context["evidences"] = display_evidences
        
        # US2: Full JSON log for the collapsible block
        import json
        checksum_log = [e.model_dump(mode="json") for e in full_evidence_list]
        context["checksum_log_json"] = json.dumps(checksum_log, indent=2)
        
        rendered = template.render(**context)
        
        # 6. Write to Files
        report_path = workspace / "report.md"
        report_path.write_text(rendered, encoding="utf-8")
        
        # US2: run_manifest.json (FR-008)
        manifest_path = workspace / "run_manifest.json"
        manifest_data = {
            "report": report.model_dump(mode="json"),
            "evidences": checksum_log,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "generator": "Digital-Courtroom/ReportGenerator"
            }
        }
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        
        logger.log_verdict_delivered(f"Report saved to {report_path}")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return fallback_render(state, e)

    return state


def fallback_render(state: AgentState, error: Exception) -> AgentState:
    """FR-007: Generates a basic error report if the main generator fails."""
    logger.warning(f"Using fallback rendering due to error: {error}")
    # Basic implementation for US1 reliability
    repo_url = state.get("repo_url", "unknown")
    repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url
    
    workspace = get_report_workspace(repo_name)
    report_path = workspace / "report_FAULT.md"
    
    content = f"# SYSTEM FAULT REPORT: {repo_name}\n\n"
    content += "An error occurred during report generation.\n\n"
    content += f"**Timestamp**: {datetime.now().isoformat()}\n"
    content += f"**Error**: `{str(error)}`\n"
    
    report_path.write_text(content, encoding="utf-8")
    return state
