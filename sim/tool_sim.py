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

    def generate_telemetry(self):
        self.cycle_count += 1
        drift = self.cycle_count * 0.005 
        current_temp = self.base_temp + drift + random.gauss(0, 0.5)
        current_pressure = self.base_pressure + random.gauss(0, 0.2)

        # determine status based on the threshold
        # matches the 188.0 limit we set in the backend
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
                "pressure": round(current_pressure, 2)
            },
            "status": status_msg,
            "location": "SITE-GREENFIELD-TX"
    }


if __name__ == "__main__":
    etch_tool = SemiconductorEtchTool(tool_id="ETCH-001")
    api_url = os.getenv("API_URL", "http://backend:8000/telemetry")
    
    print(f"--- [MISSION START] Digital Twin Stream: {etch_tool.tool_id} ---")
    
    try:
        while etch_tool.is_running:
            data = etch_tool.generate_telemetry()
            
            # send telemetry and listen for response
            try:
                response = requests.post(api_url, json=data, timeout=2)
                
                if response.status_code == 200:
                    result = response.json()
                    current_val = data['metrics']['temperature']
                    
                    if result.get("interlock_active"):
                        print(f"!!! INTERLOCK SIGNAL RECEIVED AT {current_val}°C !!!")
                        print(f"ACTION: Executing Autonomous Emergency Shutdown for {data['wafer_id']}.")
                        etch_tool.is_running = False
                    else:
                        print(f"Wafer {data['wafer_id']} Processed: {current_val}°C - Status: OK")
                
            except requests.exceptions.ConnectionError:
                print("Error: Backend Nervous System unreachable. Retrying...")

            time.sleep(2)
            
        print("--- [MISSION END] Tool in Safe State. ---")
            
    except KeyboardInterrupt:
        print("\nManual override detected. Stopping stream.")
