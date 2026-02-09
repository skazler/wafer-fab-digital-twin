import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from app.schemas.schemas import MetricType

# --- ENVIRONMENT CONFIGURATION --- #

PG_USER = os.getenv("POSTGRES_USER", "admin")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "password123")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres_db")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "fab_metadata")

POSTGRES_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://influx_db:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "greenfield_inc")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET", "wafer_telemetry")

# --- POSTGRESQL SETUP --- #

pg_engine = create_engine(POSTGRES_URL)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
Base = declarative_base()


def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- INFLUXDB SETUP --- #

influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)


def save_to_influx(data):
    point = (
        Point("wafer_metrics")
        .tag("tool_id", data.tool_id)
        .tag("wafer_id", data.wafer_id)
        .tag("status", data.status)
    )

    for metric in MetricType:
        val = data.metrics.get(metric)
        if val is not None:
            point.field(metric.value, float(val))

    point.time(data.timestamp, WritePrecision.NS)
    influx_write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)


def get_influx_history(limit=100):
    query_api = influx_client.query_api()
    query = f"""
        from(bucket: "{INFLUX_BUCKET}") 
        |> range(start: -1h) 
        |> filter(fn: (r) => r["_measurement"] == "wafer_metrics") 
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: {limit})
    """
    result = query_api.query(org=INFLUX_ORG, query=query)

    history = []
    for table in result:
        for record in table.records:
            history.append(
                {
                    "time": record.get_time(),
                    "metric": record.get_field(),
                    "value": record.get_value(),
                    "tool_id": record.values.get("tool_id"),
                    "wafer_id": record.values.get("wafer_id"),
                }
            )
    return history
