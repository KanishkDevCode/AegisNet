import requests
import json
import time
import os

# The URL of our local Phase 2 FastAPI server
URL = "http://localhost:8001/api/v1/analyze_binary"

# 1. Create a dummy binary file to act as fake intercepted malware
# We'll just generate 50 KB of random byte noise.
# This should trigger the "30 kB – 60 kB -> 128 width" dynamic reshaping logic.
dummy_filename = "fake_malware_sample.bytes"
print(f"Generating dummy binary file: {dummy_filename}...")
with open(dummy_filename, "wb") as f:
    f.write(os.urandom(50 * 1024)) # 50 KB

print(f"Sending dummy binary to {URL}...")

try:
    start_time = time.time()
    
    # 2. Send the file using multipart/form-data
    with open(dummy_filename, "rb") as f:
        files = {"file": (dummy_filename, f, "application/octet-stream")}
        response = requests.post(URL, files=files)
    
    end_time = time.time()
    
    if response.status_code == 200:
        print("\n[SUCCESS] Received response from AegisNet Phase 2:")
        result = response.json()
        
        print(f"Latency: {(end_time - start_time) * 1000:.2f} ms")
        print(json.dumps(result, indent=4))
        
        print(f"\n[VISION CLASSIFICATION] The ViT Model thinks this file looks like: {result['vision_classification']}")
        print(f"Confidence: {result['confidence']:.2%}")
            
    else:
        print(f"\n[ERROR] Error {response.status_code}: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Connection Error: Is the FastAPI server running on port 8001?")
    print("Please run: python server.py")
finally:
    # Cleanup the dummy file
    if os.path.exists(dummy_filename):
        os.remove(dummy_filename)
