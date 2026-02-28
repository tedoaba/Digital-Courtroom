# Implementation Plan: Operation Ironclad Swarm — Production-Grade Hardening

**Branch**: `013-ironclad-hardening` | **Date**: 2026-02-26 | **Spec**: [spec.md](file:///c:/Users/user/tedoaba/Digital-Courtroom/specs/013-ironclad-hardening/spec.md)
**Input**: Feature specification from `/specs/013-ironclad-hardening/spec.md`

## Summary

This feature transitions the Digital Courtroom from a functional prototype to a production-grade, hardened forensic system. The technical approach involves:

1.  **Zero-Hardcoded Config**: Migrating all configuration to environment variables and a secure local encrypted vault (AES-256).
2.  **Safe Tooling**: Implementing resource-constrained sandboxes (512MB/1CPU) for detectives and a centralized input/output validation gate.
3.  **Observability**: Mandatory LangSmith `@traceable` instrumentation for 100% trace coverage and a real-time CLI/TUI dashboard (1s refresh) using `rich`.
4.  **Integrity & Resilience**: Implementing SHA-256 sequential cryptographic chains for evidence and circuit breaker patterns (3 failures/30s reset) with cascading failure detection for core streams.
5.  **Judicial Abstraction**: Creating a dedicated layer to separate reasoning strategies from graph orchestration.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `langgraph`, `pydantic`, `langsmith`, `rich`, `cryptography`
**Storage**: `.env` for standard config, AES-256 encrypted local store for secrets, SHA-256 hash chains for evidence integrity.
**Testing**: `pytest` for unit and integration tests.
**Target Platform**: Linux/Windows/macOS
**Project Type**: CLI tool with TUI dashboard
**Performance Goals**: <1s dashboard refresh rate, <10s recovery from orchestration crashes, <50ms cryptographic overhead per operation.
**Constraints**: 512MB RAM and 1 CPU core per detective sandbox; 3 consecutive failures threshold for circuit breakers; 1 successful call to close half-open breakers.
**Scale/Scope**: Forensic swarm evaluation for multi-agent governance.

## Constitution Check

_GATE: Passed. Re-checked after Phase 1 design._

| Principle                    | Status | Implementation in this Feature                                                                              |
| ---------------------------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| I. Spec-Driven Development   | PASSED | spec.md is comprehensive and clarified.                                                                     |
| II. Test-Driven Development  | PASSED | Pre-implementation tests planned for AES Vault, Circuit Breaker states, and Sandbox resource killers.       |
| IV. Schema-First Design      | PASSED | `HardenedConfig`, `CircuitBreakerState`, and `EvidenceChain` entities defined in `data-model.md`.           |
| VII. Explicit Error Handling | PASSED | Custom `CircuitBreaker` class in `orchestration.py` manages failure-to-open logic.                          |
| XV. Tool Execution Isolation | PASSED | `SandboxEnvironment` enforced via `psutil` monitoring threads for cross-platform compliance (Windows/Unix). |
| XX. Modular Architecture     | PASSED | New `src/judicial/` package and `src/utils/observability.py` follow modular standards.                      |
| XXII. Structured Logging     | PASSED | LangSmith `@traceable` mandated across all nodes; JSON audit trails for TUI and traces.                     |

## Project Structure

### Documentation (this feature)

```text
specs/013-ironclad-hardening/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── checklists/
│   └── requirements.md  # Spec validation checklist
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
src/
├── utils/
│   ├── security.py      # AES-256 Vault, Sandbox logic, Sanitization
│   ├── orchestration.py # Graph Resilience, Circuit Breakers, Rollback logic
│   └── observability.py # TUI Dashboard, LangSmith instrumentation
├── nodes/
│   ├── judicial_nodes.py # Updated to use judicial layer abstraction
│   └── ...
├── judicial/
│   ├── layer.py         # Judicial layer abstraction
│   ├── strategies.py    # Reasoning strategies
│   └── rubrics.py       # Multi-factorial scoring rubrics
├── config.py            # HardenedConfig implementation
├── state.py             # Cryptographic chain and CircuitBreakerState
└── main.py              # Entry point for the TUI dashboard

tests/
├── unit/
│   ├── test_security.py
│   ├── test_resilience.py
│   └── ...
└── integration/
    ├── test_disaster_recovery.py
    └── test_cryptographic_chain.py
```

**Structure Decision**: Option 1 (Single Project) with modular expansion of `utils/` and a new `judicial/` package to reflect the production-grade separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
