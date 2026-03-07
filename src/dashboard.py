import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
import requests
from soil_grid import SoilGrid
from yield_model import yield_response, compute_grid_yields

# --- Configuration & Cache ---
st.set_page_config(page_title="ARZIS Dashboard", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main {
    background: #0d1117;
    color: #c9d1d9;
}
div[data-testid="stMetricValue"] {
    color: #4cd964;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_grid(seed, size):
    return SoilGrid(size=size, seed=seed)

# --- Sidebar ---
st.sidebar.title("🌱 ARZIS Control")

st.sidebar.subheader("📐 Field Configuration")
grid_size_val = st.sidebar.slider("Simulation Grid Size", 20, 100, 50)
seed = st.sidebar.slider("Field Random Seed", 1, 100, 42)

st.sidebar.subheader("🌾 Yield Configuration")
ymax_val = st.sidebar.slider("Max Potential Yield (t/ha)", 5.0, 20.0, 8.5)
baseline_dose_val = st.sidebar.slider("Flat Fertilizer Dose (kg/ha)", 0, 100, 60)

# --- Data Generation ---
size = grid_size_val
grid = get_grid(seed, size)

# Pre-calculate layers (as in ARZISEnv)
x = np.linspace(-1, 1, size)
y = np.linspace(-1, 1, size)
xx, yy = np.meshgrid(x, y)
sunlight_map = np.clip(1.0 - (np.sqrt(xx**2 + yy**2) / np.sqrt(2)), 0.2, 1.0)
water_map = (grid.moisture / 80.0)

# 1. Baseline Simulation (Flat Rate)
baseline_yields = np.zeros((size, size))
for i in range(size):
    for j in range(size):
        y_val = yield_response(grid.N[i, j], grid.P[i, j], grid.K[i, j], 
                               baseline_dose_val, baseline_dose_val, baseline_dose_val, ymax=ymax_val)
        baseline_yields[i, j] = y_val * water_map[i, j] * sunlight_map[i, j]

# 2. ARZIS Simulation (Sequential with Depletion)
arzis_yields = np.zeros((size, size))
doses_applied = np.zeros((size, size, 3))
cumulative_sum = np.zeros(3)
depletion_history = np.zeros((size, size)) 

for r in range(size):
    for c in range(size):
        # Current Available (Initial - Global Depletion)
        avail_n = np.clip(grid.N[r, c] - (cumulative_sum[0] / 100.0), 0, 300)
        avail_p = np.clip(grid.P[r, c] - (cumulative_sum[1] / 100.0), 0, 300)
        avail_k = np.clip(grid.K[r, c] - (cumulative_sum[2] / 100.0), 0, 300)
        
        # Rule-based ARZIS Agent
        dose_n = np.clip(100.0 - avail_n, 5, 50)
        dose_p = np.clip(60.0 - avail_p, 5, 50)
        dose_k = np.clip(120.0 - avail_k, 5, 50)
        
        dose = np.array([dose_n, dose_p, dose_k])
        doses_applied[r, c] = dose
        depletion_history[r, c] = np.sum(cumulative_sum)
        
        y_val = yield_response(avail_n, avail_p, avail_k, dose_n, dose_p, dose_k, ymax=ymax_val)
        arzis_yields[r, c] = y_val * water_map[r, c] * sunlight_map[r, c]
        
        cumulative_sum += dose

# --- Layout ---
# Interactive Avatar Header & Chat
st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
    <div style="font-size: 50px;">🧑‍�</div>
    <div>
        <h1 style="margin: 0; padding: 0;">YieldAI Agronomist</h1>
        <p style="margin: 0; padding: 0; color: #888;">Your adaptive interactive avatar connecting to the backend intelligence.</p>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Show previous chat messages
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"], avatar="🧑‍🌾" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Chat Input & Server call
if prompt := st.chat_input("Ask about fertilizer savings, soil alerts, or field insights..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    try:
        # Connect to the FastAPI backend server for insights
        res = requests.get(f"http://localhost:8000/insights?seed={seed}&grid_size={size}&farmer_id=1", timeout=5)
        if res.status_code == 200:
            insights = res.json()
            if not insights:
                bot_reply = "Your field looks healthy! I don't see any immediate alerts right now."
            else:
                bot_reply = "Here's the latest intelligence from our models:\n"
                for idx, inc in enumerate(insights[:3]):
                    bot_reply += f"**{idx+1}. {inc.get('category')}**: {inc.get('observation')} *{inc.get('recommendation')}*\n\n"
        else:
            bot_reply = f"Error from backend API: Status {res.status_code}"
    except Exception as e:
        bot_reply = "I couldn't reach the backend server (`localhost:8000`). Please ensure it's running!"

    with st.chat_message("assistant", avatar="🧑‍🌾"):
        st.markdown(bot_reply)
    st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})

st.markdown("---")

# KPIs
k1, k2, k3, k4 = st.columns(4)
b_avg = np.mean(baseline_yields)
a_avg = np.mean(arzis_yields)
delta_y = ((a_avg - b_avg) / b_avg) * 100 if b_avg > 0 else 0
savings = ((np.sum(baseline_dose_val * 3) * size * size - np.sum(doses_applied)) / (np.sum(baseline_dose_val * 3) * size * size)) * 100 if baseline_dose_val > 0 else 0

k1.metric("Baseline Yield", f"{b_avg:.2f} t/ha")
k2.metric("ARZIS Yield", f"{a_avg:.2f} t/ha", delta=f"{delta_y:.1f}%")
k3.metric("Fertilizer Savings", f"{savings:.1f}%")
k4.metric(f"Plants Optimized", f"{size*size:,}/{size*size:,}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Soil Nutrient Map", "Yield Comparison", "ARZIS Decisions", "System Layers"])

with tab1:
    layer = st.selectbox("Nutrient Layer", ["N", "P", "K", "pH"])
    map_data = {"N": grid.N, "P": grid.P, "K": grid.K, "pH": grid.pH}[layer]
    fig1 = px.imshow(map_data, color_continuous_scale="Viridis", template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.markdown("#### Baseline (Flat) vs ARZIS (Optimized)")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Baseline Heatmap")
        st.plotly_chart(px.imshow(baseline_yields, color_continuous_scale="YlGn", zmin=0, zmax=ymax_val, template="plotly_dark"), use_container_width=True)
    with c2:
        st.caption("ARZIS Heatmap")
        st.plotly_chart(px.imshow(arzis_yields, color_continuous_scale="YlGn", zmin=0, zmax=ymax_val, template="plotly_dark"), use_container_width=True)

with tab3:
    imp = ((arzis_yields - baseline_yields) / (baseline_yields + 1e-6)) * 100
    st.subheader("Yield Improvement (%) Discovery Map")
    fig3 = px.imshow(imp, color_continuous_scale="RdYlGn", zmin=-5, zmax=30, template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Multi-Layer Perception Context")
    la, lb = st.columns(2)
    lc, ld = st.columns(2)
    
    with la:
        st.caption("Water Availability (Uptake Efficiency)")
        st.plotly_chart(px.imshow(water_map, color_continuous_scale="Blues", zmin=0, zmax=1, template="plotly_dark"), use_container_width=True)
    with lb:
        st.caption("Sunlight Exposure (Synthetic Canopy)")
        st.plotly_chart(px.imshow(sunlight_map, color_continuous_scale="Hot", zmin=0, zmax=1, template="plotly_dark"), use_container_width=True)
    with lc:
        st.caption("Soil Nutrient Depletion (Cumulative Drawdown)")
        st.plotly_chart(px.imshow(depletion_history, color_continuous_scale="OrRd", template="plotly_dark"), use_container_width=True)
    with ld:
        st.markdown(f"""
        **Layer Influence Legend:**
        - **Water (Normalized):** High moisture improves nutrient mobility. Directly affects yield scaling.
        - **Sunlight (Normalized):** Central canopy exposure vs. shaded field edges. Directly scales photosynthetic potential.
        - **Depletion (kg/ha):** Cumulative fertilizer footprint. Affects 'Available' nutrient state for {size*size} plants.
        """)

st.caption("Labelling: SoilGrids-derived simulation | Adaptive Root-Zone Intelligence System (ARZIS) | Optimized for 2026 Hackathon Finals")
