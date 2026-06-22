<div align="center">
  <img src="https://img.shields.io/badge/Neo4j-AuraDB-blue?style=for-the-badge&logo=neo4j" />
  <img src="https://img.shields.io/badge/Ollama-Llama_3.1-black?style=for-the-badge&logo=meta" />
  <h2>Phase 3: Spatial GraphRAG & LLM Assessment</h2>
</div>

## 📖 Overview
Detecting the malware is not enough; the SOC must understand the **blast radius**. Phase 3 acts as the Brain of AegisNet, mapping the corporate network topology and querying a local LLM to assess the lateral movement risk.

## ⚙️ How It Works
1. **GraphRAG**: The system connects to a **Neo4j AuraDB** cloud database containing the entire enterprise network topology (DMZ, Internal, Database servers) and mapped MITRE ATT&CK CVE vulnerabilities.
2. **Context Retrieval**: Using Cypher queries, Phase 3 pulls all connected systems to the originally infected node.
3. **Local LLM**: The massive graph context is passed to a fully local **Ollama `llama3.1:8b`** Large Language Model via `langchain-ollama`.
4. **Threat Assessment**: The LLM dynamically drafts an enterprise-grade incident summary and determines the immediate lateral movement risk (High, Medium, Low).

## 🔑 Setup
You must have Ollama installed and the model downloaded before running this phase:
```bash
ollama run llama3.1:8b
```
And your `.env` file must contain your Neo4j credentials.
