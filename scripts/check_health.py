"""
Swarm Health & Monitoring Dashboard (CLI).
(013-ironclad-hardening)
"""
import sys
import os
import json
import pathlib
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add src to path
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from src.config import judicial_settings, detective_settings, hardened_config

console = Console()

def run_checks():
    console.print(Panel("[bold blue]Digital Courtroom: Swarm Health Dashboard[/bold blue]"))

    # 1. Configuration Audit
    config_table = Table(title="Configuration Audit")
    config_table.add_column("Property", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Status", style="bold")

    # Check Redundancy
    rf = judicial_settings.judicial_redundancy_factor
    config_table.add_row(
        "Judicial Redundancy Factor", 
        str(rf), 
        "[green]PASS[/green]" if rf > 1 else "[yellow]WARN (No redundancy)[/yellow]"
    )

    # Check Batching
    batching = judicial_settings.batching_enabled
    config_table.add_row(
        "Batching Mode", 
        "Enabled" if batching else "Disabled", 
        "[blue]INFO[/blue]"
    )

    # Check Vision Provider
    vision = detective_settings.vision_provider
    config_table.add_row(
        "Vision Provider", 
        vision, 
        "[green]PASS[/green]" if vision == "ollama" else "[blue]INFO (Cloud)[/blue]"
    )

    console.print(config_table)

    # 2. Architectural Consistency (Static Analysis)
    from src.nodes.consistency_guard import analyze_graph_consistency
    analysis = analyze_graph_consistency()
    
    cons_table = Table(title="Architectural consistency (AST Scan)")
    cons_table.add_column("Check", style="cyan")
    cons_table.add_column("Result", style="bold")

    cons_table.add_row("Graph Nodes Count", str(len(analysis.get("nodes", []))))
    cons_table.add_row("Fan-out Detectives", "Verified" if "repo_investigator" in analysis.get("nodes", []) else "FAILED")
    
    status_style = "green" if analysis["status"] == "pass" else "red"
    cons_table.add_row("OVERALL CONSISTENCY", analysis["status"].upper(), style=status_style)

    if analysis["violations"]:
        for v in analysis["violations"]:
            cons_table.add_row(f"[red]Violation[/red]", v)

    console.print(cons_table)

    # 3. Environment Check
    env_table = Table(title="Environment & Security")
    env_table.add_column("Check", style="cyan")
    env_table.add_column("Status", style="bold")

    pre_commit = pathlib.Path(".pre-commit-config.yaml").exists()
    env_table.add_row("Pre-commit Configuration", "[green]FOUND[/green]" if pre_commit else "[red]MISSING[/red]")

    console.print(env_table)

if __name__ == "__main__":
    run_checks()
