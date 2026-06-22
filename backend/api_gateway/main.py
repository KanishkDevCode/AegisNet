import os
import sys
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Add root project path to sys.path so we can import swarm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_gateway.metrics import metrics_store

app = FastAPI(title="AegisNet API Gateway", version="2.0.0")

# Add CORS Middleware so Next.js on port 3000 can talk to FastAPI on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local memory store to bypass Redis on Windows
TASK_STORE = {}

def process_scenario_background(task_id: str, state: dict):
    from phase4_agent.swarm import run_swarm
    TASK_STORE[task_id] = {"status": "PROCESSING", "result": None}
    try:
        final_state = run_swarm(state)
        TASK_STORE[task_id] = {"status": "SUCCESS", "result": final_state}
        # Record metrics from the completed scenario
        metrics_store.record_scenario(final_state)
    except Exception as e:
        TASK_STORE[task_id] = {"status": "FAILURE", "result": str(e)}

class ScenarioRequest(BaseModel):
    network_payload: Dict[str, Any] = {"bytes": 50000, "protocol": "TCP"}

@app.post("/api/scenarios")
async def create_scenario(request: ScenarioRequest, background_tasks: BackgroundTasks):
    """
    Submit a new scenario to be processed asynchronously by FastAPI Background Tasks.
    """
    try:
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
        
        # Dispatch the task to run in the background
        background_tasks.add_task(process_scenario_background, task_id, initial_state)
        
        return {
            "status": "success",
            "message": "Scenario queued for processing",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios/{task_id}")
async def get_scenario_status(task_id: str):
    """
    Check the status of a scenario task.
    """
    try:
        task = TASK_STORE.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "result": task["result"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """
    Return telemetry data for the MLOps Dashboard (replaces Prometheus + Grafana).
    """
    return metrics_store.get_dashboard_data()
