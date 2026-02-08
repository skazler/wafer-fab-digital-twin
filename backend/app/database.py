import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# --- POSTGRESQL (Relational Metadata & Audit Logs) --- #

POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@postgres_db:5432/fab_metadata")

pg_engine = create_engine(POSTGRES_URL)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
Base = declarative_base()

def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- INFLUXDB (High-Frequency Sensor Telemetry) --- #
INFLUX_URL = os.getenv("INFLUXDB_URL", "http://influx_db:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-admin-token-123")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "greenfield_inc")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET", "wafer_telemetry")

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def save_to_influx(data):
    point = Point("wafer_metrics") \
        .tag("tool_id", data.tool_id) \
        .tag("wafer_id", data.wafer_id) \
        .tag("status", data.status) \
        .field("temperature", float(data.metrics.get('temperature', 0))) \
        .field("pressure", float(data.metrics.get('pressure', 0))) \
        .time(data.timestamp, WritePrecision.NS)
    
    influx_write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)

def get_influx_history(limit=50):
    query_api = influx_client.query_api()
    query = f'''
        from(bucket: "{INFLUX_BUCKET}") 
        |> range(start: -1h) 
        |> filter(fn: (r) => r["_measurement"] == "wafer_metrics") 
        |> limit(n: {limit})
    '''
    result = query_api.query(org=INFLUX_ORG, query=query)
    
    history = []
    for table in result:
        for record in table.records:
            history.append({
                "time": record.get_time(),
                "metric": record.get_field(),
                "value": record.get_value(),
                "tool_id": record.values.get("tool_id"),
                "wafer_id": record.values.get("wafer_id")
            })
    return history
