<div align="center">
  <img src="https://img.shields.io/badge/LangGraph-Agentic_Swarm-purple?style=for-the-badge&logo=openai" />
  <img src="https://img.shields.io/badge/Stable_Baselines3-PPO_DRL-orange?style=for-the-badge" />
  <h2>Phase 4: Active Defense Simulation & SOAR</h2>
</div>

## 📖 Overview
This is the **Central Intelligence** of AegisNet. Phase 4 orchestrates the entire lifecycle of a threat, from detection (Phase 1/2) to assessment (Phase 3) to final containment (Phase 4).

## ⚙️ How It Works
1. **LangGraph State Machine**: A typed state dictionary flows through the nodes.
2. **HITL Matrix**: A Human-In-The-Loop fallback mechanism checks the Vision model's confidence. If confidence is >95%, it auto-approves containment.
3. **AegisBattleSim (Gymnasium)**: Instead of relying on buggy external dependencies (like Microsoft CyberBattleSim), AegisNet uses a **Native Python Gymnasium Environment**. The environment mathematically models lateral infection spread.
4. **Deep Reinforcement Learning**: A pre-trained `PPO` (Proximal Policy Optimization) agent dynamically observes which server is infected and outputs the optimal Zero-Trust Firewall isolation rule.
5. **SOAR Webhooks**: Upon containment, the system generates a structured JSON webhook formatted for enterprise SIEMs like Splunk or Elastic Security.

## 🧪 Testing Locally
Run the full Swarm (make sure Phase 1 and Phase 2 servers are running, or rely on the mock triggers):
```bash
python swarm.py
```
To run the State Machine Audit tests:
```bash
pytest ../tests/test_swarm.py -v
```
