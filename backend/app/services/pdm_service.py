from scipy import stats
import numpy as np
from datetime import datetime


class PdmService:
    @staticmethod
    def predict_remaining_life(history_data, threshold=188.0):
        """
        Uses SciPy to calculate the slope of sensor drift and
        forecast the Remaining Useful Life (RUL).

        history_data: List of dicts [{'time': datetime, 'value': float}]
        """
        # Sampling window (approx 20-30s of data)
        if len(history_data) < 10:
            return None

        # Extract values
        times = [h["time"].timestamp() for h in history_data]
        values = [h["value"] for h in history_data]

        # Normalize time: seconds elapsed from the start of this window
        start_ts = times[0]
        x_rel = [t - start_ts for t in times]

        # Calculate Linear Regression: y = mx + b
        # slope (m), intercept (b), r_value (correlation), p_value, std_err
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_rel, values)

        # Stability Filter: Ignore slopes that are effectively flat (0.005 deg/sec or less)
        if slope <= 0.005:
            return None

        # Prediction: (Threshold - Current Value) / Slope = Seconds Remaining
        # We use the most recent value (values[-1]) for higher accuracy
        current_val = values[-1]
        remaining_seconds = (threshold - current_val) / slope

        return max(0, round(remaining_seconds, 2))
