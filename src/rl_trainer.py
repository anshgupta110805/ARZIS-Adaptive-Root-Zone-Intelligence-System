import os
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from rl_env import ARZISEnv

# --- Training Setup ---
LOG_DIR = "./logs/"
MODEL_DIR = "./models/"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

def train():
    """
    Trains a PPO agent for agricultural fertilizer optimization.
    The agent learns to balance yield vs cost in a sequence-aware environment.
    """
    print("--- Initializing ARZIS RL Training Environment ---")
    env = ARZISEnv()
    
    # Configure PPO: Multi-layer Perceptron Policy
    # We use a standard architecture optimized for speed in a hackathon setting.
    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        device="auto"
    )
    
    # Checkpoint Callback to save model progress
    checkpoint_callback = CheckpointCallback(
        save_freq=1000, 
        save_path=MODEL_DIR,
        name_prefix="arzis_ppo_model"
    )
    
    print(f"Goal: Optimize NPK dosage for {env.total_plants} plants sequentially.")
    print("Starting Learning Loop...")
    
    try:
        # Train for a small number of steps for demo purposes
        # In a real scenario, we'd aim for 100k+ timesteps
        model.learn(
            total_timesteps=10000, 
            callback=checkpoint_callback,
            progress_bar=True
        )
        
        # Save the final optimized model
        model.save(os.path.join(MODEL_DIR, "arzis_optimized_v1"))
        print(f"Training Complete. Final model saved to {MODEL_DIR}")
        
    except KeyboardInterrupt:
        print("Training Interrupted. Saving current checkpoint...")
        model.save(os.path.join(MODEL_DIR, "arzis_interrupted_model"))

if __name__ == "__main__":
    train()
