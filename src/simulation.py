import numpy as np
from soil_grid import SoilGrid
from yield_model import yield_response, YMAX_DEFAULT

def run_simulation(seed=42, grid_size=50, ymax=YMAX_DEFAULT, baseline_dose=60.0):
    """
    Core simulation engine for ARZIS.
    Returns: Baseline, ARZIS decision grid, layers, and KPIs.
    """
    grid = SoilGrid(size=grid_size, seed=seed)
    size = grid_size

    # Layer Pre-calculation
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    xx, yy = np.meshgrid(x, y)
    sunlight_map = np.clip(1.0 - (np.sqrt(xx**2 + yy**2) / np.sqrt(2)), 0.2, 1.0).astype(np.float32)
    water_map = (grid.moisture / 80.0).astype(np.float32)

    # 1. Baseline Simulation (Flat Rate)
    # Using vectorize for some speed, or just nested loops for clarity to match dashboard logic perfectly
    baseline_yields = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            y_val = yield_response(grid.N[i, j], grid.P[i, j], grid.K[i, j], 
                                   baseline_dose, baseline_dose, baseline_dose, ymax=ymax)
            baseline_yields[i, j] = y_val * water_map[i, j] * sunlight_map[i, j]

    # 2. ARZIS Simulation (Sequential with Depletion)
    arzis_yields = np.zeros((size, size), dtype=np.float32)
    doses_applied = np.zeros((size, size, 3), dtype=np.float32)
    cumulative_sum = np.zeros(3, dtype=np.float32)
    depletion_history = np.zeros((size, size), dtype=np.float32) 

    for r in range(size):
        for c in range(size):
            # Available Context (Budget Logic)
            avail_n = np.clip(grid.N[r, c] - (cumulative_sum[0] / 100.0), 0, 300)
            avail_p = np.clip(grid.P[r, c] - (cumulative_sum[1] / 100.0), 0, 300)
            avail_k = np.clip(grid.K[r, c] - (cumulative_sum[2] / 100.0), 0, 300)
            
            # Rule-based ARZIS Agent Proxy
            dose_n = np.clip(100.0 - avail_n, 5, 50)
            dose_p = np.clip(60.0 - avail_p, 5, 50)
            dose_k = np.clip(120.0 - avail_k, 5, 50)
            
            dose = np.array([dose_n, dose_p, dose_k], dtype=np.float32)
            doses_applied[r, c] = dose
            depletion_history[r, c] = np.sum(cumulative_sum)
            
            y_val = yield_response(avail_n, avail_p, avail_k, dose_n, dose_p, dose_k, ymax=ymax)
            arzis_yields[r, c] = y_val * water_map[r, c] * sunlight_map[r, c]
            
            cumulative_sum += dose

    # Stats / KPIs
    b_avg = float(np.mean(baseline_yields))
    a_avg = float(np.mean(arzis_yields))
    delta_yield = ((a_avg - b_avg) / b_avg) * 100 if b_avg > 0 else 0
    total_baseline_fert = (baseline_dose * 3) * size * size
    total_arzis_fert = float(np.sum(doses_applied))
    savings = ((total_baseline_fert - total_arzis_fert) / total_baseline_fert) * 100 if total_baseline_fert > 0 else 0

    return {
        "metadata": {
            "grid_size": size,
            "seed": seed,
            "ymax": ymax
        },
        "soil_data": {
            "N": grid.N.tolist(),
            "P": grid.P.tolist(),
            "K": grid.K.tolist(),
            "Mg": grid.Mg.tolist(),
            "pH": grid.pH.tolist(),
            "moisture": grid.moisture.tolist()
        },
        "layers": {
            "sunlight": sunlight_map.tolist(),
            "water": water_map.tolist(),
            "depletion": depletion_history.tolist()
        },
        "results": {
            "baseline_yield": baseline_yields.tolist(),
            "arzis_yield": arzis_yields.tolist(),
            "doses": doses_applied.tolist(),
        },
        "kpis": {
            "baseline_avg": b_avg,
            "arzis_avg": a_avg,
            "delta_yield_pct": delta_yield,
            "fert_savings_pct": savings,
            "plants_optimized": size * size
        }
    }
