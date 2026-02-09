from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict
from enum import Enum

"""
Data in Transit
"""


class MetricType(str, Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VIBRATION = "vibration"


class TelemetryData(BaseModel):
    timestamp: datetime
    tool_id: str
    wafer_id: str
    metrics: Dict[MetricType, float]
    status: str
    location: str


class QuarantineResponse(BaseModel):
    id: int
    wafer_id: str
    tool_id: str
    metric_name: MetricType
    violation_value: float
    timestamp: datetime
    is_cleared: bool
    model_config = ConfigDict(from_attributes=True)
