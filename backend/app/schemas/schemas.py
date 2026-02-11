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
    GAS_FLOW = "gas_flow"


class RootCauseType(str, Enum):
    NORMAL = "NORMAL_OPERATION"
    THERMAL_RUNAWAY = "THERMAL_RUNAWAY"
    SENSORY_DRIFT = "SENSORY_DRIFT"
    SYSTEM_INSTABILITY = "SYSTEM_INSTABILITY"


class ActionType(str, Enum):
    MONITOR = "MONITOR_STABILITY"
    REDUCE_POWER = "REDUCE_HEATER_POWER_50"
    INCREASE_COOLANT = "INCREASE_COOLANT_FLOW"
    EMERGENCY_STOP = "EMERGENCY_STOP_REQUIRED"


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


class PredictionResponse(BaseModel):
    remaining_life_seconds: float | None = None
    is_drifting: bool
    root_cause: RootCauseType
    reason: str
    recommended_action: ActionType


class TelemetryProcessResponse(BaseModel):
    status: str
    wafer_id: str
    interlock_active: bool
    predictions: PredictionResponse
