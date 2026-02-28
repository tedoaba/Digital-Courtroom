import datetime
import re
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send
from pydantic import BaseModel, ValidationError

from src.config import judicial_settings
from src.nodes.judicial_nodes import bounded_llm_call, get_concurrency_controller
from src.state import AgentState, JudicialOpinion, JudicialOutcome
from src.utils.logger import StructuredLogger
from src.utils.observability import node_traceable

logger = StructuredLogger("judges")


class JudicialTask(TypedDict):
    """
    Task definition for a single judge evaluating a single criterion.
    Used for LangGraph Send parallelization.
    """

    judge_name: str
    criterion_id: str
    criterion_description: str
    evidences: dict[str, Any]  # dict[str, list[Evidence]]
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


PROSECUTOR_PHILOSOPHY = (
    'You apply a "Critical Lens" (Philosophy: "Trust No One. '
    'Assume Vibe Coding. Actively look for security vulnerabilities and code smells"). '
    "Operate strictly as an adversary hunting anomalies. Target shortcuts, "
    "unhandled exceptions, hidden attack vectors, and brittle architecture. "
    "Demand perfection; interpret ambiguity automatically as fatal flaws. "
    "Expose hardcoded secrets or logical fallacies relentlessly."
)

DEFENSE_PHILOSOPHY = (
    'You apply an "Optimistic Lens" (Philosophy: "Reward Effort and Intent. '
    'Assume good faith and prioritize partial implementation over missing features"). '
    "Highlight achievements. Emphasize constructive aspects, praising partial solutions "
    "while contextualizing technical debt reasonably. Defend pragmatic choices, "
    "assuming good faith behind each design decision. Support progression toward functionality."
)

TECHLEAD_PHILOSOPHY = (
    'You apply a "Pragmatic Lens" (Philosophy: "Does it work? Is it maintainable? '
    'Focus on architectural stability and real-world viability"). '
    "Assess deployability first. Balance theoretical purity alongside actual "
    "production constraints. Measure system resilience, ongoing maintenance burden, "
    "and efficient execution. Judge primarily whether solutions scale sustainably "
    "within current team boundaries."
)


def get_philosophy(judge_name: str) -> str:
    if judge_name == "Prosecutor":
        return PROSECUTOR_PHILOSOPHY
    if judge_name == "Defense":
        return DEFENSE_PHILOSOPHY
    if judge_name == "TechLead":
        return TECHLEAD_PHILOSOPHY
    return TECHLEAD_PHILOSOPHY  # Fallback


def get_google_llm(model_name: str):
    # Dynamic LLM fetching logic
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = judicial_settings.api_key
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=judicial_settings.llm_temperature,
        google_api_key=api_key,
    )


def get_ollama_llm(model_name: str):
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model_name,
        temperature=judicial_settings.llm_temperature,
        base_url=judicial_settings.ollama_base_url,
    )


async def _invoke_llm_with_validation(llm, messages, retries=0, schema=JudicialOutcome):
    """Internal helper to invoke LLM with schema retry (separate from 429 retries)."""
    structured_llm = llm.with_structured_output(schema)
    try:
        return await structured_llm.ainvoke(messages)
    except ValidationError as e:
        if retries < 2:
            schema_reminder = HumanMessage(
                content=f"Your previous response failed schema validation. Please fix these errors and try again: {e}",
            )
            messages.append(schema_reminder)
            return await _invoke_llm_with_validation(
                llm,
                messages,
                retries=retries + 1,
                schema=schema,
            )
        raise e
    except Exception as e:
        logger.error(
            f"LLM invocation failed: {e!s}",
            payload={"messages_len": len(messages)},
        )
        raise e


@node_traceable
async def evaluate_criterion(task: JudicialTask) -> dict[str, list[JudicialOpinion]]:
    judge = task["judge_name"]
    criterion_id = task["criterion_id"]
    criterion_description = task["criterion_description"]
    evidences = task["evidences"]
    correlation_id = task.get("correlation_id", "unknown")

    logger.log_node_entry(
        "evaluate_criterion",
        judge=judge,
        criterion_id=criterion_id,
        correlation_id=correlation_id,
    )

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    opinion_id = f"{judge}_{criterion_id}_{timestamp}"

    evidence_text = _format_evidence(evidences)

    model_name = getattr(
        judicial_settings,
        f"{judge.lower()}_model",
        judicial_settings.techlead_model,
    )

    system_prompt = f"""You are the {judge} in a digital courtroom.
{get_philosophy(judge)}

You are evaluating the criterion '{criterion_id}': {criterion_description}

Review the following synchronized evidence collected by the detectives:
{evidence_text}

Provide your evaluation in a STRICT JSON format. 
The following fields are REQUIRED:
- `criterion_id`: MUST be exactly '{criterion_id}'
- `judge`: MUST be exactly '{judge}'
- `score`: An INTEGER from 1 (poor) to 5 (excellent)
- `argument`: A detailed text string explaining your rationale
- `cited_evidence`: A list of strings containing the `evidence_id` values you used. If none, use `['NO_EVIDENCE']`.

Optional fields:
- `mitigations`: (For Defense) List of strings
- `charges`: (For Prosecutor) List of strings
- `remediation`: (For TechLead) Strategy string

Ensure you return ONLY the JSON object. Do not add markdown wrappers around the JSON.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Evaluate the evidence and provide your opinion."),
    ]

    controller = get_concurrency_controller()

    async def llm_call():
        if judicial_settings.judicial_provider == "google":
            llm = get_google_llm(model_name)
        else:
            llm = get_ollama_llm(model_name)
        # Use JudicialOutcome for structured output parsing
        outcome = await _invoke_llm_with_validation(
            llm,
            messages,
            schema=JudicialOutcome,
        )

        # Transform JudicialOutcome -> JudicialOpinion by injecting the ID
        return JudicialOpinion(
            opinion_id=opinion_id,
            **outcome.model_dump(),
        )

    try:
        result = await bounded_llm_call(
            controller=controller,
            agent=judge,
            dimension=criterion_id,
            llm_callable=llm_call,
        )
        logger.log_opinion_rendered(
            f"{judge} on {criterion_id}",
            correlation_id=correlation_id,
            score=result.score,
        )
        return {"opinions": [result]}
    except Exception as e:
        logger.error(
            f"Fallback {judge} for {criterion_id} due to persistent error: {e}",
            correlation_id=correlation_id,
        )

        # ATTEMPT: Manual extraction from the raw error if possible (for non-compliant JSON)
        err_msg = str(e)
        extracted_score = 3
        extracted_argument = f"System Error: Judicial evaluation failed after retries. Error: {err_msg[:200]}"

        # If the error contains a partial response (typical in Pydantic/LangChain error messages)
        score_match = re.search(r"'score':\s*(\d+)", err_msg)
        if score_match:
            try:
                extracted_score = int(score_match.group(1))
            except ValueError:
                pass

        arg_match = re.search(r"'argument':\s*'([^']*)'", err_msg)
        if arg_match:
            extracted_argument = f"[PARTIAL_VALIDATION] {arg_match.group(1)}"

        fallback_opinion = JudicialOpinion(
            opinion_id=opinion_id,
            judge=judge,  # type: ignore
            criterion_id=criterion_id,
            score=extracted_score,
            argument=extracted_argument,
            cited_evidence=[],
            mitigations=None,
            charges=None,
            remediation=None,
        )
        return {
            "opinions": [fallback_opinion],
            "errors": [
                f"Persistent failure for judge {judge} on criterion {criterion_id}: {err_msg}",
            ],
        }


@node_traceable
async def evaluate_batch_criterion(
    task: JudicialBatchTask,
) -> dict[str, list[JudicialOpinion]]:
    """
    Structured Batching Node (US3).
    Evaluates ALL dimensions for a single judge in one call.
    Includes logic for partial success, corrupt entries, and individual retries.
    """
    judge = task["judge_name"]
    dimensions = task["dimensions"]
    evidences = task["evidences"]
    correlation_id = task.get("correlation_id", "unknown")

    logger.log_node_entry(
        "evaluate_batch_criterion",
        judge=judge,
        dimension_count=len(dimensions),
        correlation_id=correlation_id,
    )

    evidence_text = _format_evidence(evidences)
    criteria_list = "\n".join([f"- {d['id']}: {d['description']}" for d in dimensions])

    system_prompt = f"""You are the {judge} in a digital courtroom.
{get_philosophy(judge)}

You are evaluating MULTIPLE criteria in a single batch.
Review the following synchronized evidence collected by the detectives:
{evidence_text}

Evaluate the following criteria:
{criteria_list}

Provide your response as a JSON object containing a key 'opinions' which is a LIST of JudicialOpinion results.
Each object in the 'opinions' list MUST have:
- `criterion_id`: The ID of the criterion (e.g., 'DIM1')
- `judge`: '{judge}'
- `score`: INTEGER (1-5)
- `argument`: Detailed rationale string
- `cited_evidence`: List of `evidence_id` strings or `['NO_EVIDENCE']`

Example: {{"opinions": [{{"criterion_id": "DIM1", "judge": "{judge}",
"score": 4, "argument": "...", "cited_evidence": ["..."]}}]}}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content="Evaluate all provided criteria and return a structured JSON list of opinions.",
        ),
    ]

    controller = get_concurrency_controller()

    model_name = getattr(
        judicial_settings,
        f"{judge.lower()}_model",
        judicial_settings.techlead_model,
    )

    async def llm_call():
        if judicial_settings.judicial_provider == "google":
            llm = get_google_llm(model_name)
        else:
            llm = get_ollama_llm(model_name)

        class BatchOutcomeResponse(BaseModel):
            opinions: list[JudicialOutcome]

        structured_llm = llm.with_structured_output(BatchOutcomeResponse)
        return await structured_llm.ainvoke(messages)

    try:
        # Create a custom settings object with longer timeout for the batch call
        class BatchSettingsWrapper:
            def __init__(self, original):
                for k, v in original.__dict__.items():
                    setattr(self, k, v)
                # Override timeout if batch specific timeout exists
                self.llm_call_timeout = getattr(
                    original,
                    "batch_llm_call_timeout",
                    300.0,
                )

        batch_settings = BatchSettingsWrapper(judicial_settings)

        batch_result = await bounded_llm_call(
            controller=controller,
            agent=judge,
            dimension="BATCH",
            llm_callable=llm_call,
            settings=batch_settings,
        )

        received_outcomes = batch_result.opinions

        # Transform JudicialOutcomes -> JudicialOpinions
        received_opinions = []
        for i, outcome in enumerate(received_outcomes):
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            op_id = f"{judge}_{outcome.criterion_id}_{ts}_{i}"
            received_opinions.append(
                JudicialOpinion(opinion_id=op_id, **outcome.model_dump()),
            )

        received_ids = {op.criterion_id for op in received_opinions}

        # FR-005: Handle Missing or Corrupt items (partial success logic)
        final_opinions = list(received_opinions)
        missing_dims = [d for d in dimensions if d["id"] not in received_ids]

        if missing_dims:
            logger.warning(
                f"Batch incomplete for {judge}. Missing {len(missing_dims)} IDs. Starting granular retries.",
            )
            for dim in missing_dims:
                # Trigger individual call for missing item
                retry_task = JudicialTask(
                    judge_name=judge,
                    criterion_id=dim["id"],
                    criterion_description=dim["description"],
                    evidences=evidences,
                )
                res = await evaluate_criterion(retry_task)
                final_opinions.extend(res["opinions"])

        logger.log_opinion_rendered(
            f"{judge} BATCH",
            correlation_id=correlation_id,
            count=len(final_opinions),
        )
        return {"opinions": final_opinions}

    except Exception as e:
        # FR-004 Fallback: If the whole batch fails, fall back to individual calls for the whole set
        logger.error(
            f"Whole batch evaluation failed for {judge} due to {e}. Falling back to individual dimension calls.",
        )
        all_opinions = []
        for dim in dimensions:
            task = JudicialTask(
                judge_name=judge,
                criterion_id=dim["id"],
                criterion_description=dim["description"],
                evidences=evidences,
            )
            res = await evaluate_criterion(task)
            all_opinions.extend(res["opinions"])

        logger.log_opinion_rendered(
            f"{judge} BATCH FALLBACK",
            correlation_id=correlation_id,
            count=len(all_opinions),
        )
        return {"opinions": all_opinions}


def _format_evidence(evidences: dict) -> str:
    """Helper to format evidence for prompts."""
    if not evidences:
        return "- NO_EVIDENCE: No evidence was found by detectives."

    text = ""
    for _cat, ev_list in evidences.items():
        for e in ev_list:
            e_id = getattr(
                e,
                "evidence_id",
                e.get("evidence_id") if isinstance(e, dict) else "unknown",
            )
            e_class = getattr(
                e,
                "evidence_class",
                e.get("evidence_class") if isinstance(e, dict) else "unknown",
            )
            e_conf = getattr(
                e,
                "confidence",
                e.get("confidence") if isinstance(e, dict) else 0.0,
            )
            e_content = getattr(
                e,
                "content",
                e.get("content") if isinstance(e, dict) else "",
            )
            e_class_val = getattr(e_class, "value", e_class)
            text += f"- ID: {e_id} | Class: {e_class_val} | Confidence: {e_conf}\n  Content: {e_content}\n"
    return text


@node_traceable
def execute_judicial_layer(state: AgentState) -> list[Send]:
    """Fan-out function to launch judicial evaluations."""
    controller = get_concurrency_controller()
    controller.start_job()

    dimensions = state.get("rubric_dimensions", [])
    evidences = state.get("evidences", {})
    correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
    judges = ["Prosecutor", "Defense", "TechLead"]

    sends = []
    redundancy = judicial_settings.judicial_redundancy_factor

    # FR-005: Optional Batching Toggle
    if judicial_settings.batching_enabled:
        for judge in judges:
            for i in range(redundancy):
                task = JudicialBatchTask(
                    judge_name=judge,
                    dimensions=dimensions,
                    evidences=evidences,
                    correlation_id=f"{correlation_id}_r{i}",
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
                for i in range(redundancy):
                    task = JudicialTask(
                        judge_name=judge,
                        criterion_id=crit_id,
                        criterion_description=crit_desc,
                        evidences=evidences,
                        correlation_id=f"{correlation_id}_r{i}",
                    )
                    sends.append(Send("evaluate_criterion", task))

    return sends
