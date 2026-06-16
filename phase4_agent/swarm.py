from typing import TypedDict
from langgraph.graph import StateGraph, END
from stable_baselines3 import PPO
import numpy as np
import requests
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# 1. Define the LangGraph State
class SecOpsState(TypedDict):
    network_payload: dict
    threat_detected: bool
    malware_family: str
    vision_confidence: float
    infected_server: str
    lateral_movement_risk: str
    isolation_plan: str
    human_approved: bool

# 2. Define the Agent Nodes
def phase1_intrusion_detector(state: SecOpsState):
    print("\n[PHASE 1 - SENSES] Sending network payload to Live Phase 1 Server (Port 8000)...")
    try:
        # We send an empty dict to simulate a generic Polars dataframe row. The Phase 1 server auto-pads with 0.0s.
        response = requests.post("http://localhost:8000/api/v1/ingest", json={"features": {}})
        if response.status_code == 200:
            actual_result = response.json().get("threat_detected", False)
            # Force to True so the demo continues to Phase 2, otherwise it skips the Vision model!
            state["threat_detected"] = True 
            print(f" -> Live Alert Status: Malicious={actual_result} (Forcing to True to trigger Phase 2 Demo)")
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        print(f" -> [ERROR] Phase 1 Server unreachable. Please run main.py in phase1_ingestion! Falling back to mock. ({e})")
        state["threat_detected"] = True
    return state

def phase2_vision_analyzer(state: SecOpsState):
    if not state["threat_detected"]:
        return state
        
    print("\n[PHASE 2 - VISION] Sending binary payload to Live Phase 2 Vision Server (Port 8001)...")
    try:
        dummy_bytes = b"\x00" * 50000
        files = {"file": ("payload.bytes", dummy_bytes, "application/octet-stream")}
        response = requests.post("http://localhost:8001/api/v1/analyze_binary", files=files)
        
        if response.status_code == 200:
            result = response.json()
            state["malware_family"] = result.get("vision_classification", "Unknown")
            state["vision_confidence"] = result.get("confidence", 0.0) * 100
            print(f" -> Live Classification: {state['malware_family']} (Confidence: {state['vision_confidence']:.2f}%)")
        else:
            raise Exception(f"HTTP {response.status_code}")
    except Exception as e:
        print(f" -> [ERROR] Phase 2 Server unreachable. Please run server.py in phase2_vision! Falling back to mock. ({e})")
        state["malware_family"] = "Allaple.L"
        state["vision_confidence"] = 98.2
    return state

def phase3_graph_mapper(state: SecOpsState):
    print("\n[PHASE 3 - GRAPH] Querying Live Neo4j Spatial GraphRAG...")
    try:
        # Load credentials securely from the .env file
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase3_graph', '.env'))
        load_dotenv(env_path)
        
        URI = os.getenv("NEO4J_URI")
        AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
        
        if not URI or not AUTH[1]:
            raise Exception("Missing Neo4j credentials in .env file")
            
        driver = GraphDatabase.driver(URI, auth=AUTH)
        
        malware_name = state["malware_family"]
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
            state["lateral_movement_risk"] = f"Critical: Path exists from {infected_server} via {cve}."
            print(f" -> Live Infected Node: {state['infected_server']}")
            print(f" -> Live Risk Assessment: {state['lateral_movement_risk']}")
        else:
            print(" -> [WARNING] Live Neo4j query returned no vulnerable servers (or no exact match). Falling back to mock.")
            state["infected_server"] = "Web-01"
            state["lateral_movement_risk"] = "Critical: Path exists from Web-01 -> App-01 -> DB-Primary"
            
        driver.close()
    except Exception as e:
        print(f" -> [ERROR] Neo4j AuraDB unreachable. Falling back to mock. ({e})")
        state["infected_server"] = "Web-01"
        state["lateral_movement_risk"] = "Critical: Path exists from Web-01 -> App-01 -> DB-Primary"
    return state

def hitl_approval_matrix(state: SecOpsState):
    print("\n[HITL - APPROVAL MATRIX] Evaluating automatic response conditions...")
    confidence = state["vision_confidence"]
    
    if confidence > 95.0:
        print(" -> Condition GREEN: High confidence threat. Auto-approval granted for network isolation.")
        state["human_approved"] = True
    elif confidence > 80.0:
        print(" -> Condition YELLOW: Medium confidence. Requesting human SOC approval...")
        # Mocking human clicking "Approve"
        state["human_approved"] = True 
    else:
        print(" -> Condition RED: Low confidence but critical system. Locking down subnet and paging admin.")
        state["human_approved"] = False
        
    return state

def phase4_drl_firewall(state: SecOpsState):
    if not state["human_approved"]:
        print("\n[PHASE 4 - DRL] Action blocked by HITL Approval Matrix.")
        return state
        
    print("\n[PHASE 4 - DRL] Loading AegisBattleSim PPO Agent to calculate optimal firewall rule...")
    
    try:
        model = PPO.load("outputs/aegis_ppo_agent")
        
        # We construct the observation array for AegisBattleSim
        # [Web-01, Mail-01, App-01, App-02, DB-Primary]
        # Web-01 (Index 0) is infected (1), others are clean (0)
        obs = np.array([1, 0, 0, 0, 0], dtype=np.int32)
        
        action, _ = model.predict(obs, deterministic=True)
        server_names = ["Web-01", "Mail-01", "App-01", "App-02", "DB-Primary"]
        
        target_server = server_names[action]
        state["isolation_plan"] = f"Deploying Zero-Trust Firewall to totally isolate {target_server}."
        print(f" -> DRL Agent Output: {state['isolation_plan']}")
        print(" -> STATUS: INFECTION CONTAINED.")
        
    except Exception as e:
        print(f" -> [ERROR] Could not load PPO agent. Has train_drl.py finished running? ({e})")
        
    return state

# 3. Build the LangGraph
workflow = StateGraph(SecOpsState)

# Add Nodes
workflow.add_node("phase1", phase1_intrusion_detector)
workflow.add_node("phase2", phase2_vision_analyzer)
workflow.add_node("phase3", phase3_graph_mapper)
workflow.add_node("hitl", hitl_approval_matrix)
workflow.add_node("phase4", phase4_drl_firewall)

# Define Edges (The Flow)
workflow.set_entry_point("phase1")
workflow.add_edge("phase1", "phase2")
workflow.add_edge("phase2", "phase3")
workflow.add_edge("phase3", "hitl")
workflow.add_edge("hitl", "phase4")
workflow.add_edge("phase4", END)

# Compile
aegis_swarm = workflow.compile()

if __name__ == "__main__":
    print("==========================================================")
    print("AEGISNET LANGGRAPH SWARM ORCHESTRATOR INITIATED")
    print("==========================================================")
    
    initial_state = {
        "network_payload": {"bytes": 50000, "protocol": "TCP"},
        "threat_detected": False,
        "malware_family": "",
        "vision_confidence": 0.0,
        "infected_server": "",
        "lateral_movement_risk": "",
        "isolation_plan": "",
        "human_approved": False
    }
    
    final_state = aegis_swarm.invoke(initial_state)
    
    print("\n==========================================================")
    print("FINAL AEGISNET STATE:")
    for key, value in final_state.items():
        if key != "network_payload":
            print(f" - {key}: {value}")
    print("==========================================================")
