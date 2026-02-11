from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict

from app.models.models import QuarantineLog
from app.schemas.schemas import (
    TelemetryData,
    MetricType,
    PredictionResponse,
    RootCauseType,
    ActionType,
)
from app.services.spc_service import SPCService
from app.services.pdm_service import PdmService
from app.services.smart_analysis_service import SmartAnalysisService
from app.services.analysis_orchestrator import AnalysisOrchestrator
from app.services.safety_log_service import SafetyLogService
from app.database import (
    save_to_influx,
    get_influx_history,
    get_postgres_db,
    influx_client,
    INFLUX_ORG,
    INFLUX_BUCKET,
)

router = APIRouter()

# --- Routes --- #


@router.get("/health")
async def health_check(pg_db: Session = Depends(get_postgres_db)):
    """Checks if the backend can connect to the database."""
    try:
        pg_db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "degraded", "database": "disconnected", "error": str(e)}


@router.post("/telemetry")
async def receive_telemetry(
    data: TelemetryData, pg_db: Session = Depends(get_postgres_db)
):
    # immediate safety check
    temp = data.metrics.get(MetricType.TEMPERATURE, 0)

    interlock_active = temp > 188.0
    if interlock_active:
        trigger_safety_interlock(data, pg_db)

    save_to_influx(data)

    # get insights from orchestrator
    history = get_influx_history(limit=60)
    health = AnalysisOrchestrator.analyze_tool_health(data, history)

    # terminal visibility ('heartbeat' of the fab)
    print(
        f"--> Tool: {data.tool_id} | "
        f"RUL: {health.remaining_life_seconds if health.is_drifting else 'Stable'} | "
        f"Cause: {health.root_cause} ({health.reason})"
        f"Action: {health.recommended_action}"
    )

    return {
        "status": "processed",
        "wafer_id": data.wafer_id,
        "interlock_active": interlock_active,
        "predictions": health,
    }


@router.get("/history")
async def read_history():
    """Returns full history for charts and current drift status."""
    history = get_influx_history()

    temp_values = [
        h["value"] for h in history if h["metric"] == MetricType.TEMPERATURE.value
    ]

    prediction_val = None
    if temp_values:
        prediction_val = PdmService.predict_remaining_life(temp_values[-30:])

    return {
        "history": history,
        "predictions": {
            "remaining_life_seconds": prediction_val,
            "is_drifting": prediction_val is not None,
            "root_cause": (
                RootCauseType.NORMAL
                if not prediction_val
                else RootCauseType.SENSORY_DRIFT
            ),
            "reason": "Historical trend analysis" if prediction_val else "Stable",
            "recommended_action": ActionType.MONITOR,
        },
    }


@router.get("/quarantine")
async def get_quarantine_logs(pg_db: Session = Depends(get_postgres_db)):
    return pg_db.query(QuarantineLog).order_by(QuarantineLog.timestamp.desc()).all()


@router.get("/telemetry/spc/{tool_id}")
def get_tool_spc_data(tool_id: str):
    raw_history = get_influx_history(limit=100)
    tool_data = [
        {"time": h["time"], "value": h["value"]}
        for h in raw_history
        if h["tool_id"] == tool_id and h["metric"] == MetricType.TEMPERATURE.value
    ]

    if not tool_data:
        raise HTTPException(status_code=404, detail="Insufficient data for SPC")

    return SPCService.calculate_spc_metrics(tool_data)


@router.get("/latest")
async def get_latest():
    """Utility to grab the absolute latest state of the primary tool."""
    query_api = influx_client.query_api()
    flux_query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "wafer_metrics")
            |> filter(fn: (r) => r["tool_id"] == "ETCH-001")
            |> last()
    """
    result = query_api.query(org=INFLUX_ORG, query=flux_query)

    if not result:
        return {"error": "No data found"}

    latest_data = {"metrics": {}}
    for table in result:
        for record in table.records:
            latest_data["tool_id"] = record.values.get("tool_id")
            latest_data["wafer_id"] = record.values.get("wafer_id")
            latest_data["metrics"][record.get_field()] = record.get_value()

    return latest_data


@router.post("/system/reset")
async def reset_system(pg_db: Session = Depends(get_postgres_db)):
    """
    Resumes the simulation by clearing interlock states
    and preparing the tool for a new run.
    """
    try:
        rows = pg_db.query(QuarantineLog).delete()
        pg_db.commit()
        print(f"--> RESET: Cleared {rows} quarantine records.")
    except Exception as e:
        pg_db.rollback()
        print(f"--> RESET ERROR: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset system")

    print("--> SYSTEM RESET SIGNAL SENT TO SIMULATOR")
    SafetyLogService.log_reset()

    return {"status": "system_resumed", "message": "Interlock cleared."}


# --- Helpers --- #


def trigger_safety_interlock(data: TelemetryData, pg_db: Session):
    temp = data.metrics.get(MetricType.TEMPERATURE, 0)

    # 1. Log to file FIRST (Critical Safety Path - works even if DB is down)
    SafetyLogService.log_shutdown(
        tool_id=data.tool_id,
        wafer_id=data.wafer_id,
        metric=MetricType.TEMPERATURE.value,
        value=temp,
        threshold=188.0,
    )

    # 2. Attempt Database Log (Wrapped in try/except to handle connection resets)
    try:
        existing_interlock = (
            pg_db.query(QuarantineLog)
            .filter(
                QuarantineLog.tool_id == data.tool_id,
                QuarantineLog.wafer_id == data.wafer_id,
            )
            .first()
        )

        if not existing_interlock:
            new_quarantine = QuarantineLog(
                wafer_id=data.wafer_id,
                tool_id=data.tool_id,
                metric_name=MetricType.TEMPERATURE.value,
                violation_value=temp,
                threshold_limit=188.0,
            )
            pg_db.add(new_quarantine)
            pg_db.commit()
            print(f"!!! SAFETY INTERLOCK LOGGED: {data.wafer_id} !!!")
    except Exception as e:
        print(f"!!! DB ERROR (Connection Reset?): {e}")
        pg_db.rollback()
