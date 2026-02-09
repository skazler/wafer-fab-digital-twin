from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as spc_router
from app.database import pg_engine, Base
import app.models.models as models
from app.database import PG_HOST, INFLUX_URL
import logging

# --- Database Initialization --- #
Base.metadata.create_all(bind=pg_engine)

app = FastAPI(title="Greenfield Digital Twin API")

# CORS enablement to frontend
origins = [
    "http://localhost:5173",  # the Vue/Vite dev server
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spc_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Greenfield Digital Twin API is Operational",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 50)
    print("🚀 GREENFIELD DIGITAL TWIN API IS REACHABLE")
    print(f"Connected to Postgres: {PG_HOST}")
    print(f"Connected to InfluxDB: {INFLUX_URL}")
    print("=" * 50 + "\n")
