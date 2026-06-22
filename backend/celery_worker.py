import os
import sys
from celery import Celery

# Add the root project path to sys.path so we can import from phase4_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase4_agent.swarm import run_swarm

# Redis broker and backend configuration
# Defaulting to localhost for local dev; can be overridden via ENV vars.
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "aegisnet_worker",
    broker=REDIS_URL,
    backend=RESULT_BACKEND
)

@celery_app.task(name="execute_scenario")
def execute_scenario_task(scenario_params: dict = None):
    """
    Celery task that executes the heavy ML swarm inference asynchronously.
    """
    print(f"Received scenario execution request: {scenario_params}")
    try:
        final_state = run_swarm(scenario_params)
        return final_state
    except Exception as e:
        print(f"Error executing scenario: {e}")
        # Re-raise so Celery marks task as failed
        raise e
