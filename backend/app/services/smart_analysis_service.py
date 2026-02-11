import numpy as np
from typing import Dict, List
from app.schemas.schemas import MetricType, RootCauseType, ActionType


class SmartAnalysisService:
    @staticmethod
    def get_adaptive_baseline(
        history_values: List[float], alpha: float = 0.15
    ) -> float:
        if not history_values:
            return 0.0
        ema = history_values[0]
        for val in history_values[1:]:
            ema = (val * alpha) + (ema * (1 - alpha))
        return round(ema, 2)

    @staticmethod
    def identify_root_cause(
        target_metric: MetricType, telemetry_map: Dict[MetricType, List[float]]
    ) -> tuple[RootCauseType, str]:
        # analyze correlations
        if target_metric not in telemetry_map or len(telemetry_map) < 2:
            return RootCauseType.NORMAL, "No correlations found"

        target_data = np.array(telemetry_map[target_metric])
        causes = []

        for metric_type, values in telemetry_map.items():
            if metric_type == target_metric:
                continue

            compare_data = np.array(values[-len(target_data) :])
            correlation = np.corrcoef(target_data, compare_data)[0, 1]

            if not np.isnan(correlation) and abs(correlation) > 0.7:
                causes.append(
                    {
                        "metric": metric_type.value.upper(),
                        "correlation": round(correlation, 2),
                        "impact": "DIRECT" if correlation > 0 else "INVERSE",
                    }
                )

        if not causes:
            return (
                RootCauseType.THERMAL_RUNAWAY,
                f"{target_metric.value.upper()}_PRIMARY_FAILURE",
            )

        # find top cause
        top = sorted(causes, key=lambda x: abs(x["correlation"]), reverse=True)[0]
        reason_str = f"CONTRIBUTING_FACTOR: {top['metric']} ({top['impact']})"

        return RootCauseType.SYSTEM_INSTABILITY, reason_str

    @staticmethod
    def get_countermeasures(
        deviation_severity: float, rul_seconds: float
    ) -> ActionType:
        if rul_seconds and rul_seconds < 30:
            return ActionType.EMERGENCY_STOP

        if deviation_severity > 5.0:
            return ActionType.INCREASE_COOLANT

        return ActionType.MONITOR
