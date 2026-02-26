"""
CLI Entry Point for the Digital Courtroom Audit System.
Handles user inputs and initiates the LangGraph orchestration.
"""
import argparse
import sys
import uuid
import asyncio
import os
from typing import Optional

from src.graph import courtroom_swarm
from src.utils.logger import StructuredLogger
from src.config import settings, hardened_config
from src.utils.observability import DashboardManager

logger = StructuredLogger("cli")

async def main():
    parser = argparse.ArgumentParser(description="Digital Courtroom Audit CLI")
    parser.add_argument("--repo", required=True, help="GitHub Repository URL")
    parser.add_argument("--spec", required=True, help="Path to Specification PDF")
    parser.add_argument("--output", help="Output directory for reports", default="audit/reports/")
    parser.add_argument("--rubric", help="Path to rubric JSON", default="rubric/week2_rubric.json")
    parser.add_argument("--dashboard", action="store_true", help="Enable real-time TUI dashboard")
    
    args = parser.parse_args()
    
    # FR-003: Hardening - Verify Vault key at startup
    if not hardened_config.vault_key:
        logger.warning("COURTROOM_VAULT_KEY is missing. Decryption of protected secrets will fail.")

    correlation_id = str(uuid.uuid4())
    
    # Initialize Observability
    dashboard = None
    if args.dashboard:
        dashboard = DashboardManager()
        dashboard.start()
        logger.info("TUI Dashboard enabled.", correlation_id=correlation_id)

    # Initialize basic state
    initial_state = {
        "repo_url": args.repo,
        "pdf_path": args.spec,
        "rubric_path": args.rubric,
        "rubric_dimensions": [],
        "synthesis_rules": {},
        "evidences": {},
        "opinions": [],
        "criterion_results": {},
        "errors": [],
        "metadata": {
            "correlation_id": correlation_id,
            "run_status": "STARTED"
        },
        "re_eval_count": 0,
        "re_eval_needed": False
    }
    
    logger.info(f"Starting audit for {args.repo}", correlation_id=correlation_id)
    
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
        logger.critical(f"Catastrophic failure in orchestration: {e}")
        if dashboard:
             dashboard.stop()
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())
