"""
Premium Production-Grade CLI for the Digital Courtroom.
Implements a high-fidelity TUI dashboard with live log streaming and fixed headers.
"""
import argparse
import sys
import asyncio
import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich import box

# Load environment variables
load_dotenv()

from src.graph import courtroom_swarm
from src.config import hardened_config

console = Console()

class LogBufferHandler(logging.Handler):
    """Aggressive handler to capture courtroom logs and prevent terminal leakage."""
    def __init__(self, buffer: List[Text]):
        super().__init__()
        self.buffer = buffer
        self.max_size = 22

    def emit(self, record):
        try:
            msg = self.format(record)
            # Try to parse as JSON first (our StructuredLogger format)
            try:
                data = json.loads(msg)
                ts = data.get("timestamp", "").split("T")[-1][:8]
                severity = data.get("severity", "INFO")
                event = data.get("event_type", "event").replace("_", " ").title()
                content = data.get("message", "")
                
                sev_color = "green" if severity == "INFO" else "yellow" if severity == "WARNING" else "bold red"
                event_color = "cyan" if "node" in event.lower() else "magenta" if "opinion" in event.lower() else "blue"
                
                line = Text()
                line.append(f"[{ts}] ", style="dim")
                line.append(f"{severity:<7} ", style=sev_color)
                line.append(f"» {event:<18} ", style=f"bold {event_color}")
                line.append(content, style="white")
            except:
                # Fallback for plain text logs
                ts = datetime.now().strftime("%H:%M:%S")
                line = Text()
                line.append(f"[{ts}] ", style="dim")
                line.append(f"{record.levelname:<7} ", style="dim yellow")
                line.append(f"{record.name:<18} ", style="dim cyan")
                line.append(str(record.msg), style="dim white")
                
            self.buffer.append(line)
            if len(self.buffer) > self.max_size:
                self.buffer.pop(0)
        except Exception:
            pass

class CourtroomDashboard:
    """Aesthetic TUI layout container."""
    def __init__(self, repo: str):
        self.repo = repo
        self.logs: List[Text] = []
        self.layout = Layout()
        self.start_time = datetime.now()
        self.status = "INITIALIZING"
        self.node = "Idle"
        self.error_count = 0
        
        self.layout.split_column(
            Layout(name="header", size=7),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="log_pane", ratio=3),
            Layout(name="stats_pane", ratio=1)
        )

    def make_header(self) -> Panel:
        banner = """
        █▀▄ █ █▀▀ █ ▀█▀ ▄▀█ █   █▀▀ █▀█ █ █ █▀█ ▀█▀ █▀█ █▀█ █▀█ █▀▄▀█
        █▄▀ █ █▄█ █  █  █▀█ █▄▄ █▄▄ █▄█ █▄█ █▀▄  █  █▄█ █▄█ █▄█ █ ▀ █
        """
        title = Text(banner, style="cyan", justify="center")
        subtitle = Text(f"REPO: {self.repo} | START: {self.start_time.strftime('%H:%M:%S')}", style="italic dim cyan")
        return Panel(Align.center(Group(title, subtitle)), box=box.HORIZONTALS, style="bold blue", padding=(0, 0))

    def make_log_pane(self) -> Panel:
        # Render log buffer as a group
        log_group = Group(*self.logs) if self.logs else Text("\n\n   Waiting for judicial proceedings...", style="italic dim")
        return Panel(log_group, title="[bold blue] 📜 JUDICIAL PROCEEDINGS [/bold blue]", title_align="left", border_style="blue", padding=(1, 2))

    def make_stats_pane(self) -> Panel:
        table = Table(box=box.SIMPLE, expand=True)
        table.add_column("Property", style="dim cyan")
        table.add_column("Value")
        elapsed = str(datetime.now() - self.start_time).split(".")[0]
        status_style = "bold green" if self.status == "RUNNING" else "bold yellow" if "FAILED" in self.status else "bold blue"
        
        table.add_row("System Status", f"[{status_style}]{self.status}[/]")
        table.add_row("Current Node", f"[bold magenta]{self.node}[/]")
        table.add_row("Errors Found", f"[bold red]{self.error_count}[/]")
        table.add_row("Elapsed Time", f"[white]{elapsed}[/]")
        
        return Panel(Align.center(table), title="[bold blue] 📊 SWARM VITALS [/bold blue]", border_style="blue")

    def make_footer(self) -> Panel:
        return Panel(Align.center(Text("Press [Ctrl+C] to abort the audit Swarm • Secure Session ACTIVE", style="dim italic")), box=box.SIMPLE)

    def update(self):
        self.layout["header"].update(self.make_header())
        self.layout["log_pane"].update(self.make_log_pane())
        self.layout["stats_pane"].update(self.make_stats_pane())
        self.layout["footer"].update(self.make_footer())

async def execute_swarm_with_ui(repo_url: str, pdf_path: str, rubric_path: str, dashboard_ui: CourtroomDashboard):
    """Executes the swarm while aggressively intercepting all loggers."""
    correlation_id = str(uuid.uuid4())
    dashboard_ui.status = "RUNNING"
    
    # Aggressive Log Interception
    log_handler = LogBufferHandler(dashboard_ui.logs)
    
    # Force propagation and capture on EVERY existing logger
    original_config = {}
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        original_config[name] = (logger.propagate, logger.handlers[:])
        logger.propagate = True
        logger.handlers.clear()
        
    # Also capture the root logger
    logging.root.handlers.clear()
    logging.root.addHandler(log_handler)
    logging.root.setLevel(logging.INFO)

    initial_state = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_path": rubric_path,
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

    try:
        config = {"configurable": {"thread_id": correlation_id}}
        
        # We also need to listen to terminal logs being printed by other tools
        # But for now, we focus on LangGraph events
        async for event in courtroom_swarm.astream(initial_state, config=config):
            for node_name, state in event.items():
                dashboard_ui.node = node_name.replace("_", " ").title()
                dashboard_ui.error_count = len(state.get("errors", []))
                dashboard_ui.update()
                
        dashboard_ui.status = "COMPLETED"
        dashboard_ui.node = "Final Report"
        return True
    except Exception as e:
        dashboard_ui.status = "CRITICAL FAIL"
        logging.error(f"Catastrophic failure: {e}")
        raise e
    finally:
        # Restoration
        logging.root.removeHandler(log_handler)
        for name, (prop, handlers) in original_config.items():
            lgr = logging.getLogger(name)
            lgr.propagate = prop
            lgr.handlers = handlers

async def run_audit(args):
    """Subcommand: audit run"""
    # Pre-flight check before opening the Live screen
    if not Path(args.spec).exists():
        console.print(f"[bold red]Error:[/bold red] Specification PDF not found at {args.spec}")
        sys.exit(1)
    if not Path(args.rubric).exists():
        console.print(f"[bold red]Error:[/bold red] Rubric JSON not found at {args.rubric}")
        sys.exit(1)

    dashboard_ui = CourtroomDashboard(args.repo)
    
    with Live(dashboard_ui.layout, refresh_per_second=10, screen=True) as live:
        try:
            # Time update task
            async def ticker():
                while dashboard_ui.status == "RUNNING":
                    dashboard_ui.update()
                    await asyncio.sleep(1)
            
            ticker_task = asyncio.create_task(ticker())
            
            await execute_swarm_with_ui(
                repo_url=args.repo,
                pdf_path=args.spec,
                rubric_path=args.rubric,
                dashboard_ui=dashboard_ui
            )
            
            dashboard_ui.update()
            await asyncio.sleep(3)
            ticker_task.cancel()
            
        except KeyboardInterrupt:
            live.stop()
            sys.exit(130)
        except Exception as e:
            live.stop()
            console.print(f"\n[bold red]Catastrophic Failure:[/bold red] {e}")
            sys.exit(3)

def show_config(args):
    """Subcommand: config"""
    table = Table(title="Digital Courtroom Configuration", box=box.ROUNDED)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Vault Key Present", "✅ Yes" if hardened_config.vault_key else "❌ No")
    table.add_row("Models", str(len(hardened_config.models)) if hardened_config.models else "Defaults")
    console.print(Panel(table, expand=False, border_style="blue"))

def main():
    parser = argparse.ArgumentParser(description="Digital Courtroom Production CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    audit_parser = subparsers.add_parser("audit", help="Run a courtroom audit")
    audit_parser.add_argument("--repo", required=True)
    audit_parser.add_argument("--spec", required=True)
    audit_parser.add_argument("--rubric", default="rubric/week2_rubric.json")
    audit_parser.add_argument("--dashboard", action="store_true")
    subparsers.add_parser("config", help="Show active configuration")
    args = parser.parse_args()

    if args.command == "audit":
        asyncio.run(run_audit(args))
    elif args.command == "config":
        show_config(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()




