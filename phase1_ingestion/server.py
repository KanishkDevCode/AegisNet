from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from catboost import CatBoostClassifier
import pandas as pd
import json
import os
from typing import Dict, Any

app = FastAPI(title="AegisNet Phase 1: Ingestion & Inference (CatBoost)")

# Global variables
model = None
label_mapping = {}
feature_names = []

class NetflowPayload(BaseModel):
    # Payload accepts arbitrary features, we align them to CatBoost's expected input
    features: Dict[str, float]

@app.on_event("startup")
async def load_model():
    global model, label_mapping, feature_names
    
    # Updated paths based on Kaggle output
    model_path = "outputs/phase1_catboost_model.cbm"
    mapping_path = "outputs/phase1_label_mapping.json"
    features_path = "outputs/phase1_feature_names.json"
    
    if os.path.exists(model_path) and os.path.exists(mapping_path) and os.path.exists(features_path):
        print("Loading CatBoost model, label mapping, and feature names...")
        
        # Load CatBoost
        model = CatBoostClassifier()
        model.load_model(model_path)
        
        # Load Label Mapping
        with open(mapping_path, "r") as f:
            label_mapping = json.load(f)
            
        # Load Feature Names (Crucial for CatBoost alignment)
        with open(features_path, "r") as f:
            feature_names = json.load(f)
            
        print("AegisNet Phase 1 Model Engine successfully loaded!")
    else:
        print(f"WARNING: One or more model files missing in this directory.")
        print(f"Expected: {model_path}, {mapping_path}, {features_path}")

@app.post("/api/v1/ingest")
async def ingest_netflow(payload: NetflowPayload):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please provide the trained CatBoost model files.")
    
    try:
        # Convert incoming payload to a dictionary
        incoming_features = payload.features
        
        # Build the feature array in the EXACT order the model expects
        # If a feature is missing from the payload, default to 0.0
        aligned_features = []
        for feat in feature_names:
            aligned_features.append(incoming_features.get(feat, 0.0))
            
        # CatBoost can predict directly on a 2D list/array
        prediction = model.predict([aligned_features])
        
        # CatBoost multi-class predict returns an array of shape (1, 1), e.g. [[class_idx]]
        predicted_class_idx = int(prediction[0][0])
        
        # Also get probabilities to trigger Phase 2 if confidence is high
        probs = model.predict_proba([aligned_features])[0]
        confidence = float(probs[predicted_class_idx])
        
        threat_name = label_mapping.get(str(predicted_class_idx), "UNKNOWN")
        
        is_anomaly = threat_name.upper() != "BENIGN"
        
        # LangGraph Contract Response
        network_alert = {
            "threat_detected": is_anomaly,
            "predicted_class": threat_name,
            "confidence_score": confidence,
            "raw_features": incoming_features
        }
        
        return network_alert

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
