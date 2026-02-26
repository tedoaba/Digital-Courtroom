# ⚖️ Digital Courtroom: The Automaton Auditor

> **Transforming Software Governance through Adversarial Multi-Agent Swarms**

In a world where AI-generated code outpaces human review capacity, the bottleneck of software delivery shifts from **generation** to **governance**. The **Automaton Auditor** is a production-grade, hierarchical multi-agent system built on **LangGraph** designed to automate the rigorous process of architectural review and code auditing.

---

## 🏛️ The Digital Courtroom Philosophy

Instead of relying on a single, monolithic LLM prompt prone to hallucinations and "vibe-based" grading, this system treats code validation as a formal legal proceeding. It operates on the **Dialectical Model (Thesis-Antithesis-Synthesis)**:

1.  **Forensic Analysis (The Detectives):** Objectively verifying the existence and structure of code artifacts. No opinions allowed.
2.  **Nuanced Judgment (The Judges):** Applying complex, persona-driven rubrics to interpret the evidence from conflicting viewpoints.
3.  **Deterministic Verdict (The Supreme Court):** A purely Pythonic rule-engine that synthesizes a final ruling based on the "Rule of Law"—not the "Vibe of the Model."

---

## 🏗️ Architecture Overview

The system executes through a strictly layered **StateGraph** architecture, ensuring deterministic synchronization and parallel throughput.

### **Layer 1: The Detective Layer (Parallel Fan-Out)**

Specialized agents collect raw evidence based on strict forensic protocols.

- **🔍 RepoInvestigator:** Uses AST parsing and Git forensic analysis to verify state rigor and graph wiring.
- **📄 DocAnalyst:** Cross-references technical documentation against repository reality to detect "Concept Hallucinations."
- **👁️ VisionInspector:** Analyzes architectural diagrams via multi-modal LLMs to verify structural integrity.

### **Layer 2: The Judicial Layer (The Dialectical Bench)**

Three independent personas analyze the **same evidence** for every rubric criterion:

- **⚖️ The Prosecutor (Critical):** Hunts for gaps, security flaws, and technical debt.
- **🛡️ The Defense (Optimistic):** Highlights creative intent, engineering struggle, and "Spirit of the Law."
- **🛠️ The Tech Lead (Pragmatic):** Focuses on maintainability, scalability, and functional viability.

### **Layer 3: The Supreme Court (Deterministic Synthesis)**

The **Chief Justice** node resolves conflicts using hardcoded Python rules:

- **Security Supremacy:** Confirmed vulnerabilities cap scores regardless of effort.
- **Fact Supremacy:** Forensic evidence always overrules judicial opinion.
- **Variance Re-evaluation:** High disagreement among judges triggers an automated re-audit.

---

## 🛡️ Production Hardening (Operation Ironclad Swarm)

The system is built for production environments with the following hardening features:

- **🔒 Hardened Vault:** All sensitive credentials (API keys, repository tokens) are stored in an AES-256 encrypted vault.
- **📦 Isolated Sandbox:** Detectives execute all Git and file operations within a resource-constrained `SandboxEnvironment` (512MB RAM, 1 CPU core) to prevent resource exhaustion and tool escapes.
- **🧬 Evidence Hashing:** Every piece of evidence is cryptographically linked in a SHA-256 hash chain to ensure forensic integrity.
- **🔌 Circuit Breakers:** Automatic "Circuit Breaker" patterns protect against API failures and cascading outages.
- **📊 Live TUI Dashboard:** Real-time terminal monitoring of graph execution, node health, and circuit breaker states.

---

## 🚀 Getting Started

### **Prerequisites**

- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (Fast Python Package Manager)
- API Keys for OpenAI, Google Gemini, and LangSmith.

### **Installation**

Clone the repository and install dependencies using `uv`:

```bash
git clone https://github.com/tedoaba/Digital-Courtroom.git
cd Digital-Courtroom
uv sync
```

### **Environment Setup**

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Configure your API keys and the mandatory **Vault Key**:

```bash
# Generate a vault key
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
COURTROOM_VAULT_KEY=your-base64-key-here
```

### **Basic Usage**

Run the auditor against any GitHub repository and specification PDF:

```bash
uv run python -m src.main \
  --repo https://github.com/target/repo-to-audit \
  --spec docs/design-spec.pdf \
  --dashboard
```

---

## Folder Structure

```text
Digital-Courtroom/
├── src/
│   ├── nodes/              # LangGraph node definitions
│   ├── judicial/           # Abstraction layer for reasoning & strategies
│   ├── utils/              # Security, Observability, and Orchestration
│   ├── state.py            # Pydantic models & AgentState
│   └── graph.py            # StateGraph compilation
├── rubric/                 # The "Constitution"
├── audit/                  # Generated reports and JSON traces
├── tests/                  # 100% Coverage Unit & Integration tests
└── pyproject.toml          # uv managed dependencies
```

---

## 📈 Observability

Monitor the swarm's reasoning in real-time via the **TUI Dashboard** or **LangSmith**. Every run produces a `run_audit_trail.json` providing structured traceability of every node execution and state transition.

---

> _"Building an evaluator is harder than building a generator. It requires Metacognition: the ability to think about thinking."_
