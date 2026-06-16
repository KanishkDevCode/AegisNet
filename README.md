<div align="center">
  <h1>AegisNet: Autonomous Agentic Cyber Defense</h1>
  <p>An end-to-end, multi-modal cybersecurity orchestration system built with Machine Learning, Vision Transformers, GraphRAG, and Deep Reinforcement Learning.</p>
</div>

## 🛡️ Project Overview

AegisNet represents the next generation of autonomous network defense. Instead of relying on static rules or single-dimensional ML models, AegisNet combines multiple AI modalities to detect, classify, contextualize, and mitigate cyber threats in real-time.

### The 5 Phases of Defense:
1. **[Phase 1: Ingestion & Triaging](./phase1_ingestion)** - High-speed packet parsing with Polars and anomaly detection using a trained CatBoost Machine Learning model.
2. **[Phase 2: Multi-Modal Vision Triage](./phase2_vision)** - Converts malicious binaries into 2D grayscale images and classifies malware families using a PyTorch Vision Transformer (ViT).
3. **[Phase 3: MITRE ATT&CK Spatial GraphRAG](./phase3_graph)** - Maps the corporate network topology in Neo4j AuraDB. Uses NLP SentenceTransformers to calculate lateral movement risk paths based on vulnerabilities.
4. **[Phase 4: Active Defense & Agent Swarm](./phase4_agent)** - A LangGraph State Machine orchestrator that queries all previous phases. Deploys a Deep Reinforcement Learning (PPO) agent to autonomously calculate optimal firewall isolation strategies.
5. **[Phase 5: Production MLOps](./phase5_mlops)** - Compiles the massive PyTorch ViT into a C++ ONNX engine to crush latency down to milliseconds, allowing the AI to operate at line-rate.

## 🚀 How to Run the Orchestrator

The system is designed as a distributed mesh of microservices. To see the full LangGraph swarm execute an end-to-end autonomous defense:

**1. Start the Phase 1 Sensors:**
```bash
cd phase1_ingestion
python server.py
```

**2. Start the Phase 2 Vision Analyst:**
```bash
cd phase2_vision
python server.py
```

**3. Run the LangGraph Swarm Orchestrator:**
```bash
cd phase4_agent
python swarm.py
```

*Note: Phase 3 (Neo4j) requires an AuraDB instance, and credentials must be supplied via a `.env` file in the Phase 3 directory.*
