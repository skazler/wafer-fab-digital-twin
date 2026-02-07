from fastapi import FastAPI
from models import TelemetryData
from database import save_telemetry

app = FastAPI(title="Greenfield Digital Twin API")

@app.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    # save to InfluxDB
    save_telemetry(data)
    print(f"Received data from {data.tool_id} for {data.wafer_id}")
    return {"status": "success", "wafer_id": data.wafer_id}

def trigger_safety_interlock(wafer_id: str, metric: str, value: float):
    """
    simulates a 'Machine Stop' command. In a real Fab, this would 
    signal the hardware to cease operations immediately.
    """
    print(f"!!! SAFETY INTERLOCK TRIGGERED !!!")
    print(f"REASON: {metric} value {value} exceeds safety threshold.")
    print(f"ACTION: Cutting power to Tool ETCH-001. Lot {wafer_id} quarantined.")
    # todo: in a full app, send an emergency notification via email/slack here

@app.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    temp = data.metrics.get('temperature', 0)
    interlock_triggered = False

    if temp > 188.0:
        trigger_safety_interlock(data.wafer_id, "Temperature", temp)
        interlock_triggered = True

    save_telemetry(data)
    
    return {
        "status": "processed", 
        "interlock_active": interlock_triggered
    }

@app.get("/history")
async def read_history():
    data = get_history()
    return {"history": data}

@app.get("/latest")
async def get_latest():
    query_api = client.query_api()
    
    # The Flux Query: 
    # 1. Look at the telemetry bucket
    # 2. Look at the last hour (-1h)
    # 3. Filter for our specific tool
    # 4. Grab only the very last point
    flux_query = f'''
        from(bucket: "{bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "telemetry")
            |> filter(fn: (r) => r["tool_id"] == "ETCH-001")
            |> last()
    '''
    
    result = query_api.query(org=org, query=flux_query)
    
    # transform Flux format into the JSON the app expects
    latest_data = {"metrics": {}}
    for table in result:
        for record in table.records:
            latest_data["tool_id"] = record["tool_id"]
            latest_data["wafer_id"] = record["wafer_id"]
            latest_data["status"] = record["status"]
            # map the field (temp or pressure) to the metrics dict
            latest_data["metrics"][record.get_field()] = record.get_value()
            
    return latest_data
