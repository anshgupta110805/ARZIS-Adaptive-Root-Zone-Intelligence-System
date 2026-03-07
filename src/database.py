import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Use Supabase PostgreSQL if provided, otherwise fallback to SQLite
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./arzis_data.db"
)

# SQLite needs check_same_thread=False, PostgreSQL doesn't
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Models ---
class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    
    fields = relationship("Field", back_populates="owner")
    preferences = relationship("UserPreferences", back_populates="farmer", uselist=False)

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    name = Column(String)
    area_hectares = Column(Float)
    crop_type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    soil_rating = Column(String)
    current_moisture_level = Column(Float)
    
    owner = relationship("Farmer", back_populates="fields")
    yield_history = relationship("YieldHistory", back_populates="field")

class YieldHistory(Base):
    __tablename__ = "yield_history"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"))
    year = Column(Integer)
    crop = Column(String)
    yield_tons_per_ha = Column(Float)
    
    field = relationship("Field", back_populates="yield_history")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), unique=True)
    moisture_alert_min = Column(Float, default=30.0)
    moisture_alert_max = Column(Float, default=90.0)
    ph_alert_min = Column(Float, default=5.5)
    ph_alert_max = Column(Float, default=7.5)
    irrigation_mode = Column(String, default="manual") # auto/manual
    daily_water_limit_liters = Column(Float, default=10000.0)
    theme = Column(String, default="dark")
    notification_method = Column(String, default="in-app") # email/sms/in-app
    units = Column(String, default="metric")
    language = Column(String, default="en")
    grid_size = Column(String, default="40x40")
    crop_type = Column(String, default="Corn")
    planting_date = Column(String, default="2024-03-01")

    farmer = relationship("Farmer", back_populates="preferences")

class InsightLog(Base):
    __tablename__ = "insight_logs"
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"))
    category = Column(String)
    observation = Column(String)
    recommendation = Column(String)
    expected_benefit = Column(String)
    severity = Column(String) # low, medium, high
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
