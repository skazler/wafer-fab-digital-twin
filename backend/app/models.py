from pydantic import BaseModel
from datetime import datetime
from typing import Dict
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class TelemetryData(BaseModel):
    timestamp: datetime
    tool_id: str
    wafer_id: str
    metrics: Dict[str, float]
    status: str
    location: str

class QuarantineLog(Base):
    """
    Tracks wafers that have triggered a safety interlock.
    """
    __tablename__ = "quarantine_logs"

    id = Column(Integer, primary_key=True, index=True)
    wafer_id = Column(String, index=True)
    tool_id = Column(String)
    metric_name = Column(String)  # e.g. "Temperature"
    violation_value = Column(Float)
    threshold_limit = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_cleared = Column(Boolean, default=False) # has an engineer checked this?