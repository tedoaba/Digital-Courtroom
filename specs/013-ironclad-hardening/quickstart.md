# Quickstart: Production-Grade Hardening (Ironclad Swarm)

## Prerequisites

1.  **Environment Setup**:
    - Copy `.env.example` to `.env`.
    - Generate a 32-byte master key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
    - Set `COURTROOM_VAULT_KEY` in `.env`.
2.  **Dependencies**:
    - Run `uv sync` to install dependencies (including `cryptography`, `rich`, and `psutil`).

## Using the Hardened Vault

Store sensitive API keys using the provided utility:

```python
from src.utils.security import HardenedVault

vault = HardenedVault()
vault.set_secret("GIT_FORENSIC_TOKEN", "your-sensitive-token")
```

## Running the Hardened Swarm

Launch the swarm with the real-time TUI dashboard:

```bash
uv run python -m src.main --dashboard --url <repo-url> --pdf <rubric-path>
```

## Monitoring Health

- **Live TUI**: Monitor real-time node status, memory usage of sandboxes, and circuit breaker health.
- **LangSmith**: All execution traces are automatically pushed to your LangSmith project for deep forensic audit.
- **Integrity**: Verifying a report integrity chain:

```bash
uv run python -m src.utils.security --verify <report-hash-chain.json>
```

## Resilience Features

- **Circuit Breakers**: If an external API (like GitHub or OpenAI) fails 3 times, the system will pause that branch for 30s to prevent credit exhaustion or cascading errors.
- **Sandboxing**: Detectives are automatically restricted to 512MB RAM. If exceeded, the tool call is terminated safely and logged.
