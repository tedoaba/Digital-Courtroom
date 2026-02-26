# Research: Operation Ironclad Swarm — Production-Grade Hardening

## Overview

This research resolves implementation choices for the production hardening of the Digital Courtroom.

---

### Decision: AES-256 Encryption for Secret Storage

- **Decision**: Use the `cryptography.fernet` module for AES-256 (CBC mode + HMAC).
- **Rationale**: Fernet provides high-level "recipes" for symmetric encryption that include authentication (HMAC) and are resistant to common cryptographic pitfalls (like IV reuse).
- **Key Management**: A 32-byte master key (`COURTROOM_VAULT_KEY`) will be stored in `.env`.
- **Alternatives Considered**:
  - `pycryptodome`: Provides low-level primitives but requires manual management of IVs and authentication tags (GCM/CCM), increasing the surface for errors.

---

### Decision: Resource Constrained Sandboxing (Windows/Cross-Platform)

- **Decision**: For Windows, use `psutil` to monitor and `subprocess.Popen` with Job Objects (if possible) or polling; for cross-platform robustness, use `resource` (Unix) and polling monitor threads (Windows).
- **Implementation**: The `SandboxEnvironment` will wrapper `subprocess.run` and use a secondary thread to kill processes that exceed 512MB RAM or 60s runtime. Fixed CPU affinity or `psutil.Process.cpu_percent()` will be used to track CPU usage.
- **Rationale**: Direct CPU/RAM enforcement for subprocesses on Windows is complex without third-party Docker/Sandboxie wrappers. Polling with `psutil` is the most portable approach for this stage.
- **Alternatives Considered**:
  - Docker: Perfect isolation but introduces heavy infrastructure dependencies.
  - `resource` module: Only works on Unix-like systems.

---

### Decision: Circuit Breaker Pattern for API Resilience

- **Decision**: Custom implementation integrated directly into the `orchestration.py` utility.
- **Rationale**: A custom stateful object (`CircuitBreaker`) that tracks failures and timestamps is light and easily serialized into the LangGraph `AgentState`.
- **Policy**:
  - Status: Closed (Normal), Open (Short-circuit), Half-Open (Recovery).
  - Transition: 3 consecutive failures → Open (30s timeout).
- **Alternatives Considered**:
  - `pybreaker`: Feature-rich but harder to integrate with LangGraph's state serialization requirements.

---

### Decision: Real-time TUI Dashboard with `Rich`

- **Decision**: Use `rich.live.Live` with a `Table` or `Panel` layout.
- **Rationale**: `rich.live` allows for flicker-free updating of the console at a set frequency (1s).
- **Data Source**: The TUI will consume a queue or shared state object updated by LangGraph node listeners (`on_node_start`, `on_node_end`).
- **Alternatives Considered**:
  - `Textual`: Full-blown TUI framework; excellent but potentially overkill for a status dashboard.

---

### Decision: Sequential SHA-256 Hash Chain

- **Decision**: The `state.py` will include a `evidence_chain_hash` field.
- **Mechanism**:
  - `new_hash = SHA-256(previous_hash + current_evidence_data)`
  - The first hash (Genesis) is derived from the `run_manifest.json`.
- **Rationale**: Provides a verifiable sequence of data production, where tampering with any piece of evidence invalidates all subsequent hashes.
- **Alternatives Considered**:
  - Merkle Tree: Efficient for partial verification but over-engineered for a simple sequential forensic report.

---

### Decision: Judicial Layer Abstraction

- **Decision**: Strategy Pattern using a base class `BaseReasoningStrategy`.
- **Rationale**: Allows judges to swap between "Socratic," "Critical," or "Pragmatic" reasoning without changing the node logic in `judicial_nodes.py`.
- **Scoring**: Rubrics are defined in YAML/JSON and loaded into the strategy for deterministic evaluation.
