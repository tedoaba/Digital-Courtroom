import asyncio
import datetime
import json
import logging
from typing import TypedDict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError

from pydantic import BaseModel, Field
from langgraph.types import Send
from src.state import AgentState, JudicialOpinion
from src.config import judicial_settings
from src.nodes.judicial_nodes import get_concurrency_controller, bounded_llm_call

from src.utils.logger import StructuredLogger

logger = StructuredLogger("judges")

class JudicialTask(TypedDict):
    """
    Task definition for a single judge evaluating a single criterion.
    Used for LangGraph Send parallelization.
    """
    judge_name: str
    criterion_id: str
    criterion_description: str
    evidences: dict[str, Any] # dict[str, list[Evidence]]
    correlation_id: str

class JudicialBatchTask(TypedDict):
    """
    Task definition for a single judge evaluating ALL criteria in one call.
    Used for Structured Batching (US3).
    """
    judge_name: str
    dimensions: list[dict]
    evidences: dict[str, Any]
    correlation_id: str

PROSECUTOR_PHILOSOPHY = """You apply a "Critical Lens" (Philosophy: "Trust No One. Assume Vibe Coding. Actively look for security vulnerabilities and code smells").
Operate strictly as an adversary hunting anomalies. Target shortcuts, unhandled exceptions, hidden attack vectors, and brittle architecture. Demand perfection; interpret ambiguity automatically as fatal flaws. Expose hardcoded secrets or logical fallacies relentlessly."""

DEFENSE_PHILOSOPHY = """You apply an "Optimistic Lens" (Philosophy: "Reward Effort and Intent. Assume good faith and prioritize partial implementation over missing features").
Highlight achievements. Emphasize constructive aspects, praising partial solutions while contextualizing technical debt reasonably. Defend pragmatic choices, assuming good faith behind each design decision. Support progression toward functionality."""

TECHLEAD_PHILOSOPHY = """You apply a "Pragmatic Lens" (Philosophy: "Does it work? Is it maintainable? Focus on architectural stability and real-world viability").
Assess deployability first. Balance theoretical purity alongside actual production constraints. Measure system resilience, ongoing maintenance burden, and efficient execution. Judge primarily whether solutions scale sustainably within current team boundaries."""

def get_philosophy(judge_name: str) -> str:
    if judge_name == "Prosecutor":
        return PROSECUTOR_PHILOSOPHY
    elif judge_name == "Defense":
        return DEFENSE_PHILOSOPHY
    elif judge_name == "TechLead":
        return TECHLEAD_PHILOSOPHY
    return TECHLEAD_PHILOSOPHY # Fallback

def get_google_llm():
    # Placeholder for LLM fetching logic
    from langchain_google_genai import ChatGoogleGenerativeAI
    api_key = judicial_settings.google_api_key or judicial_settings.gemini_api_key
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=judicial_settings.llm_temperature,
        google_api_key=api_key
    )

def get_ollama_llm():
    from langchain_ollama import ChatOllama
    
    return ChatOllama(
        model="qwen3-coder:480b-cloud",
        temperature=judicial_settings.llm_temperature,
    )

async def _invoke_llm_with_validation(llm, messages, retries=0):
    """Internal helper to invoke LLM with schema retry (separate from 429 retries)."""
    structured_llm = llm.with_structured_output(JudicialOpinion)
    try:
        return await structured_llm.ainvoke(messages)
    except ValidationError as e:
        if retries < 2:
            schema_reminder = HumanMessage(content=f"Your previous response failed schema validation. Please fix these errors and try again: {e}")
            messages.append(schema_reminder)
            return await _invoke_llm_with_validation(llm, messages, retries=retries + 1)
        raise e
    except Exception as e:
        logger.error(f"LLM invocation failed: {str(e)}", payload={"messages_len": len(messages)})
        raise e

async def evaluate_criterion(task: JudicialTask) -> dict[str, list[JudicialOpinion]]:
    judge = task["judge_name"]
    criterion_id = task["criterion_id"]
    criterion_description = task["criterion_description"]
    evidences = task["evidences"]
    correlation_id = task.get("correlation_id", "unknown")
    
    logger.log_node_entry("evaluate_criterion", judge=judge, criterion_id=criterion_id, correlation_id=correlation_id)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    opinion_id = f"{judge}_{criterion_id}_{timestamp}"
    
    evidence_text = _format_evidence(evidences)
                
    system_prompt = f"""You are the {judge} in a digital courtroom.
{get_philosophy(judge)}

You are evaluating the criterion '{criterion_id}': {criterion_description}

Review the following synchronized evidence collected by the detectives:
{evidence_text}

Provide your structured JudicialOpinion. 
You MUST exclusively cite `evidence_id` values from the provided evidence. If no evidence was provided, cite `['NO_EVIDENCE']`.
Ensure you adhere to the schema strictly.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Evaluate the evidence and provide your opinion.")
    ]
    
    controller = get_concurrency_controller()
    
    async def llm_call():
        llm = get_ollama_llm()
        return await _invoke_llm_with_validation(llm, messages)

    try:
        result = await bounded_llm_call(
            controller=controller,
            agent=judge,
            dimension=criterion_id,
            llm_callable=llm_call
        )
        result = result.model_copy(update={"opinion_id": opinion_id}) # ensure opinion id is correct
        logger.log_opinion_rendered(f"{judge} on {criterion_id}", correlation_id=correlation_id, score=result.score)
        return {"opinions": [result]}
    except Exception as e:
        logger.error(f"Fallback {judge} for {criterion_id} due to persistent error: {e}", correlation_id=correlation_id)
        fallback_opinion = JudicialOpinion(
            opinion_id=opinion_id,
            judge=judge, # type: ignore
            criterion_id=criterion_id,
            score=3,
            argument=f"System Error: Judicial evaluation failed after retries. Error: {str(e)[:100]}",
            cited_evidence=[],
            mitigations=None,
            charges=None,
            remediation=None
        )
        return {
            "opinions": [fallback_opinion],
            "errors": [f"Persistent failure for judge {judge} on criterion {criterion_id}: {str(e)}"]
        }

async def evaluate_batch_criterion(task: JudicialBatchTask) -> dict[str, list[JudicialOpinion]]:
    """
    Structured Batching Node (US3).
    Evaluates ALL dimensions for a single judge in one call.
    Includes logic for partial success, corrupt entries, and individual retries.
    """
    judge = task["judge_name"]
    dimensions = task["dimensions"]
    evidences = task["evidences"]
    correlation_id = task.get("correlation_id", "unknown")
    
    logger.log_node_entry("evaluate_batch_criterion", judge=judge, dimension_count=len(dimensions), correlation_id=correlation_id)
    
    evidence_text = _format_evidence(evidences)
    criteria_list = "\n".join([f"- {d['id']}: {d['description']}" for d in dimensions])
    
    system_prompt = f"""You are the {judge} in a digital courtroom.
{get_philosophy(judge)}

You are evaluating MULTIPLE criteria in a single batch.
Review the following synchronized evidence collected by the detectives:
{evidence_text}

Evaluate the following criteria:
{criteria_list}

Provide your response as a JSON LIST of JudicialOpinion results.
Example: [{"opinion_id": "...", "judge": "{judge}", "criterion_id": "DIM1", "score": 4, ...}, ...]
You MUST cite `evidence_id` values or `['NO_EVIDENCE']`.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Evaluate all provided criteria and return a structured JSON list of opinions.")
    ]
    
    controller = get_concurrency_controller()
    
    async def llm_call():
        llm = get_ollama_llm()
        # FR-004: Providers that don't support structured output for lists might fail here
        # We wrap in a list model for validation
        class BatchOpinionResponse(BaseModel):
            opinions: list[JudicialOpinion]
            
        structured_llm = llm.with_structured_output(BatchOpinionResponse)
        return await structured_llm.ainvoke(messages)

    try:
        # FR-004 Fallback: If BATCHING fails (e.g. timeout or context window), it might raise Exception
        batch_result = await bounded_llm_call(
            controller=controller,
            agent=judge,
            dimension="BATCH",
            llm_callable=llm_call
        )
        
        received_opinions = batch_result.opinions
        received_ids = {op.criterion_id for op in received_opinions}
        
        # FR-005: Handle Missing or Corrupt items (partial success logic)
        final_opinions = list(received_opinions)
        missing_dims = [d for d in dimensions if d["id"] not in received_ids]
        
        if missing_dims:
            logger.warning(f"Batch incomplete for {judge}. Missing {len(missing_dims)} IDs. Starting granular retries.")
            for dim in missing_dims:
                # Trigger individual call for missing item
                retry_task = JudicialTask(
                    judge_name=judge,
                    criterion_id=dim["id"],
                    criterion_description=dim["description"],
                    evidences=evidences
                )
                res = await evaluate_criterion(retry_task)
                final_opinions.extend(res["opinions"])
        
        logger.log_opinion_rendered(f"{judge} BATCH", correlation_id=correlation_id, count=len(final_opinions))
        return {"opinions": final_opinions}

    except Exception as e:
        # FR-004 Fallback: If the whole batch fails, fall back to individual calls for the whole set
        logger.error(f"Whole batch evaluation failed for {judge} due to {e}. Falling back to individual dimension calls.")
        all_opinions = []
        for dim in dimensions:
            task = JudicialTask(
                judge_name=judge,
                criterion_id=dim["id"],
                criterion_description=dim["description"],
                evidences=evidences
            )
            res = await evaluate_criterion(task)
            all_opinions.extend(res["opinions"])
        
        logger.log_opinion_rendered(f"{judge} BATCH FALLBACK", correlation_id=correlation_id, count=len(all_opinions))
        return {"opinions": all_opinions}

def _format_evidence(evidences: dict) -> str:
    """Helper to format evidence for prompts."""
    if not evidences:
        return "- NO_EVIDENCE: No evidence was found by detectives."
    
    text = ""
    for cat, ev_list in evidences.items():
        for e in ev_list:
            e_id = getattr(e, "evidence_id", e.get("evidence_id") if isinstance(e, dict) else "unknown")
            e_class = getattr(e, "evidence_class", e.get("evidence_class") if isinstance(e, dict) else "unknown")
            e_conf = getattr(e, "confidence", e.get("confidence") if isinstance(e, dict) else 0.0)
            e_content = getattr(e, "content", e.get("content") if isinstance(e, dict) else "")
            e_class_val = getattr(e_class, "value", e_class)
            text += f"- ID: {e_id} | Class: {e_class_val} | Confidence: {e_conf}\n  Content: {e_content}\n"
    return text

def execute_judicial_layer(state: AgentState) -> list[Send]:
    """Fan-out function to launch judicial evaluations."""
    controller = get_concurrency_controller()
    controller.start_job()
    
    dimensions = state.get("rubric_dimensions", [])
    evidences = state.get("evidences", {})
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    judges = ["Prosecutor", "Defense", "TechLead"]
    
    sends = []
    
    # FR-005: Optional Batching Toggle
    if judicial_settings.batching_enabled:
        for judge in judges:
            task = JudicialBatchTask(
                judge_name=judge,
                dimensions=dimensions,
                evidences=evidences,
                correlation_id=correlation_id
            )
            sends.append(Send("evaluate_batch_criterion", task))
    else:
        # Sequential-like fan-out for individual criterions
        for dim in dimensions:
            crit_id = dim.get("id")
            crit_desc = dim.get("description", "")
            if not crit_id:
                continue
            for judge in judges:
                task = JudicialTask(
                    judge_name=judge, 
                    criterion_id=crit_id,
                    criterion_description=crit_desc,
                    evidences=evidences,
                    correlation_id=correlation_id
                )
                sends.append(Send("evaluate_criterion", task))
    
    return sends
