# Phase 1: Ingestion & Triaging (The Senses)

This phase acts as the frontline tripwire for the AegisNet architecture. It parses raw network traffic at extremely high speeds and uses a machine learning model to detect anomalies.

## 🧠 Core Technologies
- **Polars**: Used for lightning-fast parsing of `.pcap` and `.csv` network logs.
- **CatBoost**: A highly optimized gradient boosting algorithm trained on Kaggle to detect 15 different malware signatures.
- **FastAPI**: Serves the model as a live HTTP endpoint capable of handling thousands of requests per second.

## ⚙️ Architecture Flow
1. Raw Network Traffic (Packets/Netflow) arrives.
2. Polars drops irrelevant features (IPs, Timestamps) to prevent the AI from memorizing specifics.
3. The CatBoost model infers if the packet is `BENIGN` or `ANOMALOUS`.
4. If an anomaly is detected, the payload is forwarded to **Phase 2** for deep visual inspection.

## 🚀 Usage
To start the live anomaly detection server:
```bash
python server.py
```
To test the inference locally:
```bash
python test_client.py
```
