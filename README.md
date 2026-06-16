<div align="center">
  <h1>🛡️ AegisNet: Autonomous Agentic Cyber Defense</h1>
  <p>An end-to-end, multi-modal cybersecurity orchestration system built with Machine Learning, Vision Transformers, GraphRAG, and Deep Reinforcement Learning.</p>
</div>

<br/>

## 📖 Overview

**AegisNet** represents the next generation of autonomous network defense. Traditional cybersecurity relies on static rules (YARA signatures, IP blacklists) which fail against zero-day exploits. AegisNet solves this by treating cybersecurity as a multi-modal AI problem.

It acts as an autonomous AI Security Operations Center (SOC) that can "feel" network anomalies, "see" the visual texture of malware binaries, map blast radiuses across a corporate network using Spatial GraphRAG, and deploy zero-trust isolation firewalls via Deep Reinforcement Learning.

---

## 🏗️ Architecture: The 5 Phases of Defense

AegisNet is divided into 5 distinct microservice layers, simulating a real-world enterprise deployment.

### 1️⃣ Phase 1: Ingestion & Triaging (The Senses)
The frontline tripwire. High-speed packet parsing using **Polars** drops irrelevant features (like IPs and Timestamps) to prevent the AI from overfitting. The sanitized data is fed into a highly optimized **CatBoost** Gradient Boosting model trained to detect the statistical signatures of 15 different malware families.
* **Tech Stack**: `FastAPI`, `Polars`, `CatBoost`

### 2️⃣ Phase 2: Multi-Modal Vision Triage (The Analyst)
Traditional signature matching fails when hackers slightly modify their code. AegisNet bypasses this by converting raw binary code into 2D Grayscale Images. A massive **PyTorch Vision Transformer (ViT)** then "looks" at the image to identify the malware based on its visual texture, achieving 92.9% accuracy against zero-day mutations.
* **Tech Stack**: `PyTorch`, `Transformers (ViT)`, `FastAPI`, `Pillow`

### 3️⃣ Phase 3: MITRE ATT&CK Spatial GraphRAG (The Map)
Detecting malware isn't enough; the system must understand the blast radius. Phase 3 maps the entire corporate network topology (DMZ, Internal, Database) into a **Neo4j AuraDB** cloud database. It uses NLP **SentenceTransformers** to convert MITRE ATT&CK vulnerabilities into mathematical vectors, allowing the system to calculate exact lateral movement paths.
* **Tech Stack**: `Neo4j Aura`, `Cypher`, `SentenceTransformers`, `GraphRAG`

### 4️⃣ Phase 4: Active Defense Simulation & Agent Swarm (The Brain)
The central intelligence. A **LangGraph** State Machine orchestrates the entire pipeline. It evaluates the Vision Transformer's confidence score against a strict Human-In-The-Loop (HITL) fallback matrix. If the threat is verified, it wakes up a Deep Reinforcement Learning (PPO) agent—trained via 50,000 simulated attacks in a custom **Gymnasium** environment—to calculate the optimal firewall isolation strategy to protect the network without disrupting business operations.
* **Tech Stack**: `LangGraph`, `Stable-Baselines3 (PPO)`, `Gymnasium`, `Requests`

### 5️⃣ Phase 5: Production MLOps & Tracking Layer (The Optimizer)
AI models are notoriously slow in Python. To allow AegisNet to operate at gigabit line-rate, Phase 5 compiles the massive PyTorch Vision Transformer down into a bare-metal C++ **ONNX Execution Engine**, dropping inference latency down to 15 milliseconds. It also integrates Data Drift monitoring to detect when hackers evolve their tactics.
* **Tech Stack**: `ONNX Runtime`, `Evidently AI`

---

## ⚙️ Setup & Installation

### Prerequisites
* Python 3.10+
* A free [Neo4j AuraDB](https://neo4j.com/cloud/aura/) account.

### 1. Clone the Repository
```bash
git clone https://github.com/KanishkDevCode/AegisNet.git
cd AegisNet
```

### 2. Configure Environment Variables
Navigate to the `phase3_graph` folder and create a `.env` file with your live Neo4j credentials:
```env
NEO4J_URI=neo4j+s://<YOUR_INSTANCE>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password
```

### 3. Install Dependencies
Each phase operates as an independent microservice. Install the requirements for the phases you wish to run:
```bash
pip install -r phase1_ingestion/requirements.txt
pip install -r phase2_vision/requirements.txt
pip install -r phase3_graph/requirements.txt
pip install -r phase4_agent/requirements.txt
pip install -r phase5_mlops/requirements.txt
```

---

## 🚀 Running the End-to-End Orchestrator

To see the LangGraph Swarm orchestrate a real-time defense, you must start the Sensor APIs and then trigger the Swarm.

**Terminal 1 (Start Phase 1 Server):**
```bash
cd phase1_ingestion
python server.py
```

**Terminal 2 (Start Phase 2 Server):**
```bash
cd phase2_vision
python server.py
```

**Terminal 3 (Trigger the Swarm):**
```bash
cd phase4_agent
python swarm.py
```

### Expected Output
The Swarm will ping the live Phase 1 server, forward the payload to Phase 2 for visual classification, log into your live Neo4j database to calculate the blast radius, and finally deploy the Deep Reinforcement Learning agent to isolate the infected subnet!

---

## 🔮 Future Roadmap
* **Kubernetes Orchestration**: Containerize all 5 phases into separate Docker pods managed by K8s for auto-scaling.
* **Live eBPF Packet Sniffing**: Replace the simulated payload inputs with live Kernel-level packet sniffing using eBPF.
* **LLM Incident Reporting**: Attach an open-source LLM (like Llama 3) to the end of Phase 4 to automatically draft human-readable incident reports for the SOC team.
