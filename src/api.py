import os
import uvicorn
import numpy as np
from datetime import datetime
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from simulation import run_simulation
from database import SessionLocal, init_db, Farmer, Field, YieldHistory, UserPreferences, InsightLog
import schemas

# RL Model (optional – gracefully degrade if unavailable)
rl_model = None
try:
    from stable_baselines3 import PPO
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "arzis_optimized_v1.zip")
    if os.path.exists(MODEL_PATH):
        rl_model = PPO.load(MODEL_PATH)
except Exception:
    pass

# Initialize DB
init_db()

# Seed mock data on first run
from db_init import populate_mock_data
populate_mock_data()

app = FastAPI(title="ARZIS Backend Service", description="Adaptive Root-Zone Intelligence System API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Health ---
@app.get("/")
def read_root():
    return {"status": "ARZIS API is online", "version": "1.1.0", "rl_model_loaded": rl_model is not None}

# --- Simulation ---
@app.get("/field/simulation")
def get_field_simulation(
    seed: int = Query(42),
    grid_size: int = Query(50),
    ymax: float = Query(8.5),
    baseline_dose: float = Query(60.0)
):
    try:
        return run_simulation(seed=seed, grid_size=grid_size, ymax=ymax, baseline_dose=baseline_dose)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Customer ---
@app.get("/customer/{farmer_id}", response_model=schemas.FarmerProfile)
def get_customer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer

# --- Field Details ---
@app.get("/field/{field_id}/details", response_model=schemas.FieldResponse)
def get_field_details(field_id: int, db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field

# --- Preferences ---
@app.get("/preferences/{farmer_id}", response_model=schemas.UserPreferencesResponse)
def get_preferences(farmer_id: int, db: Session = Depends(get_db)):
    prefs = db.query(UserPreferences).filter(UserPreferences.farmer_id == farmer_id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return prefs

@app.patch("/customize/{farmer_id}", response_model=schemas.UserPreferencesResponse)
def update_preferences(farmer_id: int, pref_update: schemas.UserPreferencesUpdate, db: Session = Depends(get_db)):
    prefs = db.query(UserPreferences).filter(UserPreferences.farmer_id == farmer_id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    update_data = pref_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prefs, key, value)
    db.commit()
    db.refresh(prefs)
    return prefs

# --- Insights ---
@app.get("/insights", response_model=List[schemas.InsightLogResponse])
def get_insights(
    seed: int = Query(42),
    grid_size: int = Query(50),
    farmer_id: int = Query(1),
    db: Session = Depends(get_db)
):
    prefs = db.query(UserPreferences).filter(UserPreferences.farmer_id == farmer_id).first()
    try:
        state = run_simulation(seed=seed, grid_size=grid_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    insights = []
    now = datetime.utcnow()

    soil_N = np.array(state["soil_data"]["N"])
    soil_P = np.array(state["soil_data"]["P"])
    soil_K = np.array(state["soil_data"]["K"])
    soil_moisture = np.array(state["soil_data"]["moisture"])
    soil_pH = np.array(state["soil_data"]["pH"])
    soil_Mg = np.array(state["soil_data"]["Mg"])

    avg_moisture = float(np.mean(soil_moisture))
    avg_pH = float(np.mean(soil_pH))
    avg_P = float(np.mean(soil_P))
    avg_Mg = float(np.mean(soil_Mg))
    k_min = float(np.min(soil_K))
    avg_K = float(np.mean(soil_K))
    kpis = state["kpis"]
    insight_id = 1

    # 1. Moisture
    if prefs and avg_moisture < prefs.moisture_alert_min:
        insights.append(schemas.InsightLogResponse(
            id=insight_id, field_id=1, timestamp=now,
            category="Water Optimization",
            observation=f"Average field moisture is {avg_moisture:.1f}%, below alert threshold of {prefs.moisture_alert_min}%.",
            recommendation="Initiate emergency drip-irrigation cycle focusing on Sectors B and C.",
            expected_benefit="+15% Nutrient mobility improvement",
            severity="high"
        ))
        insight_id += 1
    elif prefs and avg_moisture > prefs.moisture_alert_max:
        insights.append(schemas.InsightLogResponse(
            id=insight_id, field_id=1, timestamp=now,
            category="Irrigation Efficiency",
            observation=f"Field moisture ({avg_moisture:.1f}%) exceeds maximum threshold.",
            recommendation="Pause upcoming scheduled irrigation to prevent root rot & nutrient leaching.",
            expected_benefit="-12% Over-watering waste",
            severity="medium"
        ))
        insight_id += 1

    # 2. pH
    if prefs and avg_pH < prefs.ph_alert_min:
        insights.append(schemas.InsightLogResponse(
            id=insight_id, field_id=1, timestamp=now,
            category="Soil Acidity",
            observation=f"Average pH dropped to {avg_pH:.2f}, below safe threshold ({prefs.ph_alert_min}).",
            recommendation="Apply granular lime at 200kg/ha to neutralize acidity.",
            expected_benefit="+18% Phosphorus availability",
            severity="high"
        ))
        insight_id += 1

    # 3. Sun Rays Ratio
    insights.append(schemas.InsightLogResponse(
        id=insight_id, field_id=1, timestamp=now,
        category="Sun Rays Ratio",
        observation="Photosynthetic Active Radiation (PAR) is at 850 µmol/m²/s. Optimal for growth.",
        recommendation="No shade intervention required. Monitor daily UV index peaks.",
        expected_benefit="+12% Photosynthesis efficiency",
        severity="low"
    ))
    insight_id += 1

    # 4. Phosphorus
    if avg_P < 25:
        insights.append(schemas.InsightLogResponse(
            id=insight_id, field_id=1, timestamp=now,
            category="Crop Performance",
            observation=f"Phosphorus levels averaging {avg_P:.1f} mg/kg — suboptimal for root development.",
            recommendation="Apply DAP (Di-Ammonium Phosphate) at 40kg/ha at planting.",
            expected_benefit="+12% Root biomass and nutrient uptake",
            severity="medium"
        ))
        insight_id += 1

    # 5. Magnesium surplus
    if avg_Mg > 80:
        insights.append(schemas.InsightLogResponse(
            id=insight_id, field_id=1, timestamp=now,
            category="Magnesium Levels",
            observation=f"80% of fields show Mg surplus ({avg_Mg:.1f} mg/kg). Over-application risk.",
            recommendation="Reduce Mg-based fertilizer by 30% to save costs without yield loss.",
            expected_benefit="$2,000+ annual fertilizer savings",
            severity="low"
        ))
        insight_id += 1

    # 6. Water Level
    insights.append(schemas.InsightLogResponse(
        id=insight_id, field_id=1, timestamp=now,
        category="Water Level",
        observation=f"Current water table is stable at -1.2m. Soil saturation at {avg_moisture:.1f}%.",
        recommendation="Adjust irrigation schedule to early morning hours to minimize evaporation.",
        expected_benefit="+5% Water retention efficiency",
        severity="low"
    ))
    insight_id += 1

    # 7. Nutrient Level
    avg_N = float(np.mean(soil_N))
    insights.append(schemas.InsightLogResponse(
        id=insight_id, field_id=1, timestamp=now,
        category="Nutrient Level",
        observation=f"Overall Nitrogen levels are at {avg_N:.1f} mg/kg. Nutrient balance is healthy.",
        recommendation="Continue current fertilization plan. Monitor for leaching after 5 days.",
        expected_benefit="Stable growth trajectory",
        severity="low"
    ))
    insight_id += 1

    # 8. Humidity Level
    humidity = 68.5 
    insights.append(schemas.InsightLogResponse(
        id=insight_id, field_id=1, timestamp=now,
        category="Humidity Level",
        observation=f"Relative humidity is {humidity}%. Ideal range for crop transpiration.",
        recommendation="Maintain ventilation levels (if indoors) or monitor dew points.",
        expected_benefit="Prevent fungal growth",
        severity="low"
    ))
    insight_id += 1

    return insights

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
