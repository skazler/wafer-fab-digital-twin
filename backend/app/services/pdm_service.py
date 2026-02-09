from scipy import stats
import numpy as np
from datetime import datetime, timezone


class PdmService:
    @staticmethod
    def predict_remaining_life(history_data, threshold=188.0):
        """
        Uses SciPy to calculate the slope of sensor drift and
        forecast the Remaining Useful Life (RUL).
        """

        if not history_data or len(history_data) < 10:
            return None

        # freshness check: if data is older than 10 seconds, the tool isn't "live"
        last_reading_time = history_data[-1]["time"]
        now = datetime.now(last_reading_time.tzinfo or timezone.utc)
        if (now - last_reading_time).total_seconds() > 10:
            return None

        # extract values
        times = [h["time"].timestamp() for h in history_data]
        values = [h["value"] for h in history_data]

        # normalize time: seconds elapsed from the start of this window
        start_ts = times[0]
        x_rel = [t - start_ts for t in times]

        # calculate linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_rel, values)

        # stability filter: ignore slopes that are flat
        if slope <= 0.005:
            return None

        # prediction calculation
        current_val = values[-1]
        remaining_seconds = (threshold - current_val) / slope

        return max(0, round(remaining_seconds, 2))
