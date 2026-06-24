<div align="center">
  <img src="https://img.shields.io/badge/PyTorch-Vision_Transformer-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-ViT-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" />
  <img src="https://img.shields.io/badge/Phase-2_Vision-purple?style=for-the-badge" />
  <h2>👁️ Phase 2: Multi-Modal Vision Triage</h2>
</div>

> **Defeating polymorphic viruses.** Hackers easily bypass traditional signature-based detection by recompiling their malware to change the hash. Phase 2 defeats this using **Multi-Modal AI**.

## 🌊 Pipeline Flow

```mermaid
graph TD
    classDef default fill:#1e1e2e,stroke:#cba6f7,stroke-width:2px,color:#cdd6f4;
    classDef highlight fill:#f5c2e7,stroke:#11111b,color:#11111b,font-weight:bold;

    A[🔴 Anomalous Payload from Phase 1] -->|Raw Binary Code| B(🖼️ Binary-to-Image Converter);
    B -->|256x256 Grayscale Image| C{🧩 ViT Patch Embeddings};
    
    C -->|16x16 Image Patches| D[🧠 Transformer Self-Attention];
    D --> E[🔍 Malware Family Classification];

    E :::highlight

    E -->|Confidence Score + Family| F[💬 Phase 3 GraphRAG];
```

## ⚙️ How It Works

1. 🖼️ **Binary-to-Image**: The raw hex code of the payload is wrapped into a 2D matrix (e.g., `256x256` pixels) using the Python Imaging Library (Pillow). This literally lets the AI "look" at the binary texture.
2. 🧩 **Patch Embeddings**: The grayscale image is sliced into `16x16` patches, just like a grid.
3. 🧠 **Transformer Attention**: The `google/vit-base-patch16-224` PyTorch model analyzes the patches using Self-Attention to map visual structural patterns.
4. 🔍 **Classification**: The model classifies the specific Malware Family (e.g., `Gatak`, `Allaple.L`) and assigns a confidence score.

## 🧪 Testing Locally

You can test the Vision model independently:
```bash
python server.py
```
This will start a FastAPI endpoint at `http://localhost:8002/api/vision/predict`. It expects a raw binary payload or a base64 encoded string.
