import os
import time
import json
import torch
import torch.nn as nn
from torchvision import models
import onnx
import onnxruntime as ort
import numpy as np

# Setup absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "phase2_vision", "outputs"))
MODEL_PATH = os.path.join(PHASE2_DIR, "vit_aegisnet_phase2.pt")
MAPPING_PATH = os.path.join(PHASE2_DIR, "vit_label_mapping.json")

ONNX_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
ONNX_MODEL_PATH = os.path.join(ONNX_OUTPUT_DIR, "vit_aegisnet_phase2.onnx")
os.makedirs(ONNX_OUTPUT_DIR, exist_ok=True)

def export_to_onnx():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(MAPPING_PATH):
        print(f"[ERROR] Could not find Phase 2 model at {MODEL_PATH}")
        return False
        
    print(f"Loading PyTorch ViT Model from {MODEL_PATH}...")
    
    with open(MAPPING_PATH, "r") as f:
        label_mapping = json.load(f)
        
    # Recreate the PyTorch architecture
    model = models.vit_b_16(weights=None)
    model.heads.head = nn.Linear(model.heads.head.in_features, len(label_mapping))
    
    # Load weights
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    
    # Create a dummy input tensor that matches the input shape (Batch_Size=1, Channels=3, H=224, W=224)
    dummy_input = torch.randn(1, 3, 224, 224, device="cpu")
    
    print(f"Exporting PyTorch model to ONNX Graph Format...")
    # Export the model
    torch.onnx.export(
        model, 
        dummy_input, 
        ONNX_MODEL_PATH, 
        export_params=True, 
        opset_version=18, 
        do_constant_folding=True, 
        input_names=['input'], 
        output_names=['output'], 
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"[SUCCESS] Model successfully exported to {ONNX_MODEL_PATH}")
    return True

def benchmark_onnx_latency():
    print("\n--- ONNX Runtime Benchmark ---")
    print("Loading ONNX Model into high-performance C++ execution provider...")
    
    # Initialize ONNX Runtime Session
    ort_session = ort.InferenceSession(ONNX_MODEL_PATH)
    
    # Create dummy numpy input matching the expected shape
    dummy_input_numpy = np.random.randn(1, 3, 224, 224).astype(np.float32)
    
    print("Running 100 inference passes to calculate average latency...")
    
    latencies = []
    
    # Warmup runs (not counted)
    for _ in range(10):
        ort_session.run(None, {"input": dummy_input_numpy})
        
    # Benchmark runs
    for _ in range(100):
        start_time = time.time()
        ort_session.run(None, {"input": dummy_input_numpy})
        end_time = time.time()
        latencies.append((end_time - start_time) * 1000) # Convert to ms
        
    avg_latency = sum(latencies) / len(latencies)
    p99_latency = np.percentile(latencies, 99)
    
    print(f"\n[BENCHMARK RESULTS]")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"99th Percentile: {p99_latency:.2f} ms")
    
    if avg_latency < 15.0:
        print("\n[VERIFICATION SUCCESS] The ONNX model successfully achieves sub-15ms latency!")
    else:
        print("\n[WARNING] Latency is slightly higher than 15ms. Consider GPU execution provider for production.")

if __name__ == "__main__":
    success = export_to_onnx()
    if success:
        benchmark_onnx_latency()
