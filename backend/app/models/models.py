from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

"""
Data at Rest
"""


class QuarantineLog(Base):
    """
    Relational table for persistent safety audit trails.
    """

    __tablename__ = "quarantine_logs"

    id = Column(Integer, primary_key=True, index=True)
    wafer_id = Column(String, index=True)
    tool_id = Column(String)
    metric_name = Column(String)
    violation_value = Column(Float)
    threshold_limit = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_cleared = Column(Boolean, default=False)
