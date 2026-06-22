"""
AegisNet Metrics Module
========================
Replaces Prometheus + Grafana with a native Python metrics store.
Tracks scenario history, inference latencies, confidence trends, and drift scores.
"""

import time
import random
from datetime import datetime, timezone
from collections import deque


class AegisMetricsStore:
    """In-memory metrics store that serves telemetry data to the frontend dashboard."""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.scenarios_total = 0
        self.scenarios_success = 0
        self.scenarios_failure = 0
        self.threats_detected = 0
        self.containments = 0
        
        # Rolling history for charts
        self.confidence_history = deque(maxlen=max_history)
        self.latency_history = deque(maxlen=max_history)
        self.drift_history = deque(maxlen=max_history)
    
    def record_scenario(self, final_state: dict):
        """Record metrics from a completed scenario run."""
        self.scenarios_total += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if final_state.get("isolation_plan"):
            self.scenarios_success += 1
            self.containments += 1
        else:
            self.scenarios_failure += 1
        
        if final_state.get("threat_detected"):
            self.threats_detected += 1
        
        # Record confidence data point
        confidence = final_state.get("vision_confidence", 0.0)
        self.confidence_history.append({
            "timestamp": timestamp,
            "value": round(confidence, 2),
            "label": f"Run #{self.scenarios_total}"
        })
        
        # Record latency data points
        latencies = final_state.get("phase_latencies", {})
        self.latency_history.append({
            "timestamp": timestamp,
            "label": f"Run #{self.scenarios_total}",
            "phase1": latencies.get("phase1", 0),
            "phase2": latencies.get("phase2", 0),
            "phase3": latencies.get("phase3", 0),
            "phase4": latencies.get("phase4", 0),
        })
        
        # Simulate data drift (Wasserstein Distance)
        # In production, this would come from Evidently AI
        drift_score = round(random.uniform(0.02, 0.18), 4)
        self.drift_history.append({
            "timestamp": timestamp,
            "value": drift_score,
            "label": f"Run #{self.scenarios_total}",
            "status": "OK" if drift_score < 0.10 else ("WARNING" if drift_score < 0.15 else "CRITICAL")
        })
    
    def get_dashboard_data(self) -> dict:
        """Return all metrics as a JSON-serializable dictionary."""
        return {
            "counters": {
                "total_scenarios": self.scenarios_total,
                "successful": self.scenarios_success,
                "failed": self.scenarios_failure,
                "threats_detected": self.threats_detected,
                "containments": self.containments,
            },
            "confidence_history": list(self.confidence_history),
            "latency_history": list(self.latency_history),
            "drift_history": list(self.drift_history),
            "current_drift": self.drift_history[-1]["value"] if self.drift_history else 0.0,
            "drift_status": self.drift_history[-1]["status"] if self.drift_history else "OK",
        }


# Singleton instance
metrics_store = AegisMetricsStore()
