import gymnasium as gym
from gymnasium import spaces
import numpy as np

class AegisBattleSim(gym.Env):
    """
    A lightweight, custom Reinforcement Learning environment replacing Microsoft's CyberBattleSim.
    This exactly simulates our Phase 3 Neo4j Corporate Network:
    - 5 Nodes: Web-01 (0), Mail-01 (1), App-01 (2), App-02 (3), DB-Primary (4)
    - The infection always starts in the DMZ (Web-01 or Mail-01)
    - The goal is to isolate the infected nodes BEFORE the infection spreads to DB-Primary
    """
    metadata = {"render_modes": ["console"]}

    def __init__(self):
        super(AegisBattleSim, self).__init__()
        
        # 5 Servers in our Neo4j graph
        self.num_nodes = 5
        
        # Action Space: 5 discrete actions (Isolate Node 0, 1, 2, 3, or 4)
        self.action_space = spaces.Discrete(self.num_nodes)
        
        # Observation Space: Array of length 5. 
        # 0 = Normal, 1 = Infected, 2 = Isolated (Firewall blocked)
        self.observation_space = spaces.Box(low=0, high=2, shape=(self.num_nodes,), dtype=np.int32)
        
        # Network Topology Matrix (Who can infect who?)
        # 0:Web-01 -> 2:App-01
        # 1:Mail-01 -> 3:App-02
        # 2:App-01 -> 4:DB-Primary
        # 3:App-02 -> 4:DB-Primary
        self.adjacency_matrix = {
            0: [2],
            1: [3],
            2: [4],
            3: [4],
            4: []
        }
        
        self.state = None
        self.current_step = 0
        self.max_steps = 10

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.zeros(self.num_nodes, dtype=np.int32)
        
        # Randomly infect one of the DMZ servers (0 or 1) to start the simulation
        start_node = self.np_random.choice([0, 1])
        self.state[start_node] = 1 
        
        self.current_step = 0
        return self.state, {}

    def step(self, action):
        self.current_step += 1
        reward = 0
        terminated = False
        
        # 1. Apply the Agent's Action (Isolate a node)
        if self.state[action] != 2: # If not already isolated
            if self.state[action] == 1:
                # Good! Isolated an infected node
                reward += 10
            else:
                # Bad! Isolated a clean node (Business disruption)
                reward -= 5
            
            self.state[action] = 2 # Mark as isolated
        else:
            # Wasted action on an already isolated node
            reward -= 1
            
        # 2. Simulate Malware Spreading (Lateral Movement)
        new_infections = []
        for node in range(self.num_nodes):
            if self.state[node] == 1: # If node is infected
                for neighbor in self.adjacency_matrix[node]:
                    # If neighbor is clean (0), infect it!
                    if self.state[neighbor] == 0:
                        new_infections.append(neighbor)
                        
        for n in new_infections:
            self.state[n] = 1
            
        # 3. Check Win/Loss Conditions
        # Did the database get infected? (Loss)
        if self.state[4] == 1:
            reward -= 100
            terminated = True
            
        # Is the infection totally contained? (Win)
        elif 1 not in self.state:
            reward += 50
            terminated = True
            
        # Time limit reached
        if self.current_step >= self.max_steps:
            terminated = True
            
        return self.state, reward, terminated, False, {}

    def render(self):
        print(f"Step: {self.current_step} | State: {self.state}")
