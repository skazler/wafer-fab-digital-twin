# Project Greenfield: Industrial Digital Twin

## Summary
This project is a full-stack Digital Twin architecture designed to simulate, monitor, and control semiconductor manufacturing processes in real-time. Named **"Greenfield"** to reflect the nature of new facility development in Texas, the system demonstrates the intersection of software engineering and industrial safety protocols.

## Technical Architecture
- **Physical Layer (Simulator):** A Python-based stochastic engine modeling tool degradation and sensor drift in a plasma etching environment.
- **Nervous System (Backend):** A FastAPI microservice implementing **Safety Interlocks** and data validation.
- **Memory (Database):** InfluxDB time-series storage for millisecond-precision audit trails.
- **Control Room (Frontend):** A React dashboard featuring real-time telemetry visualization and automated event logging.

## Core Features
- **Autonomous Interlock System:** The backend monitors "drift" parameters and issues a remote shutdown command (Command & Control) to the physical tool if thermal thresholds are breached.
- **Microservice Orchestration:** Fully containerized using **Docker Compose** to simulate a distributed factory network.
- **Data Integrity:** Implements Pydantic modeling to ensure "Zero-Defect" data entry into the system history.

## 🛠 Standard Operational Procedures

To deploy the Digital Twin environment, follow these steps in order. Ensure you have **Docker Desktop** running before starting.

### Deployment & Operations SOP

```bash
# 1. Zero-State Reset
# Clear stale containers and wipe database volumes
docker compose down -v

# 2. Tactical Launch
# TERMINAL 1: Build and start Infrastructure (Backend, DB, Simulator)
docker compose up --build

# TERMINAL 2: Launch Control Room (Frontend Dashboard)
cd frontend
npm start

# 3. Mission Surveillance
# View HUD (Dashboard):     http://localhost:3000
# View API Telemetry:       http://localhost:8000/docs
# View Data Vault (DB):     http://localhost:8086
```

### Current Progress Images
TBD.

## Future Steps
- **The "OEE" Dashboard (Overall Equipment Effectiveness):** To measure if tools are being used efficiently.
  - A real-time dashboard that calculates availability, performance, and quality.
  - Why: to understand the business metrics of a fab and explain why a tool’s OEE dropped (e.g. "the digital twin showed a spike in down time which impacted availability").

- **SPC (Statistical Process Control) Integration:** detect if a process is drifting before it ruins wafers.
  - A backend service that runs Western Electric Rules (or simple thresholding) on the simulated sensor data (temperature, pressure, etc).
  - A "Control Chart" component (using D3.js or Chart.js) that highlights points in red when they violate a rule and allows an engineer to "annotate" the deviation.

- **"Digital Thread" Traceability (Data Lineage):** Semiconductors have a complex "lineage." One wafer goes through hundreds of tools. If a chip fails a month later, we need to trace it back.
  - A "Wafer History" view: If a user clicks on a virtual wafer ID, show every tool it touched, the timestamps, and the specific telemetry (sensor data) recorded at those steps.
  - Store this in a relational database (PostgreSQL) with a schema designed for high-performance time-series lookups.

- **Predictive Maintenance (PdM) Alerting:** For "smart manufacturing."
  - A simple "Health Score" for the tools (using a Python script to simulate tool wear). When the "vibration" or "temperature" exceeds a certain cumulative threshold, trigger a REST API alert (FastAPI) that shows up as a notification in the frontend.
  - This mimics a "Maintenance Management System" integration.
