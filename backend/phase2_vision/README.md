<div align="center">
  <img src="https://img.shields.io/badge/PyTorch-Vision_Transformer-red?style=for-the-badge&logo=pytorch" />
  <img src="https://img.shields.io/badge/HuggingFace-ViT-yellow?style=for-the-badge&logo=huggingface" />
  <h2>Phase 2: Multi-Modal Vision Triage</h2>
</div>

## 📖 Overview
Hackers easily bypass traditional signature-based detection by recompiling their malware to change the hash (polymorphic viruses). Phase 2 defeats this using **Multi-Modal AI**.

By converting raw binary code into 2D Grayscale Images (BytePlots), we can train a **Vision Transformer (ViT)** to literally "look" at the malware and identify it based on its visual texture.

## ⚙️ How It Works
1. **Binary-to-Image**: The raw hex code of the payload is wrapped into a 2D matrix (e.g., 256x256 pixels) using the Python Imaging Library (Pillow).
2. **Patch Embeddings**: The image is sliced into 16x16 patches.
3. **Transformer Attention**: The `google/vit-base-patch16-224` PyTorch model analyzes the patches using Self-Attention to classify the specific Malware Family (e.g., `Gatak`, `Allaple.L`).

## 🧪 Testing Locally
You can test the Vision model independently:
```bash
python server.py
```
This will start a FastAPI endpoint at `http://localhost:8002/api/vision/predict`. It expects a raw binary payload or a base64 encoded string.
