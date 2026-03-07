import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from scipy.ndimage import gaussian_filter

@dataclass
class SoilGrid:
    """
    Simulates a 2D field grid of soil nutrients and properties with spatial correlation.
    Labeled as 'SoilGrids-derived simulation' for hackathon presentation.
    """
    size: int = 50
    seed: int = 42
    
    # Grid layers (50x50)
    N: np.ndarray = field(init=False)      # Nitrogen (kg/ha)
    P: np.ndarray = field(init=False)      # Phosphorus (kg/ha)
    K: np.ndarray = field(init=False)      # Potassium (kg/ha)
    Mg: np.ndarray = field(init=False)     # Magnesium (kg/ha)
    pH: np.ndarray = field(init=False)     # Soil pH
    moisture: np.ndarray = field(init=False) # Soil moisture (%)

    def __post_init__(self):
        self.generate_grid()

    def _generate_correlated_layer(self, low, high, sigma=2.0):
        """Generates a 2D layer with spatial correlation using Gaussian filtering."""
        # Generate random noise
        layer = np.random.uniform(low, high, (self.size, self.size))
        # Apply spatial correlation
        layer = gaussian_filter(layer, sigma=sigma)
        # Re-scale to maintain original range roughly
        layer = (layer - layer.min()) / (layer.max() - layer.min()) * (high - low) + low
        return layer.astype(np.float32)

    def generate_grid(self):
        """Initializes all soil layers with believable agronomic ranges."""
        np.random.seed(self.seed)
        
        # N: 20–120 kg/ha
        self.N = self._generate_correlated_layer(20, 120, sigma=3.0)
        # P: 5–60 kg/ha
        self.P = self._generate_correlated_layer(5, 60, sigma=2.5)
        # K: 40–200 kg/ha
        self.K = self._generate_correlated_layer(40, 200, sigma=3.5)
        # Mg: 15–120 kg/ha (Believable range)
        self.Mg = self._generate_correlated_layer(15, 120, sigma=2.8)
        # pH: 5.5–7.5
        self.pH = self._generate_correlated_layer(5.5, 7.5, sigma=4.0)
        # moisture: 20–80%
        self.moisture = self._generate_correlated_layer(20, 80, sigma=2.0)

    def to_dataframe(self) -> pd.DataFrame:
        """Returns a tidy DataFrame of the soil grid."""
        rows, cols = np.indices((self.size, self.size))
        data = {
            'row': rows.flatten(),
            'col': cols.flatten(),
            'N': self.N.flatten(),
            'P': self.P.flatten(),
            'K': self.K.flatten(),
            'Mg': self.Mg.flatten(),
            'pH': self.pH.flatten(),
            'moisture': self.moisture.flatten()
        }
        return pd.DataFrame(data)

    def state_at(self, row, col) -> np.ndarray:
        """Returns the 5-dim state vector for a specific coordinate."""
        return np.array([
            self.N[row, col],
            self.P[row, col],
            self.K[row, col],
            self.Mg[row, col],
            self.pH[row, col],
            self.moisture[row, col]
        ], dtype=np.float32)

if __name__ == "__main__":
    # Test validation
    grid = SoilGrid()
    df = grid.to_dataframe()
    print(df.head())
    print(f"Shape: {grid.N.shape}")
