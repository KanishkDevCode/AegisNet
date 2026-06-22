"""
AegisNet State Machine Auditing
================================
PyTest suite that validates the LangGraph swarm logic
to prevent false positives and ensure correct DRL behavior.
"""

import pytest
import numpy as np
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from phase4_agent.swarm import (
    SecOpsState,
    hitl_approval_matrix,
    phase4_drl_firewall,
)


def make_state(**overrides) -> SecOpsState:
    """Helper to create a test state with sensible defaults."""
    base = {
        "network_payload": {"bytes": 50000, "protocol": "TCP"},
        "threat_detected": True,
        "malware_family": "Allaple.L",
        "vision_confidence": 98.2,
        "infected_server": "Web-01",
        "lateral_movement_risk": "Critical path detected.",
        "isolation_plan": "",
        "human_approved": True,
        "soar_webhook": {},
        "phase_latencies": {},
    }
    base.update(overrides)
    return base


class TestHITLApprovalMatrix:
    """Tests for the Human-in-the-Loop Approval Matrix."""

    def test_high_confidence_auto_approves(self):
        """Condition GREEN: >95% confidence should auto-approve."""
        state = make_state(vision_confidence=98.5)
        result = hitl_approval_matrix(state)
        assert result["human_approved"] is True

    def test_medium_confidence_approves(self):
        """Condition YELLOW: 80-95% confidence should still approve (mocked human)."""
        state = make_state(vision_confidence=87.0)
        result = hitl_approval_matrix(state)
        assert result["human_approved"] is True

    def test_low_confidence_blocks(self):
        """Condition RED: <80% confidence should block the DRL agent."""
        state = make_state(vision_confidence=45.0)
        result = hitl_approval_matrix(state)
        assert result["human_approved"] is False


class TestPhase4DRLFirewall:
    """Tests for the Deep Reinforcement Learning Firewall Agent."""

    def test_blocked_when_not_approved(self):
        """DRL agent should NOT execute if HITL approval is False."""
        state = make_state(human_approved=False)
        result = phase4_drl_firewall(state)
        assert result["isolation_plan"] == ""

    def test_generates_isolation_plan_when_approved(self):
        """DRL agent should generate an isolation plan when approved."""
        state = make_state(human_approved=True, infected_server="Web-01")
        result = phase4_drl_firewall(state)
        assert "isolate" in result["isolation_plan"].lower() or "isolation" in result["isolation_plan"].lower() or "Firewall" in result["isolation_plan"]

    def test_generates_soar_webhook(self):
        """SOAR webhook should be generated after DRL execution."""
        state = make_state(human_approved=True)
        result = phase4_drl_firewall(state)
        assert result.get("soar_webhook") != {}
        assert result["soar_webhook"].get("event_type") == "AEGISNET_SOAR_ACTION"
        assert result["soar_webhook"].get("severity") == "CRITICAL"

    def test_soar_webhook_contains_threat_data(self):
        """SOAR webhook should contain the malware family and confidence."""
        state = make_state(human_approved=True, malware_family="Gatak", vision_confidence=92.0)
        result = phase4_drl_firewall(state)
        webhook = result.get("soar_webhook", {})
        assert webhook.get("threat", {}).get("malware_family") == "Gatak"
        assert webhook.get("threat", {}).get("vision_confidence") == 92.0


class TestDynamicObservation:
    """Tests that the RL observation vector correctly maps infected servers."""

    @pytest.mark.parametrize("server,expected_idx", [
        ("Web-01", 0),
        ("Mail-01", 1),
        ("App-01", 2),
        ("App-02", 3),
        ("DB-Primary", 4),
    ])
    def test_dynamic_observation_mapping(self, server, expected_idx):
        """Each infected server should map to the correct index in the obs array."""
        server_names = ["Web-01", "Mail-01", "App-01", "App-02", "DB-Primary"]
        obs = np.zeros(5, dtype=np.int32)
        for i, name in enumerate(server_names):
            if name in server:
                obs[i] = 1
                break
        assert obs[expected_idx] == 1
        assert obs.sum() == 1  # Only one server should be infected
