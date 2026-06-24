<div align="center">
  <img src="https://img.shields.io/badge/Neo4j-AuraDB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-Llama_3.1-black?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/Phase-3_GraphRAG-yellow?style=for-the-badge" />
  <h2>🕸️ Phase 3: Spatial GraphRAG & LLM Assessment</h2>
</div>

> **The Brain of AegisNet.** Detecting the malware is not enough; the SOC must understand the **blast radius**. Phase 3 maps the corporate network topology and queries a local LLM to assess the lateral movement risk.

## 🌊 Pipeline Flow

```mermaid
graph TD
    classDef default fill:#1e1e2e,stroke:#f9e2af,stroke-width:2px,color:#cdd6f4;
    classDef highlight fill:#a6e3a1,stroke:#11111b,color:#11111b,font-weight:bold;

    A[🔍 Phase 2 Classification] -->|Threat Data| B[(🕸️ Neo4j AuraDB)];
    B -->|Cypher Query| C{Graph Retrieval};
    
    C -->|Network Topology & CVEs| D[🧠 Ollama Llama 3.1];
    D --> E[📝 Lateral Movement Risk Assessment];

    E :::highlight

    E -->|Natural Language Context| F[🛡️ Phase 4 DRL Agent];
```

## ⚙️ How It Works

1. 🕸️ **GraphRAG**: The system connects to a **Neo4j AuraDB** cloud database containing the entire enterprise network topology (DMZ, Internal, Database servers) and mapped MITRE ATT&CK CVE vulnerabilities.
2. 🔍 **Context Retrieval**: Using advanced Cypher queries, Phase 3 pulls all connected systems attached to the originally infected node.
3. 🧠 **Local LLM**: The massive graph context is passed to a fully local **Ollama `llama3.1:8b`** Large Language Model via `langchain-ollama`.
4. 📝 **Threat Assessment**: The LLM dynamically drafts an enterprise-grade incident summary and determines the immediate lateral movement risk (High, Medium, Low).

## 🔑 Setup

You must have Ollama installed and the model downloaded before running this phase:
```bash
ollama run llama3.1:8b
```
Ensure your `.env` file contains your Neo4j credentials so the Cypher queries can map the topology successfully.
