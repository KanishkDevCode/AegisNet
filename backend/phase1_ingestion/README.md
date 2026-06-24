<div align="center">
  <img src="https://img.shields.io/badge/CatBoost-Machine_Learning-FFE042?style=for-the-badge&logo=catboost&logoColor=black" />
  <img src="https://img.shields.io/badge/Polars-Data_Processing-111111?style=for-the-badge&logo=polars" />
  <img src="https://img.shields.io/badge/Phase-1_Sensor-blue?style=for-the-badge" />
  <h2>🌩️ Phase 1: Ingestion & Statistical Triage</h2>
</div>

> **AegisNet's primary tripwire.** This phase intercepts raw network packets and performs sub-millisecond triage to detect statistical anomalies associated with malware.

## 🌊 Pipeline Flow

```mermaid
graph TD
    classDef default fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef anomaly fill:#f38ba8,stroke:#11111b,color:#11111b,font-weight:bold;
    classDef safe fill:#a6e3a1,stroke:#11111b,color:#11111b;

    A[🌐 Raw Network Traffic] -->|TCP/UDP Packets| B(🧹 Polars Feature Extraction);
    B -->|Strip IPs & Timestamps| C{⚡ CatBoost Classifier};
    
    C -->|Probability < 85%| D[🟢 Normal Traffic];
    C -->|Probability > 85%| E[🔴 Anomaly Detected];

    D :::safe
    E :::anomaly

    E -->|Forward to Phase 2| F[👁️ Vision Transformer];
```

## ⚙️ How It Works

1. 🏎️ **Ultra-Fast Ingestion**: Instead of slow Pandas dataframes, Phase 1 uses **Polars** for multi-threaded Rust-based data ingestion.
2. 🧹 **Feature Engineering**: Irrelevant features (Source IP, Destination IP, Timestamps) are stripped out to prevent the model from overfitting.
3. 🧠 **Statistical Inference**: The `CatBoostClassifier` analyzes packet lengths, inter-arrival times, and TCP flags.
4. 🚀 **Thresholding**: If the probability of an attack is `>85%`, the payload is instantly forwarded to Phase 2 for deeper Vision Transformer analysis.

## 🧪 Testing Locally

You can test the Phase 1 sensor independently:
```bash
python server.py
```
This will start a FastAPI endpoint at `http://localhost:8001/api/ingest`. Send a JSON payload matching the expected features to see the CatBoost prediction.
