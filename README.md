# Project Greenfield: Industrial Digital Twin

## 🏗️ Overview
This repository contains a **Digital Twin Prototype** designed to model a wafer lifecycle in a miniature semiconductor manufacturing environment.

## 🛡️ IP & Security Disclaimer
**This project is a generic architectural demonstration and does not contain proprietary information.**
* **Data Integrity:** All telemetry data is synthetically generated using stochastic models and does not reflect real-world manufacturing recipes, setpoints, or proprietary process signatures.
* **Architectural Neutrality:** The system design utilizes industry-standard open-source tools (FastAPI, InfluxDB, Postgres) common in IIoT environments.
* **Compliance Awareness:** No proprietary schemas, hardware configurations, or corporate-specific logic from any manufacturer are utilized in this codebase. This project serves as a "Black Box" architectural proof-of-concept.


## 🧩 System Components
* **The Physical Layer (Simulator):** A Python-based stochastic data generator simulating an Etch tool process flow with randomized process noise.
* **The Nervous System (Backend):** An asynchronous Python hub managing data validation, safety logic, and cross-database orchestration.
* **The Memory (InfluxDB):** A time-series engine optimized for high-frequency "firehose" data (temperature, pressure, etc).
* **The Audit Trail (PostgreSQL):** A relational store for persistent "Safety Interlocks" and "Lot Quarantine" event logging.
* **The Control Room (Frontend):** A React dashboard featuring real-time telemetry visualization and automated event logging.

### 🛠️ Tech Stack
| Layer | Technology |
| :--- | :--- |
| **API Framework** | FastAPI (Python 3.11) |
| **Time-Series DB** | InfluxDB 2.7 (Flux) |
| **Relational DB** | PostgreSQL 15 |
| **ORM** | SQLAlchemy / Pydantic |
| **Analysis** | Polars / NumPy |
| **Deployment** | Docker & Docker Compose |

## 🚀 Key Technical Features
* **Automated Safety Interlock:** Real-time logic detects process excursions (e.g. temperature > 188.0°C) and automatically triggers a "Machine Stop" event.
* **Relational Event Logging:** All safety violations are persisted to PostgreSQL with a `QuarantineLog` entry, ensuring a permanent audit trail for fab engineers.
* **Time-Series Analytics:** Sensor data is streamed to InfluxDB, allowing for millisecond-resolution historical trending and analysis.
* **SPC Integration:** Leverages a custom service to calculate Statistical Process Control metrics (Mean, Sigma, Control Limits) to detect process drift before failure.
* **Containerized Orchestration:** Fully Dockerized environment to ensure seamless deployment and environment parity between development and production.

## 🛠 Standard Operational Procedures

To deploy the Digital Twin environment, follow these steps in order. Ensure you have **Docker Desktop** running before starting.

## 🚦 Getting Started

### Prerequisites
* Docker and Docker Compose installed.

### Installation
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/skazler/wafer-fab-digital-twin.git](https://github.com/skazler/wafer-fab-digital-twin.git)
    cd wafer-fab-digital-fab
    ```
2.  **Launch the System:**
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
    ```
3.  **Access Points:**
    * **Interactive API Documentation:** `http://localhost:8000/docs`
    * **InfluxDB Dashboard:** `http://localhost:8086` (Default: `admin`/`password123`)
    * **View HUD (Dashboard):** `http://localhost:3000`
    * **View API Telemetry:** `http://localhost:8000/docs`

## Current Progress Images
TBD.

## 📈 Future Roadmap
* [ ] **The "OEE" Dashboard (Overall Equipment Effectiveness):** To measure if tools are being used efficiently.
  - A real-time dashboard that calculates availability, performance, and quality.
  - Why: to understand the business metrics of a fab and explain why a tool’s OEE dropped (e.g. "the digital twin showed a spike in down time which impacted availability").

* [ ] **SPC (Statistical Process Control) Integration:** detect if a process is drifting before it ruins wafers.
  - A "Control Chart" component (using D3.js or Chart.js) that highlights points in red when they violate a rule and allows an engineer to "annotate" the deviation.

* [ ] **"Digital Thread" Traceability (Data Lineage):** Semiconductors have a complex "lineage." One wafer goes through hundreds of tools. If a chip fails a month later, we need to trace it back.
  - A "Wafer History" view: If a user clicks on a virtual wafer ID, show every tool it touched, the timestamps, and the specific telemetry (sensor data) recorded at those steps.
  - Store this in a relational database (PostgreSQL) with a schema designed for high-performance time-series lookups.

* [ ] **Predictive Maintenance (PdM) Alerting:** For "smart manufacturing."
  - A simple "Health Score" for the tools (using a Python script to simulate tool wear). When the "vibration" or "temperature" exceeds a certain cumulative threshold, trigger a REST API alert (FastAPI) that shows up as a notification in the frontend.
  - This mimics a "Maintenance Management System" integration.
