"""
AegisBattleSim - Native CyberBattleSim Replacement
====================================================
A custom Gymnasium environment that simulates a 5-node corporate network
for training Deep Reinforcement Learning (PPO) agents to contain threats.

This is a drop-in replacement for Microsoft's CyberBattleSim, built natively
so it runs on any machine without complex C++ build dependencies.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np


class AegisBattleSimEnv(gym.Env):
    """
    A 5-node corporate network simulation environment.

    Nodes:
        0: Web-01 (DMZ)     - Public-facing web server
        1: Mail-01           - Email gateway
        2: App-01            - Internal application server
        3: App-02            - Secondary application server
        4: DB-Primary        - Critical database (crown jewels)

    Adjacency Matrix (lateral movement paths):
        Web-01  -> App-01, Mail-01
        Mail-01 -> App-02
        App-01  -> DB-Primary
        App-02  -> DB-Primary

    Observation Space: [5] binary array (0=clean, 1=infected)
    Action Space: Discrete(5) - Which server to isolate with a firewall rule

    Reward Logic:
        +10  if the agent isolates the originally infected node
        +5   if the agent isolates a node adjacent to the infection (preemptive)
        -10  if the agent isolates DB-Primary when it's not infected (false positive)
        -5   if the agent isolates a completely unrelated node
    """

    metadata = {"render_modes": ["human"]}

    SERVER_NAMES = ["Web-01", "Mail-01", "App-01", "App-02", "DB-Primary"]

    # Adjacency matrix representing lateral movement paths
    ADJACENCY = {
        0: [2, 1],      # Web-01 -> App-01, Mail-01
        1: [3],          # Mail-01 -> App-02
        2: [4],          # App-01 -> DB-Primary
        3: [4],          # App-02 -> DB-Primary
        4: [],           # DB-Primary -> (terminal node)
    }

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        # Observation: 5 binary values (infected or not)
        self.observation_space = spaces.MultiBinary(5)

        # Action: which of the 5 servers to isolate
        self.action_space = spaces.Discrete(5)

        # Internal state
        self.state = np.zeros(5, dtype=np.int8)
        self.initial_infection_idx = 0
        self.steps = 0
        self.max_steps = 10

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Reset the network
        self.state = np.zeros(5, dtype=np.int8)
        self.steps = 0

        # Randomly infect one of the entry-point servers (Web-01 or Mail-01)
        self.initial_infection_idx = self.np_random.choice([0, 1])
        self.state[self.initial_infection_idx] = 1

        # Simulate 1-2 steps of lateral movement
        spread_steps = self.np_random.integers(0, 3)
        infected_nodes = [self.initial_infection_idx]

        for _ in range(spread_steps):
            new_infections = []
            for node in infected_nodes:
                for neighbor in self.ADJACENCY.get(node, []):
                    if self.state[neighbor] == 0:
                        # 60% chance of lateral movement per hop
                        if self.np_random.random() < 0.6:
                            self.state[neighbor] = 1
                            new_infections.append(neighbor)
            infected_nodes.extend(new_infections)

        return self.state.copy(), {"infected_nodes": infected_nodes}

    def step(self, action: int):
        self.steps += 1
        reward = 0.0
        terminated = False
        truncated = self.steps >= self.max_steps

        isolated_server = self.SERVER_NAMES[action]

        # Calculate reward
        if self.state[action] == 1:
            # Agent correctly isolated an infected node
            if action == self.initial_infection_idx:
                reward = 10.0  # Isolated the source — best outcome
            else:
                reward = 5.0   # Isolated a spread node — good
            self.state[action] = 0  # Clean the node
            terminated = True
        else:
            # Agent isolated a clean node (false positive)
            if action == 4:  # DB-Primary
                reward = -10.0  # Never isolate the database unnecessarily
            else:
                reward = -5.0

        info = {
            "isolated_server": isolated_server,
            "remaining_infections": int(self.state.sum()),
            "initial_infection": self.SERVER_NAMES[self.initial_infection_idx],
        }

        return self.state.copy(), reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "human":
            status = []
            for i, name in enumerate(self.SERVER_NAMES):
                icon = "🔴" if self.state[i] == 1 else "🟢"
                status.append(f"  {icon} {name}")
            print("\\n--- AegisBattleSim Network Status ---")
            print("\\n".join(status))
            print("--------------------------------------")


# Register the environment with Gymnasium
gym.register(
    id="AegisBattleSim-v0",
    entry_point="phase4_agent.aegis_battlesim:AegisBattleSimEnv",
)
