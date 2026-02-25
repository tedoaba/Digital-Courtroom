# Research: Dialectical Judicial Agents (Layer 2)

## Research Tasks

| ID  | Task                          | Goal                                                                                                                              |
| --- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| R-1 | Prompt Overlap Analysis       | Determine how to ensure < 10% overlap between Prosecutor, Defense, and TechLead system prompts.                                   |
| R-2 | LangGraph Loop/Map Patterns   | Research LangGraph `Send` API or `map` patterns to implement "one LLM call per persona per criterion" (Granular parallelization). |
| R-3 | Structured Output Retry Logic | Best pattern for catching `OutputParserException` and triggering the 2-retry loop with customized "schema reminder" prompts.      |

## Findings

### R-1: Prompt Overlap & Persona Fidelity

- **Decision**: Use a "Philosophy Block" strategy. Each persona prompt is composed of:
  1. Base System Instructions (common instructions for citing evidence).
  2. **Unique Philosophy Block** (the directive: critical vs. optimistic vs. pragmatic).
  3. Contextual Data (rubric + evidence).
- **Rationale**: The < 10% overlap constraint targets the "Character Philosophy" section. By isolating the core directive, we can maximize persona divergence.
- **Verification**: Similarity check can be performed via Jaccard similarity in unit tests.

### R-2: Granular Parallelization via LangGraph `Send`

- **Decision**: Use the LangGraph **Map-Reduce** pattern with the `Send` API.
- **Rationale**: Instead of 3 fixed nodes, we will dynamically generate a "Judicial Task" state for each (Persona, Criterion) pair.
- **Structure**:
  - `EvidenceAggregator` calculates the list of `(persona, criterion)` pairs.
  - Each pair is "sent" to a generic `evaluate_criterion` node.
  - Result is collected via the `opinions` list reducer (`operator.add`).
- **Alternatives**: Hardcoding 30 nodes (rejected as unscalable); Batching (rejected by spec).

### R-3: Structured Output Resilience

- **Decision**: Wrap `.with_structured_output()` in a recursive helper function with a `retry_count` parameter.
- **Rationale**: Enables injecting "Schema Reminder: Please ensure all cited evidence IDs are strings" into the prompt of the second and third attempts.
- **Fallback Implementation**: If `retry_count == 2` fails, return the `JudicialOpinion(score=3, argument="...")` model directly.

## Technology Choices

| Tech         | Choice                                     | Rationale                                                                                                |
| ------------ | ------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Architecture | LangGraph `Send`                           | Native support for dynamic fan-out; manages parallel LLM calls efficiently.                              |
| LLM Binding  | `.with_structured_output(JudicialOpinion)` | Constitutional requirement (Principle IV); ensures type safety.                                          |
| Prompting    | F-Strings / String Join                    | Prefer standard Python formatting over Jinja2 for internal prompt construction to minimize dependencies. |

## Unresolved Decision Points (Resolved in Planning)

- **Uniqueness of evidence IDs**: Resolved by spec (format: `{source}_{class}_{index}`).
- **Granular timeouts**: Handled via `RunnableConfig` in LangChain.
