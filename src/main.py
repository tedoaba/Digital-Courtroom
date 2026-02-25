"""
CLI Entry Point for the Digital Courtroom Audit System.
Handles user inputs and initiates the LangGraph orchestration.
"""
import argparse
import sys
import uuid
from typing import Optional

from src.graph import courtroom_swarm
from src.utils.logger import StructuredLogger

logger = StructuredLogger("cli")

def main():
    parser = argparse.ArgumentParser(description="Digital Courtroom Audit CLI")
    parser.add_argument("--repo", required=True, help="GitHub Repository URL")
    parser.add_argument("--spec", required=True, help="Path to Specification PDF")
    parser.add_argument("--output", help="Output directory for reports", default="audit/reports/")
    parser.add_argument("--rubric", help="Path to rubric JSON", default="rubric/week2_rubric.json")
    
    args = parser.parse_args()
    
    correlation_id = str(uuid.uuid4())
    
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
        # Execute the graph
        config = {"configurable": {"thread_id": correlation_id}}
        final_state = courtroom_swarm.invoke(initial_state, config=config)
        
        # Check for errors in final state
        errors = final_state.get("errors", [])
        if errors:
            logger.warning(f"Audit completed with {len(errors)} errors.")
            for err in errors:
                logger.warning(f"  - {err}")
        
        # Success exit
        logger.info("Audit workflow completed successfully.")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.error("Audit interrupted by user.")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Catastrophic failure in orchestration: {e}")
        # Partial report should have been attempted by error_handler + report_generator in graph
        sys.exit(3)

if __name__ == "__main__":
    main()
