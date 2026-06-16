import requests
import json
import time

# The URL of our local Phase 1 FastAPI server
URL = "http://localhost:8000/api/v1/ingest"

# A mock netflow payload (representing a single row of network traffic)
# We use a mix of random feature names. CatBoost will align them using feature_names.json.
mock_payload = {
    "features": {
        "Flow Duration": 500000.0,
        "Total Fwd Packets": 15.0,
        "Total Backward Packets": 12.0,
        "Fwd Packet Length Max": 1024.0,
        "Bwd Packet Length Max": 512.0,
        "Flow Bytes/s": 2500.5,
        "Flow Packets/s": 50.0,
        "Fwd IAT Mean": 1200.0,
        "Bwd IAT Mean": 1100.0,
        "Fwd PSH Flags": 0.0,
        "FIN Flag Count": 1.0,
        "SYN Flag Count": 0.0
    }
}

print(f"Sending mock network traffic to {URL}...")

try:
    start_time = time.time()
    
    # Send the POST request
    response = requests.post(URL, json=mock_payload)
    
    end_time = time.time()
    
    if response.status_code == 200:
        print("\n[SUCCESS] Received response from AegisNet Phase 1:")
        result = response.json()
        
        print(f"Latency: {(end_time - start_time) * 1000:.2f} ms")
        print(json.dumps(result, indent=4))
        
        if result["threat_detected"]:
            print(f"\n[ALERT] Threat detected! Model classified traffic as: {result['predicted_class']}")
            print(f"Confidence: {result['confidence_score']:.2%}")
        else:
            print("\n[INFO] Traffic is BENIGN. No action required.")
            
    else:
        print(f"\n[ERROR] Error {response.status_code}: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Connection Error: Is the FastAPI server running on port 8000?")
    print("Please run: python server.py")
