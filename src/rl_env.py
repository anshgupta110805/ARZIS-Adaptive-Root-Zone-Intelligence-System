import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os

# Relative imports handling
try:
    from .soil_grid import SoilGrid
    from .yield_model import yield_response
except ImportError:
    from soil_grid import SoilGrid
    from yield_model import yield_response

class ARZISEnv(gym.Env):
    """
    ARZIS (Adaptive Root-Zone Intelligence System) Environment.
    Optimizes NPK dosage per plant with a sequence-aware layer system.
    """
    def __init__(self, soil=None):
        super(ARZISEnv, self).__init__()
        self.size = 50
        self.total_plants = self.size * self.size
        self.soil = soil if soil is not None else SoilGrid(size=self.size)
        
        # Observation Space (Locked to 5 dimensions per validation requirement)
        # Dimensions: [Available_N, Available_P, Available_K, Water_Context, Sunlight_Context]
        # 'Available' includes the depletion/drawdown logic.
        self.observation_space = spaces.Box(
            low=0.0, high=300.0, shape=(5,), dtype=np.float32
        )
        
        # Action Space: [dose_N, dose_P, dose_K] kg/ha
        self.action_space = spaces.Box(
            low=0.0, high=50.0, shape=(3,), dtype=np.float32
        )
        
        # Layer System Initialization
        self._init_layers()
        
        self.curr_idx = 0
        self.cumulative_doses = np.zeros(3, dtype=np.float32)

    def _init_layers(self):
        """Initializes sunlight and water layers."""
        x = np.linspace(-1, 1, self.size)
        y = np.linspace(-1, 1, self.size)
        xx, yy = np.meshgrid(x, y)
        # Sunlight: 0 to 1, darkest at field edges (circular falloff)
        dist = np.sqrt(xx**2 + yy**2)
        self.sunlight_layer = np.clip(1.0 - (dist / np.sqrt(2)), 0.2, 1.0).astype(np.float32)
        
        # Water availability: normalized 0-1 from moisture
        self.water_layer = (self.soil.moisture / 80.0).astype(np.float32)
        
        # Depletion tracking (cumulative)
        self.depletion_val = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.soil = SoilGrid(size=self.size, seed=seed)
            self._init_layers()
        
        self.curr_idx = 0
        self.cumulative_doses = np.zeros(3, dtype=np.float32)
        
        return self._get_obs(), {}

    def _get_obs(self):
        row = self.curr_idx // self.size
        col = self.curr_idx % self.size
        
        # Available nutrients = Initial - Cumulative Doses Applied (Budget model)
        # Note: We divide the cumulative field-wide dose by a scaling factor to keep observation in [0, 300]
        # or we just model it as a field-wide 'tank' depletion.
        # Following prompt: "available_nutrient = initial_nutrient - cumulative_doses_applied"
        avail_n = np.clip(self.soil.N[row, col] - (self.cumulative_doses[0] / 100.0), 0, 300)
        avail_p = np.clip(self.soil.P[row, col] - (self.cumulative_doses[1] / 100.0), 0, 300)
        avail_k = np.clip(self.soil.K[row, col] - (self.cumulative_doses[2] / 100.0), 0, 300)
        
        water = self.water_layer[row, col]
        sun = self.sunlight_layer[row, col]
        
        return np.array([avail_n, avail_p, avail_k, water, sun], dtype=np.float32)

    def step(self, action):
        row = self.curr_idx // self.size
        col = self.curr_idx % self.size
        
        # Current plant state
        obs = self._get_obs()
        n_avail, p_avail, k_avail, water_mult, sun_mult = obs
        
        # Action is [dose_N, dose_P, dose_K]
        dose_n, dose_p, dose_k = action
        
        # Update cumulative drawdown
        self.cumulative_doses += action
        
        # Yield calculation with layer multipliers
        # Water and sunlight act as uptake efficiency multipliers
        base_yield = yield_response(n_avail, p_avail, k_avail, dose_n, dose_p, dose_k)
        actual_yield = base_yield * water_mult * sun_mult
        
        # Reward: Yield - Fertilizer Cost
        cost = 0.01 * np.sum(action)
        reward = actual_yield - cost
        
        self.curr_idx += 1
        terminated = self.curr_idx >= self.total_plants
        truncated = False
        
        next_obs = self._get_obs() if not terminated else np.zeros((5,), dtype=np.float32)
        
        info = {
            "yield": actual_yield,
            "row": row,
            "col": col,
            "sunlight": sun_mult,
            "water": water_mult
        }
        
        return next_obs, float(reward), terminated, truncated, info

if __name__ == "__main__":
    # Test validation
    env = ARZISEnv()
    obs, info = env.reset()
    print('Obs shape:', obs.shape)
    print('Obs sample:', obs)
