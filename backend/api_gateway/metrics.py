"""
AegisNet Metrics Module v2.0
==============================
Persistent SQLite-backed metrics store that survives server restarts.
Replaces Prometheus + Grafana with a native Python metrics store.
Tracks scenario history, inference latencies, confidence trends, and drift scores.
"""

import os
import json
import time
import random
import sqlite3
from datetime import datetime, timezone
from collections import deque
from threading import Lock

# Store the database in the backend directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aegisnet_metrics.db")


class AegisMetricsStore:
    """SQLite-backed metrics store that persists telemetry data across server restarts."""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self._lock = Lock()
        self._init_db()
        self._load_from_db()
    
    def _init_db(self):
        """Create the SQLite database and tables if they don't exist."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                scenarios_total INTEGER DEFAULT 0,
                scenarios_success INTEGER DEFAULT 0,
                scenarios_failure INTEGER DEFAULT 0,
                threats_detected INTEGER DEFAULT 0,
                containments INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confidence_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                label TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS latency_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                label TEXT NOT NULL,
                phase1 REAL DEFAULT 0,
                phase2 REAL DEFAULT 0,
                phase3 REAL DEFAULT 0,
                phase4 REAL DEFAULT 0,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drift_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                label TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Initialize counters row if it doesn't exist
        cursor.execute("INSERT OR IGNORE INTO counters (id) VALUES (1)")
        
        conn.commit()
        conn.close()
        print(f"  [MLOps] Metrics database initialized at {DB_PATH}")
    
    def _load_from_db(self):
        """Load existing metrics from SQLite into memory for fast reads."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Load counters
        cursor.execute("SELECT * FROM counters WHERE id = 1")
        row = cursor.fetchone()
        if row:
            self.scenarios_total = row[1]
            self.scenarios_success = row[2]
            self.scenarios_failure = row[3]
            self.threats_detected = row[4]
            self.containments = row[5]
        else:
            self.scenarios_total = 0
            self.scenarios_success = 0
            self.scenarios_failure = 0
            self.threats_detected = 0
            self.containments = 0
        
        # Load rolling histories (last N entries)
        self.confidence_history = deque(maxlen=self.max_history)
        cursor.execute(f"SELECT timestamp, value, label FROM confidence_history ORDER BY id DESC LIMIT {self.max_history}")
        for row in reversed(cursor.fetchall()):
            self.confidence_history.append({"timestamp": row[0], "value": row[1], "label": row[2]})
        
        self.latency_history = deque(maxlen=self.max_history)
        cursor.execute(f"SELECT timestamp, label, phase1, phase2, phase3, phase4 FROM latency_history ORDER BY id DESC LIMIT {self.max_history}")
        for row in reversed(cursor.fetchall()):
            self.latency_history.append({
                "timestamp": row[0], "label": row[1],
                "phase1": row[2], "phase2": row[3], "phase3": row[4], "phase4": row[5]
            })
        
        self.drift_history = deque(maxlen=self.max_history)
        cursor.execute(f"SELECT timestamp, value, label, status FROM drift_history ORDER BY id DESC LIMIT {self.max_history}")
        for row in reversed(cursor.fetchall()):
            self.drift_history.append({"timestamp": row[0], "value": row[1], "label": row[2], "status": row[3]})
        
        conn.close()
        
        if self.scenarios_total > 0:
            print(f"  [MLOps] Restored {self.scenarios_total} historical scenarios from database.")
    
    def record_scenario(self, final_state: dict):
        """Record metrics from a completed scenario run (persists to SQLite)."""
        with self._lock:
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
            conf_entry = {
                "timestamp": timestamp,
                "value": round(confidence, 2),
                "label": f"Run #{self.scenarios_total}"
            }
            self.confidence_history.append(conf_entry)
            
            # Record latency data points
            latencies = final_state.get("phase_latencies", {})
            lat_entry = {
                "timestamp": timestamp,
                "label": f"Run #{self.scenarios_total}",
                "phase1": latencies.get("phase1", 0),
                "phase2": latencies.get("phase2", 0),
                "phase3": latencies.get("phase3", 0),
                "phase4": latencies.get("phase4", 0),
            }
            self.latency_history.append(lat_entry)
            
            # Simulate data drift (Wasserstein Distance)
            # In production, this would come from Evidently AI
            drift_score = round(random.uniform(0.02, 0.18), 4)
            drift_entry = {
                "timestamp": timestamp,
                "value": drift_score,
                "label": f"Run #{self.scenarios_total}",
                "status": "OK" if drift_score < 0.10 else ("WARNING" if drift_score < 0.15 else "CRITICAL")
            }
            self.drift_history.append(drift_entry)
            
            # Persist to SQLite
            self._persist_to_db(conf_entry, lat_entry, drift_entry)
    
    def _persist_to_db(self, conf_entry, lat_entry, drift_entry):
        """Write the latest metrics to the SQLite database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Update counters
            cursor.execute("""
                UPDATE counters SET
                    scenarios_total = ?,
                    scenarios_success = ?,
                    scenarios_failure = ?,
                    threats_detected = ?,
                    containments = ?
                WHERE id = 1
            """, (self.scenarios_total, self.scenarios_success, self.scenarios_failure,
                  self.threats_detected, self.containments))
            
            # Insert history entries
            cursor.execute(
                "INSERT INTO confidence_history (timestamp, value, label) VALUES (?, ?, ?)",
                (conf_entry["timestamp"], conf_entry["value"], conf_entry["label"])
            )
            cursor.execute(
                "INSERT INTO latency_history (timestamp, label, phase1, phase2, phase3, phase4) VALUES (?, ?, ?, ?, ?, ?)",
                (lat_entry["timestamp"], lat_entry["label"],
                 lat_entry["phase1"], lat_entry["phase2"], lat_entry["phase3"], lat_entry["phase4"])
            )
            cursor.execute(
                "INSERT INTO drift_history (timestamp, value, label, status) VALUES (?, ?, ?, ?)",
                (drift_entry["timestamp"], drift_entry["value"], drift_entry["label"], drift_entry["status"])
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"  [MLOps] WARNING: Failed to persist metrics to SQLite: {e}")
    
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
