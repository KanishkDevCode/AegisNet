# Phase 5: Production MLOps & Tracking Layer

Taking AI out of Jupyter Notebooks and putting it into a live enterprise firewall requires optimization. Phase 5 ensures the models run fast enough to handle gigabit network speeds, and tracks them to ensure they remain accurate.

## 🧠 Core Technologies
- **ONNX (Open Neural Network Exchange)**: Used to compile the heavy PyTorch Python model into a bare-metal C++ execution engine.
- **Evidently AI**: Used to mathematically calculate Data Drift between training datasets and live production traffic.

## ⚙️ Architecture Flow
1. **Speed (ONNX Export)**: The `onnx_exporter.py` strips out the Python overhead of the Vision Transformer, dropping inference latency from seconds down to milliseconds.
2. **Accuracy (Data Drift)**: `drift_monitor.py` calculates the Wasserstein Distance between baseline and current network traffic. If attackers change their tactics (e.g., packet sizes), an alarm is thrown to retrain the models.

## 🚀 Usage
To compile the Phase 2 PyTorch model into a high-speed C++ ONNX engine:
```bash
python onnx_exporter.py
```
