import numpy as np

# Agronomic Constants (Mitscherlich-Baule yield response equation)
# Reference: Mitscherlich, E. A. (1909) and Baule, B. (1918)
YMAX_DEFAULT = 8.5  # Potential max yield in t/ha
CN = 0.018  # Nitrogen response coefficient
CP = 0.025  # Phosphorus response coefficient
CK = 0.012  # Potassium response coefficient

def yield_response(N: float, P: float, K: float, dose_N: float, dose_P: float, dose_K: float, ymax: float = YMAX_DEFAULT) -> float:
    """
    Computes the yield response based on the Mitscherlich-Baule model.
    Takes existing soil nutrients and added fertilizer doses.
    """
    # Total available nutrients
    total_N = N + dose_N
    total_P = P + dose_P
    total_K = K + dose_K
    
    # Law of diminishing returns per nutrient
    response_N = 1 - np.exp(-CN * total_N)
    response_P = 1 - np.exp(-CP * total_P)
    response_K = 1 - np.exp(-CK * total_K)
    
    # The Mitscherlich-Baule synergy (product of responses)
    # This reflects the 'Law of the Minimum' but smoothed for synergism.
    yield_val = ymax * response_N * response_P * response_K
    return float(yield_val)

def compute_grid_yields(grid, fertilizer_grid: np.ndarray, ymax: float = YMAX_DEFAULT) -> np.ndarray:
    """
    Computes the yield for a full grid.
    'grid' should be a SoilGrid instance.
    'fertilizer_grid' should be shape (H, W, 3) where last dim is [N, P, K] dose.
    Returns (H, W) array of yields.
    """
    # Grid access (assuming SoilGrid structure)
    N_soil = grid.N
    P_soil = grid.P
    K_soil = grid.K
    
    # Fertilizer access
    dose_N = fertilizer_grid[:, :, 0]
    dose_P = fertilizer_grid[:, :, 1]
    dose_K = fertilizer_grid[:, :, 2]
    
    # Vectorized computation for NumPy performance
    total_N = N_soil + dose_N
    total_P = P_soil + dose_P
    total_K = K_soil + dose_K
    
    response_N = 1 - np.exp(-CN * total_N)
    response_P = 1 - np.exp(-CP * total_P)
    response_K = 1 - np.exp(-CK * total_K)
    
    yields = ymax * response_N * response_P * response_K
    return yields.astype(np.float32)

if __name__ == "__main__":
    # Test validation
    print(yield_response(50, 20, 100, 10, 5, 20))
