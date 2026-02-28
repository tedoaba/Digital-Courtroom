<p align="center">
  <div align="center" style="background-image: url('assets/banner.png'); background-size: cover; padding: 40px; border-radius: 10px;">
    <h1 style="color: #1E90FF; font-size: 3em; margin-bottom: 0;">DIGITAL COURTROOM</h1>
    <h3 style="color: #64B5F6; margin-top: 5px;">Autonomous Auditor with LangGraph</h3>
  </div>
</p>

<p align="center">
  <strong>Transforming Software Governance through Adversarial Multi-Agent Swarms</strong>
</p>

In a world where AI-generated code outpaces human review capacity, the bottleneck of software delivery shifts from **generation** to **governance**. The **Automaton Auditor** is a production-grade, hierarchical multi-agent system built on **LangGraph** designed to automate the rigorous process of architectural review and code auditing.

## 🏛️ The Digital Courtroom Philosophy

Instead of relying on a single, monolithic LLM prompt prone to hallucinations and "vibe-based" grading, this system treats code validation as a formal legal proceeding. It operates on the **Dialectical Model (Thesis-Antithesis-Synthesis)**:

1.  **Forensic Analysis (The Detectives):** Objectively verifying the existence and structure of code artifacts. No opinions allowed.
2.  **Nuanced Judgment (The Judges):** Applying complex, persona-driven rubrics to interpret the evidence from conflicting viewpoints.
3.  **Deterministic Verdict (The Supreme Court):** A purely Pythonic rule-engine that synthesizes a final ruling based on the "Rule of Law"—not the "Vibe of the Model."

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

## 🛡️ Production Hardening (Operation Ironclad Swarm)

The system is built for production-grade reliability and forensic rigor through the following hardening features:

- **🔒 Hardened Vault**: All sensitive credentials (API keys, repo tokens) are stored in an **AES-256 encrypted vault** (Fernet).
- **📦 Isolated Sandbox**: Detectives execute all Git and file operations within a resource-constrained `SandboxEnvironment`. It enforces strict limits (**512MB RAM, 1 CPU core**) and uses a cross-platform watchdog to prevent tool escapes.
- **🧬 Evidence Hashing**: Every piece of evidence is cryptographically linked in a **sequential SHA-256 hash chain**, ensuring the final report is verifiable and tamper-proof.
- **🔌 Circuit Breakers**: Built-in **Circuit Breaker** patterns (3-failure threshold, 30s reset) protect against external API outages.
- **⚖️ Redundant Judges**: Implements a **Leader Election** pattern for judicial nodes to handle rate limits or regional outages seamlessly.
- **📊 Live TUI Dashboard**: Real-time terminal monitoring of graph execution, node health, and judicial consensus metrics.

## 🚀 Getting Started

### **Prerequisites**

- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (Fast Python Package Manager)
- API Keys for OpenAI/Gemini and a [LangSmith](https://smith.langchain.com/) account for tracing.

### **Installation**

Clone the repository and install dependencies using `uv`:

```bash
git clone https://github.com/tedoaba/Digital-Courtroom.git
cd Digital-Courtroom
uv sync
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Generate a **Vault Key** for AES-256 encryption:

```bash
# Generate a key and add it to your .env as COURTROOM_VAULT_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### **Running the Auditor**

#### 1. Standard Execution

Run a full audit with default settings:

```bash
uv run python -m src.main --repo <REPO_URL> --spec <PDF_PATH>
```

#### 2. With Real-time Dashboard (Recommended)

Enable the high-fidelity TUI (Terminal User Interface) to visualize the swarm in action:

```bash
uv run python -m src.cli audit --repo <REPO_URL> --spec <PDF_PATH>
```

#### 3. Advanced Configuration

Customize the scoring rubric or view the active system configuration:

```bash
# Run with a custom rubric
uv run python -m src.cli audit \
  --repo https://github.com/user/project \
  --spec specs/feature-v1.pdf \
  --rubric rubric/strict_rubric.json \
  --dashboard

# View hardened configuration status
uv run python -m src.cli config
```

## 📂 Folder Structure

```text
Digital-Courtroom/
├── src/
│   ├── nodes/              # LangGraph node definitions (Orchestrators)
│   ├── judicial/           # Judicial Layer (Strategies & Rubrics)
│   ├── utils/              # Security (Vault, Sandbox), Observability, Resilience
│   ├── config.py           # Pydantic HardenedConfig
│   └── state.py            # EvidenceChain & CircuitBreakerState models
├── specs/                  # Feature branch specifications and tasks
├── rubric/                 # Scoring constitution and qualitative rubrics
├── audit/                  # Generated reports and sequential JSON traces
└── tests/                  # Unit, Integration, and Chaos testing suites
```

## 📈 Observability & Forensics

Every execution is a "Forensic Event." You can audit the results through:

1.  **LangSmith**: Deep-dive into every node's `state_diff` and model prompt/response.
2.  **TUI Dashboard**: Live performance metrics and node status tracking.
3.  **Audit Trail**: A `run_audit_trail.json` is generated for every run, containing the full sequential hash chain of evidence.

> _"Building an evaluator is harder than building a generator. It requires Metacognition: the ability to think about thinking."_
