import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

url = os.getenv("INFLUXDB_URL", "http://db:8086")
token = os.getenv("INFLUXDB_TOKEN", "password123")
org = os.getenv("INFLUXDB_ORG", "greenfield_inc")
bucket = os.getenv("INFLUXDB_BUCKET", "wafer_telemetry")

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def save_telemetry(data):
    point = Point("wafer_metrics") \
        .tag("tool_id", data.tool_id) \
        .tag("status", data.status) \
        .field("temp", data.metrics['temperature']) \
        .field("pressure", data.metrics['pressure']) \
        .time(data.timestamp, WritePrecision.NS)
    
    write_api.write(bucket, org, point)

def get_history(limit=50):
    query = f'from(bucket: "{bucket}") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "wafer_metrics") |> limit(n: {limit})'
    result = client.query_api().query(org=org, query=query)
    
    history = []
    for table in result:
        for record in table.records:
            history.append({
                "time": record.get_time(),
                "metric": record.get_field(),
                "value": record.get_value(),
                "tool_id": record.values.get("tool_id")
            })
    return history
