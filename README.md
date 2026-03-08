# ARZIS – Adaptive Root-Zone Intelligence System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-2023-%2320232a.svg?style=flat&logo=react)](https://reactjs.org/)

**ARZIS** is a cutting-edge, AI-powered agricultural optimization platform designed to maximize crop yield while minimizing fertilizer waste through precise, plant-level root-zone intelligence. 

By leveraging Reinforcement Learning (RL) and real-time environmental data, ARZIS provides farmers with actionable prescriptions for every individual plant in their field.

---

## 🌟 Key Features

### 🚜 Precision Root-Zone Heatmap
A dynamic, interactive 40x40 (or custom) plant grid representing your field. Each cell indicates individual plant health using real-time sensor data (N, P, K, pH, Moisture).
- **Green**: Healthy & Optimized
- **Yellow**: Moderate Nutrient Stress
- **Red**: Deficient - Needs Immediate Attention

### 🤖 AI Simulation Engine
Run advanced "what-if" scenarios. The ARZIS backend utilizes an RL Agent to simulate nutrient depletion and yield response, providing:
- **Fertilizer Prescriptions**: Exact kg/ha requirements per sector.
- **Ideal Water Ratios**: Dynamic adaptive irrigation levels based on soil saturation.
- **Yield Gain Forecasting**: Predict +12% to +18% improvements in harvest volume.

### 🧪 Bio-Metric Insights
AI-driven insights that analyze professional agricultural metrics:
- **Sun Rays Ratio**: Monitoring Photosynthetic Active Radiation (PAR).
- **Water Table Analysis**: Tracking subsurface water levels and retention.
- **Nutrient Balance**: Real-time N-P-K level monitoring.
- **Humidity & Transpiration**: Preventing fungal growth and optimizing crop breathability.

### 🌙 Premium UI/UX
- **Dark Mode**: High-contrast professional aesthetic for night-time field monitoring.
- **Responsive Simulation Settings**: Configure grid density, crop types (Corn, Wheat, etc.), and planting dates.
- **Real-time Transitions**: Smooth cross-fade animations and interactive "Wow" moments for demo presentations.

---

## 🛠️ Technology Stack

- **Frontend**: React (Vite), Tailwind CSS, Framer Motion, Axios, Lucide React.
- **Backend**: FastAPI (Python), SQLAlchemy, Pydantic.
- **Optimization**: NumPy, Reinforcement Learning (RL) Agents.
- **Database**: PostgreSQL (via Supabase) / SQLite for local development.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js & npm

### Backend Installation
1. Navigate to the root directory:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize the environment:
   ```bash
   python src/api.py
   ```
   *The API will start at `http://localhost:8000`*

### Frontend Installation
1. Navigate to the `frontend` directory:
   ```bash
   npm install
   npm run dev
   ```
   *The UI will start at `http://localhost:5173`*

---

## 📊 Analytics Controller
For advanced administrative monitoring, ARZIS includes a Streamlit-based controller:
```bash
streamlit run src/dashboard.py
```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---

**Developed for the Future of Sustainable Agriculture.**
*Empowering farmers with Plant-Level Intelligence.*

---
*Last Updated: 2026-03-08 | Build v1.2.5*
