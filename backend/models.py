from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class TelemetryData(BaseModel):
    timestamp: datetime
    tool_id: str
    wafer_id: str
    metrics: Dict[str, float]
    status: str
    location: str
