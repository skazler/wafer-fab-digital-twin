from scipy import stats
import numpy as np


class PdmService:
    @staticmethod
    def predict_remaining_life(
        values: list[float], threshold: float = 188.0
    ) -> float | None:
        """
        Calculates the slope of sensor drift and forecasts Remaining Useful Life (RUL).
        Includes data safety guards.
        """
        CONCERNING_SLOPE = 0.005

        # data safety guard: linregress needs at least 2, but we prefer 10 for stability
        if not values or len(values) < 10:
            return None

        # variance guard: If all values are identical, slope is 0.
        if len(set(values)) <= 1:
            return None

        # now begin calculations
        x = np.arange(len(values))
        y = np.array(values)

        # linear regression
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        except Exception:
            return None

        # only predict if the temperature is actually rising
        if slope <= CONCERNING_SLOPE:
            return None

        # RUL = (Limit - Current) / Rate of change (slope)
        current_val = values[-1]
        if current_val >= threshold:
            return 0.0
        seconds_to_failure = (threshold - current_val) / slope

        return round(max(0, seconds_to_failure), 2)
