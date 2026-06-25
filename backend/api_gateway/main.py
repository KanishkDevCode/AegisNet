"""
AegisNet API Gateway v3.2
==========================
UNIFIED BACKEND: Loads ALL models (CatBoost, ViT, PPO) at startup.
Now with HITL (Human-in-the-Loop) approval endpoint.
v3.2: Added WebSocket endpoint for real-time metrics push.
"""

import os
import sys
import uuid
import asyncio
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Set

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_gateway.metrics import metrics_store

app = FastAPI(title="AegisNet API Gateway", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task store — holds all scenario states
# Status values: PENDING | PROCESSING | AWAITING_APPROVAL | SUCCESS | FAILURE | DENIED
TASK_STORE: Dict[str, dict] = {}

# ============================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================
class ConnectionManager:
    """Manages active WebSocket connections for real-time metrics push."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"  [WS] Client connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"  [WS] Client disconnected. Active connections: {len(self.active_connections)}")
    
    async def broadcast_metrics(self):
        """Push current metrics to all connected WebSocket clients."""
        if not self.active_connections:
            return
        data = json.dumps(metrics_store.get_dashboard_data())
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)

ws_manager = ConnectionManager()


@app.on_event("startup")
async def startup_load_models():
    """Pre-load ALL ML models into memory once at boot."""
    from phase4_agent.swarm import registry
    registry.load_all()


def process_scenario_background(task_id: str, state: dict):
    """Run the full 4-phase swarm pipeline in a background thread."""
    from phase4_agent.swarm import run_swarm_phase1_to_3, run_phase4
    TASK_STORE[task_id] = {"status": "PROCESSING", "result": None}
    try:
        # Run Phase 1-3 first to get confidence score
        intermediate_state = run_swarm_phase1_to_3(state)
        
        if not intermediate_state.get("threat_detected", False):
            # Benign! No need for HITL or Phase 4
            TASK_STORE[task_id] = {"status": "SUCCESS", "result": intermediate_state}
            metrics_store.record_scenario(intermediate_state)
            return

        confidence = intermediate_state.get("vision_confidence", 0.0)

        if confidence < 95.0:
            # Medium/Low confidence — pause and wait for human approval
            TASK_STORE[task_id] = {
                "status": "AWAITING_APPROVAL",
                "result": intermediate_state
            }
            print(f"\n[HITL] Task {task_id} paused — confidence {confidence:.2f}% < 95%. Awaiting human approval.")
        else:
            # High confidence — auto-approve and run Phase 4
            intermediate_state["human_approved"] = True
            final_state = run_phase4(intermediate_state)
            TASK_STORE[task_id] = {"status": "SUCCESS", "result": final_state}
            metrics_store.record_scenario(final_state)

    except Exception as e:
        TASK_STORE[task_id] = {"status": "FAILURE", "result": str(e)}


def finalize_scenario_background(task_id: str, state: dict, approved: bool):
    """Continue from Phase 4 after human approval/denial."""
    from phase4_agent.swarm import run_phase4
    try:
        state["human_approved"] = approved
        if approved:
            final_state = run_phase4(state)
            TASK_STORE[task_id] = {"status": "SUCCESS", "result": final_state}
            metrics_store.record_scenario(final_state)
        else:
            state["isolation_plan"] = "ACTION DENIED: Human analyst rejected auto-containment."
            TASK_STORE[task_id] = {"status": "DENIED", "result": state}
            metrics_store.record_scenario(state)
    except Exception as e:
        TASK_STORE[task_id] = {"status": "FAILURE", "result": str(e)}


class ScenarioRequest(BaseModel):
    network_payload: Dict[str, Any] = {"bytes": 50000, "protocol": "TCP"}


@app.post("/api/scenarios")
async def create_scenario(request: ScenarioRequest, background_tasks: BackgroundTasks):
    """Submit a new scenario. Runs Phase 1-3, then waits for HITL if confidence < 80%."""
    initial_state = {
        "network_payload": request.network_payload,
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
    task_id = str(uuid.uuid4())
    TASK_STORE[task_id] = {"status": "PENDING", "result": None}
    background_tasks.add_task(process_scenario_background, task_id, initial_state)
    return {"status": "success", "message": "Scenario queued", "task_id": task_id}


@app.get("/api/scenarios/{task_id}")
async def get_scenario_status(task_id: str):
    """Poll scenario status. Returns AWAITING_APPROVAL when human action needed."""
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": task["status"], "result": task["result"]}


@app.post("/api/scenarios/{task_id}/approve")
async def approve_scenario(task_id: str, background_tasks: BackgroundTasks):
    """Human analyst approves the HITL — triggers Phase 4 (DRL firewall isolation)."""
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "AWAITING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Task is not awaiting approval. Current status: {task['status']}")
    
    TASK_STORE[task_id]["status"] = "PROCESSING"
    intermediate_state = task["result"]
    background_tasks.add_task(finalize_scenario_background, task_id, intermediate_state, True)
    return {"status": "success", "message": "Approval granted. Phase 4 DRL agent executing."}


@app.post("/api/scenarios/{task_id}/deny")
async def deny_scenario(task_id: str, background_tasks: BackgroundTasks):
    """Human analyst denies the HITL — blocks the DRL agent from acting."""
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "AWAITING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Task is not awaiting approval. Current status: {task['status']}")
    
    TASK_STORE[task_id]["status"] = "PROCESSING"
    intermediate_state = task["result"]
    background_tasks.add_task(finalize_scenario_background, task_id, intermediate_state, False)
    return {"status": "success", "message": "Action denied by human analyst."}


@app.get("/api/metrics")
async def get_metrics():
    """Return telemetry data for the MLOps Dashboard (HTTP fallback)."""
    return metrics_store.get_dashboard_data()


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """Real-time WebSocket endpoint for MLOps telemetry push.
    
    Replaces the 3-second HTTP polling with an efficient push model.
    Only sends data when metrics actually change.
    """
    await ws_manager.connect(websocket)
    last_hash = None
    try:
        while True:
            # Build current metrics snapshot
            data = metrics_store.get_dashboard_data()
            current_hash = hash(json.dumps(data, sort_keys=True))
            
            # Only push if data has changed
            if current_hash != last_hash:
                await websocket.send_text(json.dumps(data))
                last_hash = current_hash
            
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
