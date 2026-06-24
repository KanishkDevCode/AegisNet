<div align="center">
  <img src="https://img.shields.io/badge/LangGraph-Agentic_Swarm-8A2BE2?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Stable_Baselines3-PPO_DRL-FF8C00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Phase-4_Active_Defense-green?style=for-the-badge" />
  <h2>🛡️ Phase 4: Active Defense Simulation & SOAR</h2>
</div>

> **The Central Intelligence.** Phase 4 orchestrates the entire lifecycle of a threat, from detection (Phase 1/2) to assessment (Phase 3) to final containment (Phase 4).

## 🌊 Pipeline Flow

```mermaid
graph TD
    classDef default fill:#1e1e2e,stroke:#a6e3a1,stroke-width:2px,color:#cdd6f4;
    classDef highlight fill:#89b4fa,stroke:#11111b,color:#11111b,font-weight:bold;
    classDef hitl fill:#fab387,stroke:#11111b,color:#11111b,font-weight:bold;

    A[📡 Swarm Entry] -->|Typed State Dict| B{⚖️ HITL Matrix};
    
    B -->|Confidence < 80%| C[🧑‍💻 Human Approval Required];
    B -->|Confidence >= 80%| D[🤖 Auto-Approval];

    C --> D;
    D --> E(🎮 AegisBattleSim Gymnasium);
    
    E -->|Observe Infection| F[🧠 Deep Reinforcement Learning PPO];
    F -->|Zero-Trust Firewall Policy| G[🔗 SOAR Webhooks];

    class C hitl;
    class G highlight;
```

## ⚙️ How It Works

1. 🧭 **LangGraph State Machine**: A typed state dictionary flows seamlessly through the nodes.
2. ⚖️ **HITL Matrix**: A Human-In-The-Loop fallback mechanism checks the Vision model's confidence. If confidence is `>=80%`, it auto-approves containment; otherwise, it pings the SOC.
3. 🎮 **AegisBattleSim (Gymnasium)**: Instead of relying on buggy external dependencies, AegisNet uses a **Native Python Gymnasium Environment** to mathematically model lateral infection spread.
4. 🧠 **Deep Reinforcement Learning**: A pre-trained `PPO` (Proximal Policy Optimization) agent dynamically observes which server is infected and outputs the optimal Zero-Trust Firewall isolation rule.
5. 🔗 **SOAR Webhooks**: Upon containment, the system generates a structured JSON webhook formatted for enterprise SIEMs like Splunk or Elastic Security.

## 🧪 Testing Locally

Run the full Swarm (make sure Phase 1 and Phase 2 servers are running, or rely on the mock triggers):
```bash
python swarm.py
```
To run the State Machine Audit tests:
```bash
pytest ../tests/test_swarm.py -v
```
