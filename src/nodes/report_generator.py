"""
Final Report Generation Node for the Digital Courtroom.
Translates AgentState into a human-readable Markdown Audit Report.
"""

import json
import pathlib
from datetime import datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.state import AgentState, AuditReport
from src.utils.logger import StructuredLogger
from src.utils.manifest import ManifestManager
from src.utils.observability import node_traceable
from src.utils.orchestration import get_report_workspace, round_half_up

logger = StructuredLogger("report_generator")


@node_traceable
def report_generator_node(state: AgentState) -> dict[str, Any]:
    """
    Report Generator Node.
    Synthesizes the final verdict and renders the Markdown output.
    """
    try:
        correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
        logger.log_node_entry("report_generator", correlation_id=correlation_id)

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
            git_hash="HEAD",  # Placeholder for actual git hash if available
            rubric_version="1.1",
            results=results,
            summary="Full automated audit completed by Digital Courtroom swarm.",
            global_score=global_score,
            remediation_plan=None,
        )

        # 4. Initialize Workspace
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        workspace = get_report_workspace(
            repo_url,
            base_dir=str(root / "audit" / "reports"),
        )

        # 5. Render Markdown
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        template_dir = root / "src" / "templates"

        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
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
                        update={
                            "content": e_display.content[:5000] + "\n\n[TRUNCATED]",
                        },
                    )
                display_evidences[src].append(e_display)

        # Prepare context for template
        context = report.model_dump()
        context["evidences"] = display_evidences

        # Serialize evidence for the manifest and the checksum log
        checksum_log = [e.model_dump(mode="json") for e in full_evidence_list]
        context["checksum_log_json"] = json.dumps(checksum_log, indent=2)

        rendered = template.render(**context)

        # 6. Write to Files
        report_path = workspace / "report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        # 7. Save Manifest (T014)
        ManifestManager.save_manifest(
            str(workspace),
            state.get("metadata", {}),
            state.get("errors", []),
        )

        logger.log_verdict_delivered(
            f"Audit completed: {repo_name}",
            correlation_id=correlation_id,
            workspace=str(workspace),
        )

        return {
            "final_report": report,
        }

    except Exception as e:
        correlation_id = state.get("metadata", {}).get("correlation_id", "unknown")
        logger.error(f"Report generation failed: {e}", correlation_id=correlation_id)
        # In case of failure, we still want to save what we can
        return fallback_save(state, e)


def fallback_save(state: AgentState, error: Exception) -> dict[str, Any]:
    """Saves a minimal failure report to disk."""
    repo_url = state.get("repo_url", "unknown")
    repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url

    try:
        root = pathlib.Path(__file__).resolve().parent.parent.parent
        workspace = get_report_workspace(
            repo_url,
            base_dir=str(root / "audit" / "reports"),
        )
        report_path = workspace / "report_ERROR.md"

        content = f"# SYSTEM FAULT REPORT: {repo_name}\n\n"
        content += "An error occurred during report generation.\n\n"
        content += f"**Timestamp**: {datetime.now().isoformat()}\n"
        content += f"**Error**: `{error!s}`\n"
        content += f"**Collected Errors**: {state.get('errors', [])}\n"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {}
    except Exception:
        # If even this fails, dump to stdout as a last resort
        logger.error(f"FATAL: Could not even save error report. Error: {error}")
        return {}
