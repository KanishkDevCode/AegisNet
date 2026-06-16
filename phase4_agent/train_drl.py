import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from aegis_battle_sim import AegisBattleSim

def train_agent():
    print("Initializing AegisBattleSim Environment...")
    env = AegisBattleSim()
    
    # Verify the custom environment follows the Gymnasium API
    check_env(env, warn=True)
    
    print("\nTraining Deep Reinforcement Learning Agent (PPO)...")
    print("The agent is learning how to stop lateral movement on our Phase 3 Graph.")
    
    # Initialize PPO Agent
    model = PPO("MlpPolicy", env, verbose=1)
    
    # Train for 50,000 timesteps (Simulated cyber attacks)
    model.learn(total_timesteps=50000)
    
    # Save the trained model
    os.makedirs("outputs", exist_ok=True)
    model_path = "outputs/aegis_ppo_agent"
    model.save(model_path)
    print(f"\n[SUCCESS] Agent successfully trained and saved to {model_path}.zip!")

def test_agent():
    print("\n--- Running a Simulation with the Trained Agent ---")
    env = AegisBattleSim()
    model = PPO.load("outputs/aegis_ppo_agent")
    
    obs, _ = env.reset()
    print(f"Initial State (0=Clean, 1=Infected, 2=Isolated): {obs}")
    
    done = False
    while not done:
        # The AI decides which server to firewall off
        action, _states = model.predict(obs, deterministic=True)
        print(f"Agent Action: Isolate Node {action}")
        
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"New State: {obs} | Reward: {reward}")
        
        done = terminated or truncated

if __name__ == "__main__":
    train_agent()
    test_agent()
