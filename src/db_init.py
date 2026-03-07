import os
from database import engine, Base, SessionLocal, Farmer, Field, YieldHistory, UserPreferences, init_db
from datetime import datetime

def populate_mock_data():
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Farmer).first():
        print("Database already populated. Skipping initialization.")
        db.close()
        return

    print("Populating minimal mock data for the Farmer Profile...")

    # Farmer
    farmer = Farmer(
        name="John Doe",
        email="john.doe@farmtech.io",
        phone="+1 555-0198"
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)

    # Field
    field = Field(
        farmer_id=farmer.id,
        name="Sector A - North",
        area_hectares=150.0,
        crop_type="Corn",
        latitude=41.8781,
        longitude=-87.6298,
        soil_rating="Excellent",
        current_moisture_level=65.4
    )
    db.add(field)
    db.commit()
    db.refresh(field)

    # Yield Histories
    history1 = YieldHistory(field_id=field.id, year=2024, crop="Corn", yield_tons_per_ha=11.2)
    history2 = YieldHistory(field_id=field.id, year=2023, crop="Soybeans", yield_tons_per_ha=4.5)
    history3 = YieldHistory(field_id=field.id, year=2022, crop="Corn", yield_tons_per_ha=10.8)
    db.add_all([history1, history2, history3])

    # Preferences
    prefs = UserPreferences(
        farmer_id=farmer.id,
        moisture_alert_min=30.0,
        moisture_alert_max=90.0,
        ph_alert_min=5.5,
        ph_alert_max=7.5,
        irrigation_mode="auto",
        daily_water_limit_liters=10000.0,
        theme="dark",
        notification_method="in-app",
        units="metric",
        language="en"
    )
    db.add(prefs)
    
    db.commit()
    db.close()
    print("Mock data setup complete.")

if __name__ == "__main__":
    init_db()
    populate_mock_data()
