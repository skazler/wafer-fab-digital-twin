import time
import json
import random
from datetime import datetime

class SemiconductorEtchTool:
    def __init__(self, tool_id):
        self.tool_id = tool_id
        self.base_temp = 180.0  # celsius
        self.base_pressure = 10.0  # mTorr
        self.cycle_count = 0
        self.is_running = True

    def generate_telemetry(self):
        """Simulates sensor data with realistic industrial noise"""
        self.cycle_count += 1
        
        # simulate 'sensor drift': temperature rises slightly as the tool ages
        drift = self.cycle_count * 0.005 
        
        # add Gaussian noise (normal distribution) to simulate real-world physics
        current_temp = self.base_temp + drift + random.gauss(0, 0.5)
        current_pressure = self.base_pressure + random.gauss(0, 0.2)

        # logic: If temp exceeds 185, it's an 'Anomaly'
        status = "NOMINAL"
        if current_temp > 185.0:
            status = "CRITICAL_OVERHEAT"

        telemetry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_id": self.tool_id,
            "wafer_id": f"WFR-{self.cycle_count:04d}",
            "metrics": {
                "temperature": round(current_temp, 2),
                "pressure": round(current_pressure, 2)
            },
            "status": status,
            "location": "Greenfield-Line1"
        }
        return telemetry

# --- Execution Block ---
if __name__ == "__main__":
    # Simulate Tool 'ETCH-001' in the Greenfield Fab
    etch_tool = SemiconductorEtchTool(tool_id="ETCH-001")
    
    print(f"--- Starting Digital Twin Stream for {etch_tool.tool_id} ---")
    
    try:
        while True:
            data = etch_tool.generate_telemetry()
            
            # This is sent to backend/MQTT
            print(json.dumps(data, indent=2))
            
            # Wait 2 seconds between wafer cycles to simulate processing time
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStream stopped by user.")
