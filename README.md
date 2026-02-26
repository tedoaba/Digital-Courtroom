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

## 🚀 Getting Started

### **Prerequisites**

- [Python 3.11+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (Fast Python Package Manager)
- API Keys for OpenAI, Google Gemini, and LangSmith.

### **Installation**

Clone the repository and install dependencies using `uv`:

```bash
git clone https://github.com/tedoaba/Digital-Courtroom.git
cd Digital-Courtroom
uv venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
uv pip install -e .
```

### **Environment Setup**

Create a `.env` file and configure your API keys and the new **Judicial Performance** settings:

```bash
# API Keys
GEMINI_API_KEY=...
LANGCHAIN_API_KEY=...

# --- Judicial Performance (012-bounded-agent-eval) ---
# Global concurrency limit for LLM requests (1-50)
MAX_CONCURRENT_LLM_CALLS=5

# Retry policy with exponential backoff
RETRY_INITIAL_DELAY=1.0
RETRY_MAX_DELAY=60.0
RETRY_MAX_ATTEMPTS=3

# Per-request timeout for hung calls
LLM_CALL_TIMEOUT=120.0

# Performance: Enable structured evaluation batching
BATCHING_ENABLED=false
```

### **Basic Usage**

Run the auditor against any GitHub repository and specification PDF:

```bash
uv run python -m src.main \
  --repo https://github.com/target/repo-to-audit \
  --spec docs/design-spec.pdf \
  --output audit/results/
```

---

## 🛡️ Engineering Standards & Security

- **Sandboxed Execution:** All repository cloning and analysis occur within transient `tempfile.TemporaryDirectory()` namespaces.
- **No Code Execution:** The system uses **Abstract Syntax Tree (AST)** parsing to analyze code structure, ensuring that untrusted code is never imported or executed.
- **Typed State Management:** Built on **Pydantic V2** to enforce strict schema validation for every agent transition.
- **Full Traceability:** 100% LangSmith tracing coverage for every multi-agent interaction.

---

## 📁 Project Structure

```text
Digital-Courtroom/
├── src/
│   ├── nodes/              # LangGraph node definitions (Detectives, Judges, Justice)
│   ├── tools/              # Forensic tools (Repo, AST, Doc, Vision)
│   ├── state.py            # Pydantic models & AgentState
│   └── graph.py            # StateGraph compilation & wiring
├── rubric/                 # The "Constitution" (JSON-based evaluation rules)
├── audit/                  # Generated results and manifest logs
├── tests/                  # Unit & integration tests
└── pyproject.toml          # uv managed dependencies
```

---

## 📈 Observability

Monitor the swarm's reasoning in real-time via **LangSmith**. Every run produces a `run_manifest.json` that tracks the provenance of every piece of evidence and every judicial opinion, ensuring 100% reproducibility of the final verdict.

---

> _"Building an evaluator is harder than building a generator. It requires Metacognition: the ability to think about thinking."_
