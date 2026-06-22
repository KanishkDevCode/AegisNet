import os
import math
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File
import json
import io

app = FastAPI(title="AegisNet Phase 2: Vision Triage (ViT Inference)")

# Global variables
model = None
label_mapping = {}
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Transformation expected by ViT
vit_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def get_dynamic_width(file_size_bytes):
    size_kb = file_size_bytes / 1024.0
    if size_kb < 10: return 32
    elif size_kb < 30: return 64
    elif size_kb < 60: return 128
    elif size_kb < 100: return 256
    elif size_kb < 200: return 384
    elif size_kb < 500: return 512
    elif size_kb < 1000: return 768
    else: return 1024

def bytes_to_image(content: bytes):
    """
    Converts raw bytes to a PIL Image using dynamic width logic.
    """
    file_size = len(content)
    width = get_dynamic_width(file_size)
    
    array_1d = np.frombuffer(content, dtype=np.uint8)
    height = int(math.ceil(len(array_1d) / width))
    
    pad_len = (width * height) - len(array_1d)
    if pad_len > 0:
        array_1d = np.pad(array_1d, (0, pad_len), 'constant', constant_values=0)
        
    array_2d = np.reshape(array_1d, (height, width))
    img = Image.fromarray(array_2d, mode='L').convert('RGB') # Convert Grayscale to RGB for ViT
    return img

@app.on_event("startup")
async def load_model():
    global model, label_mapping
    model_path = "outputs/vit_aegisnet_phase2.pt"
    mapping_path = "outputs/vit_label_mapping.json"
    
    if os.path.exists(model_path) and os.path.exists(mapping_path):
        print("Loading ViT model and label mapping...")
        
        with open(mapping_path, "r") as f:
            label_mapping = json.load(f)
            
        # Initialize architecture
        model = models.vit_b_16(weights=None)
        model.heads.head = nn.Linear(model.heads.head.in_features, len(label_mapping))
        
        # Load weights
        model.load_state_dict(torch.load(model_path, map_location=device))
        model = model.to(device)
        model.eval()
        
        print(f"ViT model loaded on {device}!")
    else:
        print(f"WARNING: {model_path} or {mapping_path} not found.")

@app.post("/api/v1/analyze_binary")
async def analyze_binary(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="ViT Model not loaded.")
        
    try:
        content = await file.read()
        
        # 1. Byte-to-Image Conversion
        img = bytes_to_image(content)
        
        # 2. PyTorch Transformations
        img_tensor = vit_transform(img).unsqueeze(0).to(device)
        
        # 3. Inference
        with torch.no_grad():
            outputs = model(img_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
        # 4. Result Parsing
        confidence, predicted_idx = torch.max(probabilities, 0)
        confidence = float(confidence.item())
        predicted_class = label_mapping.get(str(predicted_idx.item()), "UNKNOWN")
        
        return {
            "filename": file.filename,
            "vision_classification": predicted_class,
            "confidence": confidence,
            "threat_detected": True # Since only suspicious files reach Phase 2
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) # Port 8001 to not conflict with Phase 1
