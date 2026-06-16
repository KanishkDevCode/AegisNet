import pandas as pd
import numpy as np
import os
from evidently import Report
from evidently.metrics import *
from evidently.presets import DataDriftPreset

# Setup absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ONNX_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
os.makedirs(ONNX_OUTPUT_DIR, exist_ok=True)
REPORT_PATH = os.path.join(ONNX_OUTPUT_DIR, "data_drift_report.html")

def generate_mock_data():
    """
    Generates mock Phase 1 Network features to simulate data drift.
    """
    # Features from Phase 1
    columns = [
        "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
        "Fwd Packet Length Max", "Bwd Packet Length Max", "Flow Bytes/s",
        "Flow Packets/s", "Fwd IAT Mean", "Bwd IAT Mean", "Fwd PSH Flags",
        "FIN Flag Count", "SYN Flag Count"
    ]
    
    # 1. Generate "Reference" Baseline Data (What the AI trained on last week)
    # Using normal statistical distributions
    reference_data = pd.DataFrame({
        col: np.random.normal(loc=50, scale=10, size=1000) for col in columns
    })
    
    # 2. Generate "Current" Live Data (What the AI saw today)
    # Simulate an attacker changing tactics (Data Drift!)
    # We increase the mean and standard deviation of packet lengths and flows.
    current_data = pd.DataFrame({
        col: np.random.normal(loc=50, scale=10, size=1000) for col in columns
    })
    
    # Inject massive drift into specific features to trigger the alarm
    current_data["Total Fwd Packets"] = np.random.normal(loc=150, scale=50, size=1000) # Drift!
    current_data["Fwd Packet Length Max"] = np.random.normal(loc=1024, scale=100, size=1000) # Drift!
    current_data["SYN Flag Count"] = np.random.choice([0, 1], size=1000, p=[0.2, 0.8]) # Drift!
    
    return reference_data, current_data

def run_evidently_drift_report():
    print("Generating Mock Network Traffic for Baseline and Current data...")
    reference_data, current_data = generate_mock_data()
    
    print("\nInitializing Evidently AI Data Drift Report...")
    print("Calculating Statistical Distance Metrics (e.g., Wasserstein distance, Jensen-Shannon)...")
    
    # Run the Evidently Report with the DataDriftPreset
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_data, current_data=current_data)
    
    # Save the report as an interactive HTML file
    print(f"\nExporting interactive Data Drift Dashboard to {REPORT_PATH}...")
    report.save_html(REPORT_PATH)
    
    print("\n[SUCCESS] Phase 5 Data Drift Tracking completed.")
    print(f"You can now open {REPORT_PATH} in your web browser to view the AI monitoring dashboard!")

if __name__ == "__main__":
    run_evidently_drift_report()
