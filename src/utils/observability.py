import json
import os
import threading
import time

from langsmith import traceable
from pydantic import BaseModel, Field
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from src.config import settings
from src.state import StrictModel


class TraceAuditTrail(StrictModel):
    """
    Structured log for LangSmith export.
    (013-ironclad-hardening)
    """

    node_name: str
    node_id: str
    input_state_hash: str
    output_state_hash: str
    tool_calls: list[dict] = Field(default_factory=list)
    latency_ms: float
    state_diff: dict | None = None
    tool_call_payload: dict | None = None


def export_json_trace(trail: TraceAuditTrail):
    """(FR-011, T022) Export trace to structured JSON."""
    os.makedirs("audit", exist_ok=True)
    with open("audit/run_audit_trail.json", "a") as f:
        f.write(json.dumps(trail.model_dump(), default=str) + "\n")


# Re-exporting traceable for convenience
node_traceable = traceable(project_name=settings.langchain_project)


class ObservableDashboardStatus(BaseModel):
    """Internal state for TUI dashboard."""

    active_node: str = "Idle"
    node_health: dict[str, str] = Field(default_factory=dict)
    performance_metrics: dict[str, float] = Field(default_factory=dict)
    last_refresh: float = 0.0
    is_paused: bool = False
    active_circuit_breakers: list[str] = Field(default_factory=list)


class DashboardManager:
    """
    Manages real-time TUI dashboard using rich.
    (FR-006, CHK002)
    """

    def __init__(self):
        self.status = ObservableDashboardStatus()
        self.console = Console()
        self.live: Live | None = None
        self._input_thread: threading.Thread | None = None
        self._running = False

    def generate_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        layout["header"].update(
            Panel(
                "Digital Courtroom — Ironclad Swarm Monitor",
                style="bold white on blue",
            ),
        )

        main_table = Table(box=box.SIMPLE)
        main_table.add_column("Property", style="bold cyan")
        main_table.add_column("Value")
        main_table.add_row("Active Node", self.status.active_node)
        main_table.add_row(
            "Status",
            "PAUSED" if self.status.is_paused else "RUNNING",
            style="bold yellow" if self.status.is_paused else "bold green",
        )
        main_table.add_row(
            "Open Breakers",
            ", ".join(self.status.active_circuit_breakers) or "None",
        )

        layout["main"].update(Panel(main_table, title="Swarm State"))
        layout["footer"].update(
            Panel("[p] Pause | [r] Resume | [c] Reset CB", style="dim italic"),
        )

        return layout

    def start(self):
        self._running = True
        self.live = Live(
            self.generate_layout(),
            console=self.console,
            refresh_per_second=1,
        )
        self.live.start()
        self._input_thread = threading.Thread(target=self._handle_input, daemon=True)
        self._input_thread.start()

    def _handle_input(self):
        while self._running:
            time.sleep(1)

    def update_node(self, node_name: str, status: str = "Active"):
        self.status.active_node = node_name
        self.status.node_health[node_name] = status
        if self.live:
            self.live.update(self.generate_layout())

    def stop(self):
        self._running = False
        if self.live:
            self.live.stop()
