import datetime
import json
import logging
from typing import TypedDict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.state import AgentState, JudicialOpinion
from src.config import judicial_settings

logger = logging.getLogger(__name__)

class JudicialTask(TypedDict):
    """
    Task definition for a single judge evaluating a single criterion.
    Used for LangGraph Send parallelization.
    """
    judge_name: str
    criterion_id: str
    criterion_description: str
    evidences: dict[str, Any] # dict[str, list[Evidence]]

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
        model="gemini-2.5-flash", 
        temperature=judicial_settings.llm_temperature,
        google_api_key=api_key
    )

def get_ollama_llm():
    from langchain_ollama import ChatOllama
    
    return ChatOllama(
        model="qwen3-coder:480b-cloud",
        temperature=judicial_settings.llm_temperature,
        # base_url="http://localhost:11434" # Optional: clarify if Ollama is running elsewhere
    )

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def invoke_llm_with_retry(llm, messages, retries=0):
    """Invokes LLM with retry for schema compliance and exponential backoff for HTTP timeouts."""
    structured_llm = llm.with_structured_output(JudicialOpinion)
    try:
        return structured_llm.invoke(messages)
    except ValidationError as e:
        if retries < 2:
            schema_reminder = HumanMessage(content=f"Your previous response failed schema validation. Please fix these errors and try again: {e}")
            messages.append(schema_reminder)
            return invoke_llm_with_retry(llm, messages, retries=retries + 1)
        raise e

def evaluate_criterion(task: JudicialTask) -> dict[str, list[JudicialOpinion]]:
    judge = task["judge_name"]
    criterion_id = task["criterion_id"]
    criterion_description = task["criterion_description"]
    evidences = task["evidences"]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    opinion_id = f"{judge}_{criterion_id}_{timestamp}"
    
    # Format evidence for the prompt
    evidence_text = ""
    if not evidences:
        evidence_text = "- NO_EVIDENCE: No evidence was found by detectives."
    else:
        for cat, ev_list in evidences.items():
            for e in ev_list:
                # Handle both Evidence objects and raw dicts if necessary (for flexibility in tests)
                e_id = getattr(e, "evidence_id", e.get("evidence_id") if isinstance(e, dict) else "unknown")
                e_class = getattr(e, "evidence_class", e.get("evidence_class") if isinstance(e, dict) else "unknown")
                e_conf = getattr(e, "confidence", e.get("confidence") if isinstance(e, dict) else 0.0)
                e_content = getattr(e, "content", e.get("content") if isinstance(e, dict) else "")
                
                # If e_class is Enum, get its value
                e_class_val = getattr(e_class, "value", e_class)
                
                evidence_text += f"- ID: {e_id} | Class: {e_class_val} | Confidence: {e_conf}\n  Content: {e_content}\n"
                
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
    
    logger.info(f"Entry {judge} for {criterion_id}")
    try:
        llm = get_ollama_llm()
        result = invoke_llm_with_retry(llm, messages)
        result = result.model_copy(update={"opinion_id": opinion_id}) # ensure opinion id is correct
        logger.info(f"Exit {judge} for {criterion_id} with score {result.score}")
        return {"opinions": [result]}
    except Exception as e:
        logger.error(f"Fallback {judge} for {criterion_id} due to error: {e}")
        fallback_opinion = JudicialOpinion(
            opinion_id=opinion_id,
            judge=judge, # type: ignore
            criterion_id=criterion_id,
            score=3,
            argument="System Error: Judicial evaluation failed after retries.",
            cited_evidence=[],
            mitigations=None,
            charges=None,
            remediation=None
        )
        return {"opinions": [fallback_opinion]}

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send

def execute_judicial_layer(state: AgentState) -> list[Send]:
    """Fan-out function to launch judicial evaluations."""
    sends = []
    dimensions = state.get("rubric_dimensions", [])
    evidences = state.get("evidences", {})
    judges = ["Prosecutor", "Defense", "TechLead"]
    
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
                evidences=evidences
            )
            sends.append(Send("evaluate_criterion", task))
    
    return sends
