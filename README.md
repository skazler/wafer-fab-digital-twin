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

## 🛠 Operational Procedures (SOP)

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