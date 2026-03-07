from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Profile base
class FarmerBase(BaseModel):
    name: str
    email: str
    phone: str

class FarmerCreate(FarmerBase):
    pass

class FarmerProfile(FarmerBase):
    id: int
    class Config:
        from_attributes = True

# Yield History
class YieldHistoryBase(BaseModel):
    year: int
    crop: str
    yield_tons_per_ha: float

class YieldHistoryResponse(YieldHistoryBase):
    id: int
    field_id: int
    class Config:
        from_attributes = True

# Field details
class FieldBase(BaseModel):
    name: str
    area_hectares: float
    crop_type: str
    latitude: float
    longitude: float
    soil_rating: str
    current_moisture_level: float

class FieldResponse(FieldBase):
    id: int
    farmer_id: int
    yield_history: List[YieldHistoryResponse] = []
    class Config:
        from_attributes = True

# Permissions/Settings
class UserPreferencesBase(BaseModel):
    moisture_alert_min: float = 30.0
    moisture_alert_max: float = 90.0
    ph_alert_min: float = 5.5
    ph_alert_max: float = 7.5
    irrigation_mode: str = "manual"
    daily_water_limit_liters: float = 10000.0
    theme: str = "dark"
    notification_method: str = "in-app"
    units: str = "metric"
    language: str = "en"
    grid_size: Optional[str] = "40x40"
    crop_type: Optional[str] = "Corn"
    planting_date: Optional[str] = "2024-03-01"

class UserPreferencesResponse(UserPreferencesBase):
    id: int
    farmer_id: int
    class Config:
        from_attributes = True

class UserPreferencesUpdate(BaseModel):
    moisture_alert_min: Optional[float] = None
    moisture_alert_max: Optional[float] = None
    ph_alert_min: Optional[float] = None
    ph_alert_max: Optional[float] = None
    irrigation_mode: Optional[str] = None
    daily_water_limit_liters: Optional[float] = None
    theme: Optional[str] = None
    notification_method: Optional[str] = None
    units: Optional[str] = None
    language: Optional[str] = None
    grid_size: Optional[str] = None
    crop_type: Optional[str] = None
    planting_date: Optional[str] = None

# Insights
class InsightLogBase(BaseModel):
    category: str
    observation: str
    recommendation: str
    expected_benefit: str
    severity: str

class InsightLogResponse(InsightLogBase):
    id: int
    field_id: int
    timestamp: datetime
    class Config:
        from_attributes = True
