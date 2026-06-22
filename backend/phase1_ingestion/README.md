<div align="center">
  <img src="https://img.shields.io/badge/CatBoost-Machine_Learning-yellow?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Polars-Data_Processing-blue?style=for-the-badge&logo=python" />
  <h2>Phase 1: Ingestion & Statistical Triage</h2>
</div>

## 📖 Overview
Phase 1 acts as the **tripwire** of AegisNet. It is responsible for intercepting raw network packets and performing sub-millisecond triage to detect statistical anomalies associated with malware.

Instead of slow Pandas dataframes, Phase 1 uses **Polars** for multi-threaded Rust-based data ingestion. The parsed payload is then fed into a highly optimized **CatBoost** Gradient Boosting model trained on the CICIDS2017 dataset.

## ⚙️ How It Works
1. **Feature Engineering**: Irrelevant features (Source IP, Destination IP, Timestamps) are stripped out to prevent the model from overfitting.
2. **Statistical Inference**: The `CatBoostClassifier` analyzes packet lengths, inter-arrival times, and TCP flags.
3. **Thresholding**: If the probability of an attack is >85%, the payload is instantly forwarded to Phase 2 for deeper Vision Transformer analysis.

## 🧪 Testing Locally
You can test the Phase 1 sensor independently:
```bash
python server.py
```
This will start a FastAPI endpoint at `http://localhost:8001/api/ingest`. Send a JSON payload matching the expected features to see the CatBoost prediction.
