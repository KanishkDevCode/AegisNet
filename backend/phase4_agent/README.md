# Phase 4: Active Defense Simulation & Agent Swarm (The Brain)

This phase acts as the central intelligence of AegisNet. It orchestrates the entire pipeline and makes autonomous decisions to isolate threats before they can spread.

## 🧠 Core Technologies
- **LangGraph**: A state machine framework used to orchestrate the flow of data between Phase 1, 2, 3, and 4.
- **Gymnasium**: A custom reinforcement learning environment (`AegisBattleSim`) mapping the Neo4j topology.
- **Stable-Baselines3 (PPO)**: Used to train a Deep Reinforcement Learning agent via 50,000 simulated cyber attacks.

## ⚙️ Architecture Flow
1. The **LangGraph Swarm** calls Phase 1. If an anomaly is found, it triggers Phase 2.
2. Phase 2 classifies the malware.
3. Phase 3 maps the blast radius.
4. The **HITL (Human-in-the-Loop) Approval Matrix** evaluates the confidence score. If confidence > 95%, it auto-approves. Otherwise, it halts for human SOC review.
5. If approved, the **DRL Agent** determines the mathematically optimal firewall isolation strategy to contain the infected node without taking down critical infrastructure.

## 🚀 Usage
To run the full end-to-end simulated cyber attack across all phases:
```bash
# Make sure Phase 1 and Phase 2 servers are running in the background!
python swarm.py
```
