from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.models import QuarantineLog
from app.schemas.schemas import TelemetryData, MetricType
from app.services.spc_service import SPCService
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
    temp = data.metrics.get("temperature", 0)
    interlock_triggered = False

    if temp > 188.0:
        trigger_safety_interlock(data, pg_db)
        interlock_triggered = True

    save_to_influx(data)
    print(
        f"Processed: {data.tool_id} | Wafer: {data.wafer_id} | Interlock: {interlock_triggered}"
    )
    return {
        "status": "processed",
        "wafer_id": data.wafer_id,
        "interlock_active": interlock_triggered,
    }


@router.get("/history")
async def read_history():
    return {"history": get_influx_history()}


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
        if h["tool_id"] == tool_id and h["metric"] == "temperature"
    ]

    if not tool_data:
        raise HTTPException(
            status_code=404, detail="No telemetry found for SPC calculation"
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
    temp = data.metrics.get("temperature", 0)
    print(f"!!! SAFETY INTERLOCK TRIGGERED: Tool {data.tool_id} !!!")

    new_quarantine = QuarantineLog(
        wafer_id=data.wafer_id,
        tool_id=data.tool_id,
        metric_name="Temperature",
        violation_value=temp,
        threshold_limit=188.0,
    )
    pg_db.add(new_quarantine)
    pg_db.commit()
