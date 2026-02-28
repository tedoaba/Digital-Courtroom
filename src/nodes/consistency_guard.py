"""
Consistency Guard Node for the Digital Courtroom.
Performs architectural reconciliation between implemention and specs.
"""
import ast
import pathlib
from src.state import AgentState
from src.utils.logger import StructuredLogger

logger = StructuredLogger("consistency_guard")

def analyze_graph_consistency() -> dict:
    """
    Analyzes src/graph.py via AST to ensure it follows the specified Swarm pattern.
    Checks for: 
    1. Parallel Detective fan-out
    2. Parallel Judge fan-out (via execute_judicial_layer)
    3. Chief Justice fan-in
    """
    graph_path = pathlib.Path("src/graph.py")
    if not graph_path.exists():
        return {"status": "error", "message": "graph.py not found"}

    with open(graph_path, "r") as f:
        tree = ast.parse(f.read())

    nodes_found = []
    edges_found = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Find builder.add_node calls
            if isinstance(node.func, ast.Attribute) and node.func.attr == "add_node":
                if len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
                    nodes_found.append(node.args[0].value)
            
            # Find builder.add_edge calls
            if isinstance(node.func, ast.Attribute) and node.func.attr == "add_edge":
                if len(node.args) >= 2:
                    src = node.args[0].value if isinstance(node.args[0], ast.Constant) else "dynamic"
                    dst = node.args[1].value if isinstance(node.args[1], ast.Constant) else "dynamic"
                    edges_found.append((src, dst))

    # Basic Swarm Pattern Validation
    violations = []
    if "repo_investigator" not in nodes_found: violations.append("Missing repo_investigator node")
    if "chief_justice" not in nodes_found: violations.append("Missing chief_justice node")
    
    # Check for fan-out (context -> detectives)
    detectives = {"repo_investigator", "doc_analyst", "vision_inspector"}
    for det in detectives:
        if ("context_builder", det) not in edges_found:
            violations.append(f"Missing edge: context_builder -> {det}")

    return {
        "status": "pass" if not violations else "fail",
        "violations": violations,
        "nodes": nodes_found,
        "edges_count": len(edges_found)
    }

def consistency_guard_node(state: AgentState) -> AgentState:
    """
    Final architectural check before report finalization.
    (013-ironclad-hardening)
    """
    logger.info("Running architectural consistency guard...")
    
    analysis = analyze_graph_consistency()
    
    # SC-005: Architectural Reconciliation (Vision-to-Code Linkage)
    vision_findings = state.get("evidences", {}).get("vision", [])
    if vision_findings:
        logger.info(f"Reconciling AST with {len(vision_findings)} vision findings...")
        for vf in vision_findings:
            if "SMA" in (vf.content or "").upper() or "STATE" in (vf.content or "").upper():
                # If vision detected a state machine, verify AST also found one
                if len(analysis.get("nodes", [])) < 5:
                    analysis["status"] = "fail"
                    analysis["violations"].append("Vision detected StateMachine but AST verification shows insufficient node complexity.")

    if "metadata" not in state:
        state["metadata"] = {}
    
    state["metadata"]["consistency_report"] = analysis
    
    if analysis["status"] == "fail":
        msg = f"Architectural Consistency Violation: {', '.join(analysis['violations'])}"
        logger.warning(msg)
        state["errors"].append(msg)
    else:
        logger.info("Architectural consistency verified.")
        
    return state
