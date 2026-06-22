# Phase 2: Multi-Modal Vision Triage (The Analyst)

When Phase 1 detects a threat, it forwards the malicious binary payload to this phase. Traditional signature matching fails against zero-day malware. AegisNet solves this by converting binary code into 2D images and using Computer Vision to identify the malware family based on its visual "texture".

## 🧠 Core Technologies
- **PyTorch**: Used to build and train the Vision Transformer.
- **Vision Transformers (ViT)**: A state-of-the-art attention-based neural network that "looks" at the malware images to classify them (achieved 92.9% accuracy on the Malimg dataset).
- **FastAPI**: Hosts the deep learning model for real-time inference.

## ⚙️ Architecture Flow
1. A raw binary payload (`.bytes` or `.exe`) is intercepted.
2. The binary is converted from a 1D byte array into a 2D Grayscale Image.
3. The image is passed through the Vision Transformer.
4. The ViT classifies the malware family (e.g., `Allaple.L`, `Kelihos_ver1`).
5. The classification is sent to **Phase 3** to calculate lateral movement risk.

## 🚀 Usage
To start the Vision server:
```bash
python server.py
```
To send a dummy binary file to the server for classification:
```bash
python test_client_phase2.py
```
