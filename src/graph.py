"""
End-to-End LangGraph Orchestrator for the Digital Courtroom.
Wires together all forensic and judicial nodes into a deterministic swarm.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Union
import operator
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from src.state import AgentState
from src.utils.logger import StructuredLogger
from src.utils.orchestration import timeout_wrapper

# Node Imports
from src.nodes.context_builder import build_context
from src.nodes.detectives import repo_investigator, doc_analyst, vision_inspector
from src.nodes.evidence_aggregator import aggregator_node
from src.nodes.judges import evaluate_criterion, evaluate_batch_criterion, execute_judicial_layer
from src.nodes.justice import chief_justice_node, route_after_justice
from src.nodes.report_generator import report_generator_node
from src.nodes.error_handler import error_handler_node

# Initialize global logger
logger = StructuredLogger("orchestrator")

# Apply Timeouts (SC-004: increased to 900s to support slow models and multiple retries)
timed_repo_investigator = timeout_wrapper(900)(repo_investigator)
timed_doc_analyst = timeout_wrapper(900)(doc_analyst)
timed_vision_inspector = timeout_wrapper(900)(vision_inspector)
timed_evaluate_criterion = timeout_wrapper(900)(evaluate_criterion)
timed_evaluate_batch_criterion = timeout_wrapper(900)(evaluate_batch_criterion)

# Routing Functions for US2 (Fault Tolerance)
def route_after_aggregator(state: AgentState) -> Union[List[Send], str]:
    """Routes to judicial layer (parallel) or error handler."""
    # US2: Proceed to judicial layer even if partial errors occurred.
    # We only stop if there's a truly catastrophic failure (e.g. no dimensions)
    if not state.get("rubric_dimensions"):
        return "error_handler"
    return execute_judicial_layer(state)

def route_after_justice_with_errors(state: AgentState) -> str:
    """Routes after justice, checking for errors first."""
    # US2: Proceed to report/re-eval even if errors occurred (they will be in the log)
    return route_after_justice(state)

def create_graph() -> StateGraph:
    """Creates the LangGraph definition for the swarm."""
    builder = StateGraph(AgentState)
    
    # 1. Add Nodes
    builder.add_node("context_builder", build_context)
    
    # Layer 1: Detectives
    builder.add_node("repo_investigator", timed_repo_investigator)
    builder.add_node("doc_analyst", timed_doc_analyst)
    builder.add_node("vision_inspector", timed_vision_inspector)
    
    # Layer 1.5: Aggregation
    builder.add_node("aggregator", aggregator_node)
    
    # Layer 2: Judges (parallel via Send)
    builder.add_node("evaluate_criterion", timed_evaluate_criterion)
    builder.add_node("evaluate_batch_criterion", timed_evaluate_batch_criterion)
    
    # Layer 3: Justice
    builder.add_node("chief_justice", chief_justice_node)
    
    # Finalization
    builder.add_node("report_generator", report_generator_node)
    builder.add_node("error_handler", error_handler_node)
    
    # 2. Define Edges
    builder.add_edge(START, "context_builder")
    
    # Detective Fan-Out
    builder.add_edge("context_builder", "repo_investigator")
    builder.add_edge("context_builder", "doc_analyst")
    builder.add_edge("context_builder", "vision_inspector")
    
    # Detective Fan-In (Synchronization Point)
    builder.add_edge("repo_investigator", "aggregator")
    builder.add_edge("doc_analyst", "aggregator")
    builder.add_edge("vision_inspector", "aggregator")
    
    # Judge Fan-Out (Conditional Send)
    builder.add_conditional_edges(
        "aggregator",
        route_after_aggregator,
        ["evaluate_criterion", "evaluate_batch_criterion", "error_handler"]
    )
    
    # Judge Fan-In
    builder.add_edge("evaluate_criterion", "chief_justice")
    builder.add_edge("evaluate_batch_criterion", "chief_justice")
    
    # Justice Routing (Re-evaluation Loop or Report)
    builder.add_conditional_edges(
        "chief_justice",
        route_after_justice_with_errors,
        {
            "judges": "aggregator",
            "report": "report_generator",
            "error_handler": "error_handler"
        }
    )
    
    builder.add_edge("report_generator", END)
    builder.add_edge("error_handler", "report_generator") # Fatal path
    
    return builder

# Compile the graph
courtroom_swarm = create_graph().compile()

if __name__ == "__main__":
    print("Graph compiled successfully.")
