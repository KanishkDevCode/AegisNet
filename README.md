<div align="center">
  <img src="assets/hero_banner.png" alt="AegisNet Hero Banner" width="800" style="border-radius: 12px; margin-bottom: 20px;" />
  <br/><br/>
  <img src="https://img.shields.io/badge/Next.js-React_Flow-black?style=for-the-badge&logo=next.js" />
  <img src="https://img.shields.io/badge/LangGraph-Agentic_Swarm-8A2BE2?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-Llama_3.1-black?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/Stable_Baselines3-PPO_DRL-FF8C00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Neo4j-AuraDB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white" />
  
  <h1>🛡️ AegisNet: Autonomous Agentic Cyber Defense</h1>
  <p><b>An end-to-end, multi-modal cybersecurity orchestration system built with Machine Learning, Vision Transformers, GraphRAG, Deep Reinforcement Learning, and Local LLMs.</b></p>
</div>

<br/>

> **AegisNet** represents the next generation of autonomous network defense. Traditional cybersecurity relies on static rules (YARA signatures, IP blacklists) which fail against zero-day exploits. AegisNet solves this by treating cybersecurity as a **multi-modal AI problem**.

It acts as an autonomous AI Security Operations Center (SOC) that can "feel" network anomalies via gradient boosting, "see" the visual texture of malware binaries, map blast radiuses using Spatial GraphRAG, generate human-readable threat assessments using local Llama 3.1 LLMs, and deploy zero-trust isolation firewalls via Deep Reinforcement Learning.

---

## 🏗️ Master Architecture Flow

```mermaid
graph TD
    classDef frontend fill:#1e1e2e,stroke:#cba6f7,stroke-width:2px,color:#cdd6f4;
    classDef api fill:#1e1e2e,stroke:#89dceb,stroke-width:2px,color:#89dceb,font-weight:bold;
    classDef p1 fill:#1e1e2e,stroke:#f9e2af,stroke-width:2px,color:#f9e2af;
    classDef p2 fill:#1e1e2e,stroke:#f38ba8,stroke-width:2px,color:#f38ba8;
    classDef p3 fill:#1e1e2e,stroke:#a6e3a1,stroke-width:2px,color:#a6e3a1;
    classDef p4 fill:#1e1e2e,stroke:#fab387,stroke-width:2px,color:#fab387;
    classDef p5 fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#89b4fa;
    classDef highlight fill:#f38ba8,stroke:#11111b,color:#11111b,font-weight:bold;

    A[💻 Next.js Frontend UI] <-->|REST API / Webhooks| B{🔌 FastAPI API Gateway}
    
    B -->|Payload Delivery| C[⚡ Phase 1: CatBoost Sensor]
    
    C -->|If >85% Anomaly| D[👁️ Phase 2: Vision Transformer]
    C -->|If Safe| Z[🟢 Ignore Traffic]

    D -->|Confidence Score & Malware Family| E[🕸️ Phase 3: GraphRAG & LLM]
    
    E -->|Retrieve Topology| F[(Neo4j AuraDB)]
    E -->|Assess Lateral Risk| G[🧠 Ollama Llama-3.1 LLM]
    
    G -->|Threat Context| H{⚖️ Phase 4: LangGraph Swarm}
    
    H -->|Confidence < 80%| I[🧑‍💻 Human-In-The-Loop Approval]
    H -->|Confidence >= 80%| J[🤖 DRL Agent]
    
    I --> J
    J -->|AegisBattleSim Gym| K[🛡️ Output Zero-Trust Firewall Rule]
    K -->|Webhook Update| B
    
    B -->|Logs & Latency Data| L[📊 Phase 5: MLOps Metrics Store]
    L -->|Polling| A

    class A frontend;
    class B api;
    class C p1;
    class D p2;
    class E,F,G p3;
    class H,I,J p4;
    class K highlight;
    class L p5;
```

---

## 🚀 The 5 Phases of Defense

### 1️⃣ Phase 1: Ingestion & Triaging (The Senses)
The frontline tripwire. High-speed packet parsing using **Polars** drops irrelevant features to prevent the AI from overfitting. The sanitized data is fed into a highly optimized **CatBoost** Gradient Boosting model trained to detect the statistical signatures of 15 different malware families.
* **Tech Stack**: `FastAPI`, `Polars`, `CatBoost`

### 2️⃣ Phase 2: Multi-Modal Vision Triage (The Analyst)
Traditional signature matching fails when hackers slightly modify their code. AegisNet bypasses this by converting raw binary code into 2D Grayscale Images. A massive **PyTorch Vision Transformer (ViT)** then "looks" at the image to identify the malware based on its visual texture, achieving extremely high accuracy against zero-day mutations.
* **Tech Stack**: `PyTorch`, `Transformers (ViT)`, `FastAPI`, `Pillow`

### 3️⃣ Phase 3: Spatial GraphRAG & Local LLM (The Brain)
Detecting malware isn't enough; the system must understand the blast radius. Phase 3 maps the corporate network topology into a **Neo4j AuraDB** graph database. The system then passes the retrieved graph context to a completely local **Ollama (`llama3.1:8b`)** Large Language Model to dynamically generate an enterprise-grade threat summary and lateral movement risk assessment.
* **Tech Stack**: `Neo4j Aura`, `Cypher`, `LangChain`, `Ollama`

### 4️⃣ Phase 4: Native Active Defense & SOAR (The Shield)
The central intelligence. A **LangGraph** State Machine orchestrates the pipeline. It evaluates the AI confidence against a strict Human-In-The-Loop (HITL) matrix. If approved, it passes the state to a Deep Reinforcement Learning (PPO) agent inside a native **AegisBattleSim** Gymnasium environment. The agent calculates the optimal firewall isolation strategy, and generates a structured JSON SOAR webhook mimicking an enterprise push to Splunk or Elastic Security.
* **Tech Stack**: `LangGraph`, `Stable-Baselines3 (PPO)`, `Gymnasium`, `PyTest`

### 5️⃣ Phase 5: MLOps Dashboard (The Overwatch)
A stunning **Next.js** interactive dashboard that fully decouples the frontend from the backend. Features a real-time `React Flow` network canvas showing live infection spread and isolation, alongside a massive MLOps telemetry suite tracking Vision Model Confidence, Data Drift (Wasserstein Distance), and Phase Inference Latency via `Recharts`.
* **Tech Stack**: `Next.js`, `React Flow`, `Tailwind CSS`, `Recharts`

---

## ⚙️ Setup & Installation (Local Execution)

AegisNet has been engineered to run **100% locally** on a Windows/Linux machine without requiring Docker containers, leveraging native Python environments.

### Prerequisites
* Python 3.10+
* Node.js & npm
* [Ollama](https://ollama.com/) (installed with `llama3.1:8b` model pulled)
* A free [Neo4j AuraDB](https://neo4j.com/cloud/aura/) account.

### 1. Configure Graph Database
Navigate to `backend/phase3_graph` and create a `.env` file with your live Neo4j credentials:
```env
NEO4J_URI=neo4j+s://<YOUR_INSTANCE>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password
```

### 2. Backend Setup
Initialize the Python environment and start the FastAPI Gateway. This gateway centrally manages all 5 phases.
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api_gateway.main:app --reload --port 8000
```

### 3. Frontend Setup
In a separate terminal, install the UI dependencies and start the Next.js server.
```bash
cd frontend
npm install
npm run dev
```

---

## 🎮 Running the Simulation

1. Open your browser to `http://localhost:3000`.
2. Ensure **Ollama** is running in the background.
3. Select an attack vector from the Control Panel and click the **"Launch Attack"** button.
4. Watch the terminal output in the UI as the LangGraph State Machine triggers the CatBoost model, the Vision Transformer, the Neo4j query, the Llama-3 summary, and the DRL firewall isolation.
5. If the AI is uncertain, a gorgeous **Human-In-The-Loop (HITL)** modal will pop up demanding your approval.
6. Once contained, an **After-Action Report** overlay will slide in detailing exactly what happened.
7. Switch to the **MLOps Tab** to view the live Recharts telemetry, latency profiling, and data drift tracking.

---

> **Note:** To audit the LangGraph state machine and verify the RL agent's False Positive protections, run the native PyTest suite: `pytest backend/tests/test_swarm.py -v`.
