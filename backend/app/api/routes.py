from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.models import QuarantineLog
from app.schemas.schemas import TelemetryData, MetricType
from app.services.spc_service import SPCService
from app.services.pdm_service import PdmService
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


@router.post("/telemetry")
async def receive_telemetry(
    data: TelemetryData, pg_db: Session = Depends(get_postgres_db)
):
    temp = data.metrics.get(MetricType.TEMPERATURE, 0)
    interlock_triggered = False

    if temp > 188.0:
        trigger_safety_interlock(data, pg_db)
        interlock_triggered = True

    save_to_influx(data)

    # calculate Predictive Maintenance (PdM) Metrics
    raw_history = get_influx_history(limit=30)
    tool_history = [
        {"time": h["time"], "value": h["value"]}
        for h in raw_history
        if h["tool_id"] == data.tool_id and h["metric"] == MetricType.TEMPERATURE.value
    ]
    rul_seconds = PdmService.predict_remaining_life(tool_history)

    print(
        f"Processed: {data.tool_id} | Wafer: {data.wafer_id} | "
        f"Interlock: {interlock_triggered} | RUL: {rul_seconds if rul_seconds else 'Stable'}"
    )

    return {
        "status": "processed",
        "wafer_id": data.wafer_id,
        "interlock_active": interlock_triggered,
        "predictions": {
            "remaining_life_seconds": rul_seconds,
            "is_drifting": rul_seconds is not None,
        },
    }


@router.get("/history")
async def read_history():
    history = get_influx_history()

    latest_history = [h for h in history if h["metric"] == MetricType.TEMPERATURE.value]

    prediction = (
        PdmService.predict_remaining_life(latest_history[-30:])
        if latest_history
        else None
    )

    return {
        "history": history,
        "predictions": {
            "remaining_life_seconds": prediction,
            "is_drifting": prediction is not None,
        },
    }


@router.get("/quarantine")
async def get_quarantine_logs(pg_db: Session = Depends(get_postgres_db)):
    logs = pg_db.query(QuarantineLog).order_by(QuarantineLog.timestamp.desc()).all()
    return logs


@router.get("/telemetry/spc/{tool_id}")
def get_tool_spc_data(tool_id: str):
    raw_history = get_influx_history(limit=100)

    tool_data = [
        {"time": h["time"], "value": h["value"]}
        for h in raw_history
        if h["tool_id"] == tool_id and h["metric"] == MetricType.TEMPERATURE.value
    ]

    if not tool_data:
        raise HTTPException(
            status_code=404,
            detail=f"No {MetricType.TEMPERATURE} telemetry found for SPC",
        )

    analysis = SPCService.calculate_spc_metrics(tool_data)
    return analysis


@router.get("/latest")
async def get_latest():
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
        return {"error": "No data found in the last hour"}

    latest_data = {"metrics": {}}
    for table in result:
        for record in table.records:
            latest_data["tool_id"] = record.values.get("tool_id")
            latest_data["wafer_id"] = record.values.get("wafer_id")
            latest_data["status"] = record.values.get("status", "unknown")
            latest_data["metrics"][record.get_field()] = record.get_value()

    return latest_data


# --- Helpers --- #


def trigger_safety_interlock(data: TelemetryData, pg_db: Session):
    temp = data.metrics.get(MetricType.TEMPERATURE, 0)
    print(f"!!! SAFETY INTERLOCK TRIGGERED: Tool {data.tool_id} !!!")

    new_quarantine = QuarantineLog(
        wafer_id=data.wafer_id,
        tool_id=data.tool_id,
        metric_name=MetricType.TEMPERATURE.value,
        violation_value=temp,
        threshold_limit=188.0,
    )
    pg_db.add(new_quarantine)
    pg_db.commit()
