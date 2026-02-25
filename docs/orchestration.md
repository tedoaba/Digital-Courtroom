# Orchestration Documentation

## Overview

The Digital Courtroom uses **LangGraph** to coordinate a multi-agent swarm. The workflow is divided into layers (0-4) to ensure deterministic synchronization, parallel execution, and structured reporting.

## Swarm Architecture

### Layer 0: Context Initialization

- **Node**: `ContextBuilder`
- **Role**: Validates repository URL and PDF specification path. Loads evaluation criteria (Rubric).

### Layer 1: Forensic Detectives (Parallel Fan-Out)

- **Nodes**: `RepoInvestigator`, `DocAnalyst`, `VisionInspector`
- **Performance**: Enforced 120s timeout per node.
- **Goal**: Collect raw evidence from codebases and documentation.

### Layer 1.5: Evidence Aggregation

- **Node**: `EvidenceAggregator`
- **Role**: Synchronizes and deduplicates findings. Flags missing sources or security violations.

### Layer 2: Dialectical Judicial Agents (Parallel Fan-Out)

- **Node**: `evaluate_criterion` (Multi-instanced)
- **Agents**: Prosecution, Defense, Tech Lead.
- **Role**: Evaluate evidence against specific rubric dimensions.

### Layer 3: Deterministic Synthesis

- **Node**: `ChiefJustice`
- **Role**: Resolves conflicting opinions using strict precedence. Triggers re-evaluation if variance > 2.

### Layer 4: Final Reporting

- **Node**: `ReportGenerator`
- **Role**: Renders Markdown report and serializes the `run_manifest.json`.

## CLI Usage

### Basic Command

```bash
uv run audit --repo <GITHUB_URL> --spec <PDF_PATH>
```

### Options

- `--repo`: (Required) The HTTPS URL of the GitHub repository to audit.
- `--spec`: (Required) Path to the design/specification PDF.
- `--rubric`: (Optional) Path to the rubric JSON file (Default: `rubric/week2_rubric.json`).
- `--output`: (Optional) Base directory for report artifacts (Default: `audit/reports/`).

## Fault Tolerance

- **Timeouts**: Every detective and judge node is wrapped in a 120s timeout.
- **Graceful Failure**: If a node fails, the swarm routes to `ErrorHandler`, which tags the failure and allows `ReportGenerator` to produce a partial result.
- **Manifest**: The `run_manifest.json` always contains a `status` field (`SUCCESS` or `FAILED`) to ensure automated pipelines can detect issues.

## Re-evaluation Loops

If the `ChiefJustice` detects significant disagreement among judges (variance > 2), it will trigger a one-time re-evaluation cycle. The `re_eval_count` in `AgentState` ensures this never results in an infinite loop.
