<!--
Sync Impact Report
===================
Version change: 0.0.0 → 1.0.0
Modified principles: N/A (initial ratification)
Added sections:
  - Core Engineering Principles (7 principles)
  - Governance & Audit Principles (5 principles)
  - Architectural Constraints (5 principles)
  - Code & Repository Standards (4 principles)
  - Testing Requirements (5 principles)
  - Definition of Enforcement (3 rules)
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check section already present)
  - .specify/templates/spec-template.md ✅ (Requirements section compatible; no update needed)
  - .specify/templates/tasks-template.md ✅ (Test-first ordering already required; no update needed)
Follow-up TODOs: None
-->

# Digital Courtroom Constitution

## Core Engineering Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

1. Every feature MUST begin with a formal specification (`spec.md`) before any implementation work starts.
2. Implementation plans (`plan.md`) MUST be derived from the specification and approved before coding.
3. Tasks (`tasks.md`) MUST be generated from the plan and traced back to spec requirements.
4. No code MUST be written without a corresponding specification artifact.
5. Specifications MUST reference which Constitutional principles they satisfy.

### II. Test-Driven Development (NON-NEGOTIABLE)

1. Tests MUST be written before implementation for every specification.
2. The Red-Green-Refactor cycle MUST be strictly enforced: tests fail → implement → tests pass → refactor.
3. No implementation MUST be merged without corresponding passing tests.
4. Test files MUST exist in the repository before the implementation files they validate.

### III. Deterministic LangGraph State Transitions

1. All state transitions MUST be defined in a LangGraph `StateGraph` with typed state.
2. Conditional edges MUST use deterministic Python predicates, not LLM-generated routing.
3. Given identical inputs (repo snapshot + PDF), the detective layer MUST produce identical evidence.
4. Judicial score variance MUST be bounded within ±1 (mitigated by `temperature=0`).
5. Synthesis rules in `ChiefJusticeNode` MUST be fully deterministic Python logic — no LLM calls.

### IV. Schema-First Design

1. All state objects MUST be defined using Pydantic `BaseModel` or `TypedDict` with explicit field types.
2. `AgentState` MUST use `TypedDict` with `Annotated` reducers for parallel-safe state merging.
3. All LLM outputs MUST be validated against Pydantic schemas via `.with_structured_output()` or `.bind_tools()`.
4. Plain Python dictionaries MUST NOT be used to pass complex nested state between nodes.
5. Every schema MUST include field-level validation constraints (`ge`, `le`, `min_length`, etc.) where applicable.

### V. Strong Typing and Validation Enforcement

1. All function signatures MUST include type annotations for parameters and return values.
2. All API boundaries MUST enforce runtime type validation via Pydantic.
3. `Evidence.confidence` MUST be constrained to `[0.0, 1.0]`.
4. `JudicialOpinion.score` MUST be constrained to `[1, 5]`.
5. Schema violations from LLM outputs MUST trigger retry logic (max 2 retries) before fallback.

### VI. Parallel-Safe State Reducers

1. The `evidences` state field MUST use `Annotated[Dict[str, List[Evidence]], operator.ior]` to merge dictionaries from parallel detective branches.
2. The `opinions` state field MUST use `Annotated[List[JudicialOpinion], operator.add]` to append lists from parallel judge branches.
3. The `errors` and `execution_log` fields MUST use `Annotated[List[str], operator.add]`.
4. No parallel branch MUST write to a state key that another parallel branch also writes to, unless a reducer is defined.
5. Shared mutable state between parallel branches is PROHIBITED.

### VII. Explicit Error Handling Contracts

1. Every node MUST define its failure modes, retry logic, and fallback behavior.
2. Timeout errors and network errors MUST trigger retry with exponential backoff (max 3 retries).
3. Schema validation errors MUST trigger retry with an explicit schema reminder in the prompt (max 2 retries).
4. Invalid input errors MUST fail fast with a descriptive error message appended to `state.errors`.
5. Fatal errors MUST NOT crash the pipeline; the node MUST return a partial result with `found=False` and continue.
6. Structured error handling is REQUIRED in all critical workflows.
7. Silent failures are PROHIBITED. All errors MUST be informative, traceable, and safe.
8. Clear exception-handling policies MUST be established and adhered to across the architecture.

## Governance & Audit Principles

### VIII. Evidence Must Precede Judgment

1. Detective agents MUST complete evidence collection before any judicial evaluation begins.
2. Judges MUST NOT render opinions without citing specific `evidence_id` values from detective output.
3. The `EvidenceAggregator` synchronization node MUST validate evidence completeness before releasing to the judicial layer.

### IX. Separation of Fact Collection and Opinion

1. Detective agents (Layer 1) MUST produce only factual `Evidence` objects — no scores, no opinions, no interpretations.
2. Judge agents (Layer 2) MUST produce only `JudicialOpinion` objects — scores and arguments grounded in cited evidence.
3. No single node MUST perform both evidence collection and judicial evaluation.

### X. Dialectical Judicial Execution

1. Three distinct judge personas MUST exist: Prosecutor (critical lens), Defense (optimistic lens), and Tech Lead (pragmatic lens).
2. Judge system prompts MUST share less than 10% of their text content.
3. All three judges MUST evaluate the same evidence for each rubric criterion independently and in parallel.
4. The Chief Justice MUST summarize the conflict — explaining why judges disagreed and which side was overruled.

### XI. Rule-Based Synthesis

1. The following precedence hierarchy MUST be enforced in verdict synthesis:
   - **Priority 1 — SECURITY_OVERRIDE**: Confirmed security flaws cap the criterion score at 3.
   - **Priority 2 — FACT_SUPREMACY**: Forensic evidence (facts) always overrules judicial interpretation (opinions).
   - **Priority 3 — FUNCTIONALITY_WEIGHT**: Tech Lead score carries highest weight for architecture criteria.
   - **Priority 4 — DISSENT_REQUIREMENT**: The Chief Justice must summarize why the Prosecutor and Defense disagreed.
   - **Priority 5 — VARIANCE_RE_EVALUATION**: Score variance > 2 triggers explicit re-evaluation of specific evidence.

### XII. No Hallucinated Artifacts

1. Every file path, function name, or code snippet cited in a report MUST be cross-verified against actual detective evidence.
2. The `EvidenceAggregator` MUST flag any document claim referencing a non-existent file as `"Hallucinated Path"`.
3. If the Defense cites an `evidence_id` where `Evidence.found == False`, the Defense argument MUST be overruled under FACT_SUPREMACY.

## Architectural Constraints

### XIII. Hierarchical StateGraph Only

1. The system MUST be implemented as a single `StateGraph(AgentState)` using LangGraph.
2. The graph MUST follow the hierarchical layer decomposition: ContextBuilder → Detective Layer → EvidenceAggregator → Judicial Layer → ChiefJustice → ReportGenerator.
3. No ad-hoc agent orchestration (e.g., direct function call chains bypassing the graph) is permitted.

### XIV. Parallel Fan-Out / Fan-In Required

1. Detective agents (RepoInvestigator, DocAnalyst, VisionInspector) MUST execute in parallel via fan-out from ContextBuilder.
2. Judge agents (Prosecutor, Defense, TechLead) MUST execute in parallel via fan-out from EvidenceAggregator.
3. Fan-in synchronization nodes (EvidenceAggregator, ChiefJustice entry) MUST exist to collect all parallel outputs before downstream processing.
4. A purely linear pipeline (A→B→C→D) is a VIOLATION of this Constitution.

### XV. Tool Execution Must Be Isolated and Sandboxed

1. All `git clone` operations MUST target a `tempfile.TemporaryDirectory()` or `tempfile.mkdtemp()`.
2. All subprocess calls MUST use list-form arguments (`subprocess.run(["git", "clone", url, path])`) — never `shell=True`.
3. `os.system()` is PROHIBITED throughout the entire codebase.
4. All subprocess calls MUST include a `timeout` parameter (max 60 seconds).
5. Cloned code MUST be parsed via `ast.parse()` (static analysis only) — never imported, executed, or `eval()`'d.

### XVI. Immutable Evidence Objects

1. Once an `Evidence` object is created by a detective, it MUST NOT be modified by any downstream node.
2. Judges MUST receive a frozen snapshot of evidence.
3. Evidence objects MUST include a unique `evidence_id` (format: `{source}_{class}_{index}`) and a `timestamp` for traceability.

### XVII. Reproducible and Traceable Scoring

1. Every `CriterionResult` MUST include: `final_score`, `judge_opinions`, `dissent_summary` (if variance > 2), and `remediation`.
2. Every run MUST produce a `run_manifest.json` containing: input URL, PDF hash (SHA-256), rubric version, model names, temperature settings, and timestamp.
3. The final report MUST reference specific `evidence_id` values and `opinion_id` values for auditability.

## Code & Repository Standards

### XVIII. Atomic Commits Required

1. Every commit MUST represent a single logical change (e.g., one feature, one fix, one refactor).
2. The repository MUST contain more than 3 commits showing incremental development progression.
3. Commit messages MUST follow the format: `<type>: <description>` (e.g., `feat:`, `fix:`, `test:`, `docs:`, `refactor:`).

### XIX. No Monolithic Commits

1. A single commit containing the entire implementation ("init" or "bulk upload") is a VIOLATION.
2. Commits MUST demonstrate progressive development: setup → tools → detectives → judges → synthesis → testing.
3. Each phase of development MUST have at least one corresponding commit.

### XX. Explicit Module Boundaries & Modular Architecture

1. The codebase MUST follow the prescribed file structure with clear separation:
   - `src/state.py` — Pydantic models only.
   - `src/graph.py` — StateGraph definition only.
   - `src/nodes/` — One file per node layer (detectives, judges, justice, context_builder, evidence_aggregator).
   - `src/tools/` — One file per tool domain (repo_tools, doc_tools, vision_tools, ast_tools).
2. Cross-layer imports MUST follow the dependency direction: tools ← nodes ← graph.
3. Circular imports are PROHIBITED.
4. Clean, modular structure with proper separation of concerns MUST be maintained to promote scalability.
5. Hardcoded values are PROHIBITED. All environment-specific, configurable, or reusable values MUST be moved into centralized configuration files.

### XXI. Naming, Code Clarity, and Style (PEP8 & OOP)

1. Variable, function, and class names MUST be meaningful and intention-revealing.
2. Consistent naming conventions MUST be stringently followed across the codebase.
3. Ambiguous, shortened, or context-dependent identifiers are PROHIBITED.
4. All implementation MUST strictly adhere to PEP8 formatting and coding conventions.
5. Object-Oriented Programming (OOP) best practices MUST be utilized for all implementation where applicable, ensuring encapsulation, inheritance, and polymorphism are used effectively to design robust and maintainable classes.

### XXII. Structured Logging Mandatory

1. All node entry and exit events MUST emit structured JSON logs via `StructuredLogger`.
2. All evidence creation events MUST be logged with `evidence_id`, `source`, `class`, `found`, and `confidence`.
3. All opinion rendering events MUST be logged with `opinion_id`, `judge`, `criterion`, `score`, and `cited_evidence_count`.
4. All verdict events MUST be logged with `criterion`, `final_score`, `variance`, and `rules_applied`.
5. LangSmith tracing (`LANGCHAIN_TRACING_V2=true`) MUST be enabled for all runs.
6. Structured, leveled logging (e.g., INFO, WARNING, ERROR, DEBUG) MUST be enforced across all critical operations and integration points.
7. Logs MUST support robust debugging, monitoring, and auditability.

### XXIII. Package & Command Management (uv)

1. The `uv` package manager is MANDATORY for dependency installation, script execution, environment management, and any runtime command execution.
2. Documentation, run scripts, and execution instructions MUST consistently reflect `uv` usage exclusively.

### XXIV. Deterministic Outputs Under Identical Inputs

1. Detective layer output MUST be deterministic given identical repository snapshots and PDF files.
2. LLM calls MUST use `temperature=0` to minimize non-determinism.
3. The synthesis engine (ChiefJustice) MUST produce identical verdicts given identical judicial opinions and evidence.

## Testing Requirements

### XXV. Unit Tests Per Node

1. Every node in the StateGraph MUST have a corresponding unit test file in `tests/`.
2. Unit test structure and coverage expectations MUST be clearly defined and strictly met.
3. Unit tests MUST validate: correct output schema, proper state mutation, edge case handling, and error recovery.
4. Node tests MUST mock LLM calls and external tool invocations.

### XXVI. Integration Tests for Full Judicial Workflow

1. At least one end-to-end integration test MUST exercise the complete pipeline: ContextBuilder → Detectives → EvidenceAggregator → Judges → ChiefJustice → ReportGenerator.
2. Integration test structure and scope MUST be clearly defined, specifying exactly when integration vs. unit tests are required.
3. Integration tests MUST verify that fan-out/fan-in synchronization works correctly.
4. Integration tests MUST verify that state reducers merge parallel outputs without data loss.

### XXVII. Testing Architecture & Testability

1. Unit and integration tests MUST be separated logically across the repository.
2. Testability MUST be treated as a first-class architectural concern, designed explicitly into all components and workflows.

### XXVIII. Failure Case Tests

1. Tests MUST cover: missing repository (invalid URL), invalid PDF (corrupt or missing file), and security violation detection (`os.system` usage in target repo).
2. Tests MUST verify that the pipeline degrades gracefully — producing a partial report with error documentation rather than crashing.
3. Tests MUST verify that LLM schema violations trigger retry logic and eventual fallback.

### XXIX. Deterministic Scoring Verification Tests

1. Tests MUST verify that the ChiefJustice `synthesize_criterion` function produces correct scores given known judicial opinion inputs.
2. Tests MUST verify that SECURITY_OVERRIDE correctly caps scores at 3.
3. Tests MUST verify that FACT_SUPREMACY correctly nullifies Defense arguments citing non-existent evidence.
4. Tests MUST verify that high-variance (>2) triggers re-evaluation.

### XXX. CI Must Fail on Coverage Regression

1. Test coverage MUST NOT decrease between commits.
2. CI pipelines MUST enforce a minimum coverage threshold.
3. Any new node or tool MUST include tests before the implementation is merged.

## Definition of Enforcement

### E-1. Constitutional Review Gate

Any specification, plan, or implementation that violates this Constitution MUST fail review. The `Constitution Check` section in `plan-template.md` MUST validate compliance with all applicable principles before implementation proceeds.

### E-2. Spec-Constitution Traceability

Every specification (`spec.md`) and plan (`plan.md`) MUST reference which Constitutional principles (by number) they satisfy. Plans lacking Constitutional traceability MUST NOT proceed to task generation.

### E-3. No Implementation Without Tests

No implementation code MUST be merged into the main branch without corresponding tests. Test files MUST exist and fail (Red phase) before the implementation is written (Green phase).

## Governance

1. This Constitution supersedes all other development practices, guidelines, and conventions for the Digital Courtroom project.
2. Amendments to this Constitution MUST include: a description of the change, rationale, impact assessment, and a version bump following semantic versioning (MAJOR.MINOR.PATCH).
3. All pull requests and code reviews MUST verify compliance with this Constitution.
4. The rubric JSON (`rubric/week2_rubric.json`) is the single machine-readable source of truth for evaluation criteria and MUST NOT be contradicted by any specification.
5. Complexity deviations from this Constitution MUST be justified in the plan's `Complexity Tracking` section.

**Version**: 1.0.0 | **Ratified**: 2026-02-23 | **Last Amended**: 2026-02-23
