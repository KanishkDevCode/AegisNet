# Phase 3: MITRE ATT&CK Spatial GraphRAG (The Map)

Detecting malware is not enough; we must understand *where* it is and *what* it can reach. Phase 3 builds a live, searchable map of the entire corporate network.

## 🧠 Core Technologies
- **Neo4j AuraDB**: A cloud-native Graph Database used to map servers, subnets, and vulnerabilities.
- **SentenceTransformers**: Used to convert MITRE ATT&CK textual descriptions into NLP mathematical vectors.
- **GraphRAG**: Combines Graph traversal with Retrieval-Augmented Generation to understand threat context.

## ⚙️ Architecture Flow
1. A virtual corporate network (DMZ, Internal, Database) is built in Neo4j.
2. Servers and known vulnerabilities (CVEs) are mapped as nodes.
3. When Phase 2 identifies a malware family (e.g., `Allaple.L`), this phase uses Cypher queries to calculate exactly which servers are exposed to lateral movement.
4. The blast radius and risk assessment are forwarded to **Phase 4** for action.

## 🚀 Usage
To build the network topology and inject vector embeddings into your Neo4j instance:
```bash
# Ensure your .env file is populated with your Neo4j Aura credentials
python build_graph.py
```
