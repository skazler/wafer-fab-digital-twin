import time
import json
import random
import os
import requests
from datetime import datetime


class SemiconductorEtchTool:
    def __init__(self, tool_id):
        self.tool_id = tool_id
        self.base_temp = 180.0
        self.base_pressure = 10.0
        self.cycle_count = 0
        self.is_running = True

        self.degradation_rate = 0.0
        self.is_degrading = False
        self.total_drift = 0.0

    def generate_telemetry(self):
        self.cycle_count += 1

        # 1. Random Chance to start Degradation (e.g. 33% chance per cycle)
        if not self.is_degrading and random.random() < 0.33:
            print(
                f"--- [HARDWARE EVENT] {self.tool_id}: Heating element wear detected. Starting drift. ---"
            )
            self.is_degrading = True
            self.degradation_rate = random.uniform(0.05, 0.15)

        # 2. Accumulate drift over time
        if self.is_degrading:
            self.total_drift += self.degradation_rate

        # 3. Calculate metrics with Gauss noise
        current_temp = self.base_temp + self.total_drift + random.gauss(0, 0.3)
        current_pressure = self.base_pressure + random.gauss(0, 0.1)

        # 4. Determine status based on thresholds
        if current_temp > 188.0:
            status_msg = "CRITICAL_OVERHEAT"
        elif current_temp > 185.0:
            status_msg = "WARNING_HIGH_TEMP"
        else:
            status_msg = "NOMINAL"

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_id": self.tool_id,
            "wafer_id": f"WFR-{self.cycle_count:04d}",
            "metrics": {
                "temperature": round(current_temp, 2),
                "pressure": round(current_pressure, 2),
            },
            "status": status_msg,
            "is_degrading": self.is_degrading,
            "location": "SITE-GREENFIELD-TX",
        }


if __name__ == "__main__":
    etch_tool = SemiconductorEtchTool(tool_id="ETCH-001")
    api_url = os.getenv("API_URL", "http://backend:8000/telemetry")

    print(f"--- [MISSION START] Digital Twin Stream: {etch_tool.tool_id} ---")

    try:
        while etch_tool.is_running:
            data = etch_tool.generate_telemetry()

            try:
                response = requests.post(api_url, json=data, timeout=2)

                if response.status_code == 200:
                    result = response.json()
                    current_val = data["metrics"]["temperature"]

                    if result.get("interlock_active"):
                        print(f"!!! INTERLOCK SIGNAL RECEIVED AT {current_val}°C !!!")
                        print(
                            f"ACTION: Executing Autonomous Emergency Shutdown for {data['wafer_id']}."
                        )
                        etch_tool.is_running = False
                    else:
                        drift_info = (
                            f"[DRIFTING: +{etch_tool.degradation_rate:.3f}/cycle]"
                            if etch_tool.is_degrading
                            else "[STABLE]"
                        )
                        print(
                            f"Wafer {data['wafer_id']} | {current_val}°C | Status: {data['status']} {drift_info}"
                        )

            except requests.exceptions.ConnectionError:
                print("Error: Backend Nervous System unreachable. Retrying...")

            time.sleep(2)

        print("--- [MISSION END] Tool in Safe State. ---")

    except KeyboardInterrupt:
        print("\nManual override detected. Stopping stream.")
