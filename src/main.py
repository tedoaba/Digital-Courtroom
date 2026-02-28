"""
CLI Entry Point for the Digital Courtroom Audit System.
Handles user inputs and initiates the LangGraph orchestration.
"""

import argparse
import asyncio
import sys
import uuid

from dotenv import load_dotenv

# Load environment variables from .env before any other imports that might depend on them
load_dotenv()

from src.config import hardened_config
from src.graph import courtroom_swarm
from src.utils.logger import StructuredLogger
from src.utils.observability import DashboardManager

logger = StructuredLogger("cli")


async def amain():
    parser = argparse.ArgumentParser(description="Digital Courtroom Audit CLI")
    parser.add_argument("--repo", required=True, help="GitHub Repository URL")
    parser.add_argument("--spec", required=True, help="Path to Specification PDF")
    parser.add_argument(
        "--output", help="Output directory for reports", default="audit/reports/"
    )
    parser.add_argument(
        "--rubric", help="Path to rubric JSON", default="rubric/week2_rubric.json"
    )
    parser.add_argument(
        "--dashboard", action="store_true", help="Enable real-time TUI dashboard"
    )

    args = parser.parse_args()

    from pydantic import ValidationError
    from src.state import AuditRequest

    try:
        validated_request = AuditRequest(**vars(args))
    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        sys.exit(2)

    # FR-003: Hardening - Verify Vault key at startup
    if not hardened_config.vault_key:
        logger.warning(
            "COURTROOM_VAULT_KEY is missing. Decryption of protected secrets will fail."
        )

    correlation_id = str(uuid.uuid4())

    # Initialize Observability
    dashboard = None
    if args.dashboard:
        dashboard = DashboardManager()
        dashboard.start()
        logger.info("TUI Dashboard enabled.", correlation_id=correlation_id)

    # Initialize basic state
    initial_state = {
        "repo_url": validated_request.repo,
        "pdf_path": validated_request.spec,
        "rubric_path": validated_request.rubric,
        "rubric_dimensions": [],
        "synthesis_rules": {},
        "evidences": {},
        "opinions": [],
        "criterion_results": {},
        "errors": [],
        "metadata": {
            "correlation_id": correlation_id,
            "run_status": "STARTED",
        },
        "re_eval_count": 0,
        "re_eval_needed": False,
    }

    logger.info(f"Starting audit for {validated_request.repo}", correlation_id=correlation_id)

    try:
        config = {
            "configurable": {"thread_id": correlation_id},
        }

        # FR-009: Observability - Wrap graph nodes to update dashboard
        # This is a bit complex without custom graph listeners,
        # but the nodes themselves now have @node_traceable.
        # We could also use graph.astream() to monitor events.

        final_state = await courtroom_swarm.ainvoke(initial_state, config=config)

        errors = final_state.get("errors", [])
        if errors:
            logger.warning(f"Audit completed with {len(errors)} errors.")

        logger.info("Audit workflow completed successfully.")
        if dashboard:
            dashboard.stop()
        sys.exit(0)

    except KeyboardInterrupt:
        logger.error("Audit interrupted by user.")
        if dashboard:
            dashboard.stop()
        sys.exit(130)
    except Exception as e:
        err_type = type(e).__name__
        logger.critical(f"Catastrophic failure in orchestration ({err_type}): {e}")
        if dashboard:
            dashboard.stop()
        sys.exit(3)


def main():
    """Synchronous entry point for project.scripts."""
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
