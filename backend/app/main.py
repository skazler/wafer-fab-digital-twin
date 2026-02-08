from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as spc_router
from app.database import pg_engine, Base
import app.models as models

# --- Database Initialization --- #
Base.metadata.create_all(bind=pg_engine)

app = FastAPI(title="Greenfield Digital Twin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "documentation": "/docs"
    }
