# Project Greenfield: Industrial Digital Twin

## 🏗️ Overview
This repository contains a **Digital Twin Prototype** designed to model a wafer lifecycle in a miniature semiconductor manufacturing environment. It demonstrates the intersection of high-frequency sensor telemetry and strict relational audit trails.

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
| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **API Framework** | FastAPI (Python 3.11) | High-concurrency async logic |
| **Time-Series DB** | InfluxDB 2.7 (Flux) | Millisecond sensor telemetry |
| **Relational DB** | PostgreSQL 15 | Persistent audit & state management |
| **ORM** | SQLAlchemy / Pydantic | Schema enforcement & validation |
| **Analysis** | Polars / NumPy | High-performance SPC calculations |
| **Deployment** | Docker & Docker Compose | Environment parity & orchestration |

### 🚀 Key Technical Features
* **Automated Safety Interlock:** Real-time logic detects process excursions (e.g. temperature > 188.0°C) and automatically triggers a "Machine Stop" event.
* **Relational Event Logging:** All safety violations are persisted to PostgreSQL with a `QuarantineLog` entry, ensuring a permanent audit trail for fab engineers.
* **Time-Series Analytics:** Sensor data is streamed to InfluxDB, allowing for millisecond-resolution historical trending and analysis.
* **SPC Integration:** Leverages a custom service to calculate Statistical Process Control metrics (Mean, Sigma, Control Limits) to detect process drift before failure.
* **Containerized Orchestration:** Fully Dockerized environment to ensure seamless deployment between development and production.

## 🚦 Getting Started

### Prerequisites
* Docker and Docker Compose installed.

### Installation
1. **Clone the Repository:**
    ```bash
    git clone [https://github.com/skazler/wafer-fab-digital-twin.git](https://github.com/skazler/wafer-fab-digital-twin.git)
    cd wafer-fab-digital-twin
    ```
2. **Launch the System:**
    ```bash
    # 1. Zero-State Reset
    # Clear stale containers and wipe database volumes
    docker compose down -v

    # 2. Tactical Launch
    # TERMINAL 1: Build and start Infrastructure (Backend, DB, Simulator)
    docker compose up --build

    # TERMINAL 2: Launch Control Room (Frontend Dashboard)
    cd frontend
    npm install
    npm run dev
    ```
3. **Access Points:**
    * **Interactive API Documentation:** `http://localhost:8000/docs`
    * **InfluxDB Dashboard:** `http://localhost:8086` (Default: `admin`/`password123`)
    * **View HUD (Dashboard):** `http://localhost:5173/`

## 📈 Future Roadmap
* [ ] **The "OEE" Dashboard:** Real-time calculation of Availability, Performance, and Quality metrics to track tool efficiency.
* [ ] **Visual SPC Control Charts:** Integrated D3.js components to highlight process drift and allow engineer annotations.
* [ ] **"Digital Thread" Traceability:** A "Wafer History" view tracing a single ID through multiple tools to ensure total data lineage.
* [ ] **Predictive Maintenance (PdM):** Health-scoring algorithms to trigger maintenance alerts before hardware failure occurs.

## 👋 Contact & Connect

**Sky H. Yoo** 📧 [yooskyh@gmail.com](mailto:yooskyh@gmail.com)

I’m a developer passionate about resilient and scalable solutions and modern software stacks. If you have questions about this architecture or want to discuss how we can optimize software workflows, feel free to reach out—I'm always happy to chat and learn something new!
