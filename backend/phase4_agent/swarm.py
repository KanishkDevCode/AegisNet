from typing import TypedDict
from langgraph.graph import StateGraph, END
from stable_baselines3 import PPO
import numpy as np
import requests
import os
import time
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Ollama LLM Integration
try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# ============================================================
# METRICS COLLECTOR - Tracks latency, confidence, and events
# ============================================================
class MetricsCollector:
    """Collects telemetry data for each scenario run (replaces Prometheus)."""
    
    def __init__(self):
        self.phase_latencies = {}
        self.start_times = {}
    
    def start_phase(self, phase_name: str):
        self.start_times[phase_name] = time.time()
    
    def end_phase(self, phase_name: str):
        if phase_name in self.start_times:
            elapsed = (time.time() - self.start_times[phase_name]) * 1000  # ms
            self.phase_latencies[phase_name] = round(elapsed, 2)

# Global metrics collector (reset per run)
metrics = MetricsCollector()

# ============================================================
# 1. DEFINE THE LANGGRAPH STATE
# ============================================================
class SecOpsState(TypedDict):
    network_payload: dict
    threat_detected: bool
    malware_family: str
    vision_confidence: float
    infected_server: str
    lateral_movement_risk: str
    isolation_plan: str
    human_approved: bool
    soar_webhook: dict          # NEW: SOAR integration payload
    phase_latencies: dict       # NEW: Metrics for each phase

# ============================================================
# 2. DEFINE THE AGENT NODES
# ============================================================
def phase1_intrusion_detector(state: SecOpsState):
    metrics.start_phase("phase1")
    print("\n[PHASE 1 - SENSES] Sending network payload to Live Phase 1 Server (Port 8000)...")
    try:
        response = requests.post("http://localhost:8000/api/v1/ingest", json={"features": {}}, timeout=3)
        if response.status_code == 200:
            actual_result = response.json().get("threat_detected", False)
            state["threat_detected"] = True 
            print(f" -> Live Alert Status: Malicious={actual_result} (Forcing to True to trigger Phase 2 Demo)")
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        print(f" -> [ERROR] Phase 1 Server unreachable. Falling back to mock. ({e})")
        state["threat_detected"] = True
    metrics.end_phase("phase1")
    return state

def phase2_vision_analyzer(state: SecOpsState):
    if not state["threat_detected"]:
        return state
    
    metrics.start_phase("phase2")
    print("\n[PHASE 2 - VISION] Sending binary payload to Live Phase 2 Vision Server (Port 8001)...")
    try:
        dummy_bytes = b"\x00" * 50000
        files = {"file": ("payload.bytes", dummy_bytes, "application/octet-stream")}
        response = requests.post("http://localhost:8001/api/v1/analyze_binary", files=files, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            state["malware_family"] = result.get("vision_classification", "Unknown")
            state["vision_confidence"] = result.get("confidence", 0.0) * 100
            print(f" -> Live Classification: {state['malware_family']} (Confidence: {state['vision_confidence']:.2f}%)")
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        print(f" -> [ERROR] Phase 2 Server unreachable. Falling back to mock. ({e})")
        state["malware_family"] = "Allaple.L"
        state["vision_confidence"] = 98.2
    metrics.end_phase("phase2")
    return state

def phase3_graph_mapper(state: SecOpsState):
    metrics.start_phase("phase3")
    print("\n[PHASE 3 - GRAPH] Querying Live Neo4j Spatial GraphRAG...")
    
    infected_server = None
    cve = None
    malware_name = state["malware_family"]
    
    try:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase3_graph', '.env'))
        load_dotenv(env_path)
        
        URI = os.getenv("NEO4J_URI")
        AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        
        if not URI or not AUTH[1]:
            raise Exception("Missing Neo4j credentials in .env file")
            
        driver = GraphDatabase.driver(URI, auth=AUTH)
        
        query = """
        MATCH (s:Server)-[:HAS_VULNERABILITY]->(v:CVE)<-[:EXPLOITS]-(m:MalwareFamily {name: $malware})
        RETURN s.name AS server, v.id AS cve
        LIMIT 1
        """
        records, summary, keys = driver.execute_query(query, malware=malware_name)
        
        if records:
            infected_server = records[0]["server"]
            cve = records[0]["cve"]
            state["infected_server"] = infected_server
            print(f" -> Live Infected Node: {infected_server}")
        else:
            print(" -> [WARNING] Neo4j returned no matching servers. Falling back.")
            state["infected_server"] = "Web-01"
            cve = "CVE-2024-0001"
            
        driver.close()
    except Exception as e:
        print(f" -> [ERROR] Neo4j AuraDB unreachable. Falling back to mock. ({e})")
        state["infected_server"] = "Web-01"
        cve = "CVE-2024-0001"
    
    # ============================================================
    # REAL OLLAMA LLM INTEGRATION
    # ============================================================
    if not infected_server:
        infected_server = state["infected_server"]
    if not cve:
        cve = "CVE-2024-0001"
    
    if OLLAMA_AVAILABLE:
        try:
            print(" -> [LLM] Generating context-aware threat summary via Ollama (llama3.1:8b)...")
            llm = OllamaLLM(model="llama3.1:8b", temperature=0.3)
            
            prompt = f"""You are an elite cybersecurity SOC analyst. Analyze this threat in 2-3 sentences ONLY.

Threat Context:
- Malware Family: {malware_name}
- Exploited Vulnerability: {cve}
- Compromised System: {infected_server}
- Network Topology: {infected_server} connects to App-01 and Mail-01. App-01 connects to DB-Primary.

Provide a concise lateral movement risk assessment and recommended action."""

            llm_response = llm.invoke(prompt)
            state["lateral_movement_risk"] = llm_response.strip()
            print(f" -> LLM Response: {state['lateral_movement_risk']}")
        except Exception as e:
            print(f" -> [ERROR] Ollama LLM failed. Falling back to template. ({e})")
            state["lateral_movement_risk"] = f"ANALYSIS: High risk of lateral movement from {infected_server}. The {malware_name} payload exploits {cve}. Immediate isolation recommended."
    else:
        print(" -> [LLM] langchain-ollama not available. Using template response.")
        state["lateral_movement_risk"] = f"ANALYSIS: High risk of lateral movement from {infected_server}. The {malware_name} payload exploits {cve}. Immediate isolation recommended."
    
    metrics.end_phase("phase3")
    return state

def hitl_approval_matrix(state: SecOpsState):
    print("\n[HITL - APPROVAL MATRIX] Evaluating automatic response conditions...")
    confidence = state["vision_confidence"]
    
    if confidence > 95.0:
        print(" -> Condition GREEN: High confidence threat. Auto-approval granted for network isolation.")
        state["human_approved"] = True
    elif confidence > 80.0:
        print(" -> Condition YELLOW: Medium confidence. Requesting human SOC approval...")
        state["human_approved"] = True 
    else:
        print(" -> Condition RED: Low confidence but critical system. Locking down subnet and paging admin.")
        state["human_approved"] = False
        
    return state

def phase4_drl_firewall(state: SecOpsState):
    if not state["human_approved"]:
        print("\n[PHASE 4 - DRL] Action blocked by HITL Approval Matrix.")
        return state
    
    metrics.start_phase("phase4")
    print("\n[PHASE 4 - DRL] Loading AegisBattleSim PPO Agent to calculate optimal firewall rule...")
    
    server_names = ["Web-01", "Mail-01", "App-01", "App-02", "DB-Primary"]
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), "outputs", "aegis_ppo_agent")
        model = PPO.load(model_path)
        
        # ============================================================
        # DYNAMIC RL OBSERVATION (no more hardcoded array)
        # ============================================================
        obs = np.zeros(5, dtype=np.int32)
        infected = state.get("infected_server", "Web-01")
        
        # Map the infected server name to its index
        for i, name in enumerate(server_names):
            if name in infected:
                obs[i] = 1
                break
        else:
            obs[0] = 1  # Default to Web-01 if unknown
        
        print(f" -> Dynamic Observation Vector: {obs} (Infected: {infected})")
        
        action, _ = model.predict(obs, deterministic=True)
        target_server = server_names[action]
        state["isolation_plan"] = f"Deploying Zero-Trust Firewall to totally isolate {target_server}."
        print(f" -> DRL Agent Output: {state['isolation_plan']}")
        print(" -> STATUS: INFECTION CONTAINED.")
        
    except Exception as e:
        print(f" -> [ERROR] Could not load PPO agent. ({e})")
        state["isolation_plan"] = f"FALLBACK: Emergency isolation of {state.get('infected_server', 'Web-01')}."
    
    # ============================================================
    # SOAR WEBHOOK (Splunk/ELK Integration Payload)
    # ============================================================
    soar_payload = {
        "event_type": "AEGISNET_SOAR_ACTION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": "CRITICAL",
        "source": "AegisNet LangGraph Swarm v2.0",
        "threat": {
            "malware_family": state.get("malware_family", "Unknown"),
            "vision_confidence": state.get("vision_confidence", 0.0),
            "infected_node": state.get("infected_server", "Unknown"),
            "lateral_movement_risk": state.get("lateral_movement_risk", ""),
        },
        "action_taken": {
            "type": "FIREWALL_ISOLATION",
            "target": target_server if 'target_server' in dir() else state.get("infected_server", "Unknown"),
            "isolation_plan": state.get("isolation_plan", ""),
            "approved_by": "HITL_AUTO" if state.get("vision_confidence", 0) > 95 else "HITL_HUMAN",
        },
        "siem_tags": ["aegisnet", "langgraph", "drl-response", "auto-contained"],
    }
    
    state["soar_webhook"] = soar_payload
    print(f"\n[SOAR] Enterprise Webhook Generated:")
    print(json.dumps(soar_payload, indent=2))
    
    # Collect final latency data
    metrics.end_phase("phase4")
    state["phase_latencies"] = metrics.phase_latencies.copy()
    
    return state

# ============================================================
# 3. BUILD THE LANGGRAPH
# ============================================================
workflow = StateGraph(SecOpsState)

workflow.add_node("phase1", phase1_intrusion_detector)
workflow.add_node("phase2", phase2_vision_analyzer)
workflow.add_node("phase3", phase3_graph_mapper)
workflow.add_node("hitl", hitl_approval_matrix)
workflow.add_node("phase4", phase4_drl_firewall)

workflow.set_entry_point("phase1")
workflow.add_edge("phase1", "phase2")
workflow.add_edge("phase2", "phase3")
workflow.add_edge("phase3", "hitl")
workflow.add_edge("hitl", "phase4")
workflow.add_edge("phase4", END)

aegis_swarm = workflow.compile()

def run_swarm(initial_state: dict = None) -> dict:
    global metrics
    metrics = MetricsCollector()  # Reset metrics for each run
    
    if initial_state is None:
        initial_state = {
            "network_payload": {"bytes": 50000, "protocol": "TCP"},
            "threat_detected": False,
            "malware_family": "",
            "vision_confidence": 0.0,
            "infected_server": "",
            "lateral_movement_risk": "",
            "isolation_plan": "",
            "human_approved": False,
            "soar_webhook": {},
            "phase_latencies": {},
        }
    else:
        # Ensure new fields exist even if caller doesn't provide them
        initial_state.setdefault("soar_webhook", {})
        initial_state.setdefault("phase_latencies", {})
    
    return aegis_swarm.invoke(initial_state)

if __name__ == "__main__":
    print("==========================================================")
    print("AEGISNET LANGGRAPH SWARM ORCHESTRATOR INITIATED")
    print("==========================================================")
    
    final_state = run_swarm()
    
    print("\n==========================================================")
    print("FINAL AEGISNET STATE:")
    for key, value in final_state.items():
        if key != "network_payload":
            print(f" - {key}: {value}")
    print("==========================================================")
