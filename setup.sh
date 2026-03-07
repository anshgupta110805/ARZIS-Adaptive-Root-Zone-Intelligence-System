#!/bin/bash

# ARZIS Setup & Deployment Script
# ---------------------------------------------------------
# Adaptive Root-Zone Intelligence System (ARZIS)
# Project for 24-hour hackathon. Optimized from scratch.
# ---------------------------------------------------------

echo "Initializing ARZIS Project Structure..."
mkdir -p src models data logs

echo "Installing Dependency Stack..."
pip3 install -r requirements.txt

echo "Running Ground-Truth Validation (src/soil_grid.py)..."
python3 -c "from src.soil_grid import SoilGrid; g = SoilGrid(); print(g.to_dataframe().head()); print('Validation Result: OK (Grid Shape: ', g.N.shape, ')')"

echo "To launch the main dashboard, run:"
echo "streamlit run src/dashboard.py"

echo "To train the RL agent in the background, run:"
echo "python3 src/rl_trainer.py &"
