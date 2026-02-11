from typing import List, Dict, Any
from app.schemas.schemas import (
    TelemetryData,
    MetricType,
    RootCauseType,
    ActionType,
    PredictionResponse,
)
from app.services.pdm_service import PdmService
from app.services.smart_analysis_service import SmartAnalysisService


class AnalysisOrchestrator:
    @staticmethod
    def analyze_tool_health(
        data: TelemetryData, raw_history: List[dict]
    ) -> PredictionResponse:
        """
        Orchestrates tool health analysis.
        """
        # extract content
        tool_id = data.tool_id
        current_temp = data.metrics.get(MetricType.TEMPERATURE, 0.0)

        # build map and extract history
        telemetry_map = AnalysisOrchestrator._build_telemetry_map(tool_id, raw_history)
        temp_vals = telemetry_map.get(MetricType.TEMPERATURE, [])

        # prognostic analysis (RUL)
        rul_seconds = PdmService.predict_remaining_life(temp_vals)

        # smart analysis (RCA & countermeasure)
        root_cause = RootCauseType.NORMAL
        reason = "Stable"
        action = ActionType.MONITOR
        if rul_seconds is not None:
            baseline = SmartAnalysisService.get_adaptive_baseline(temp_vals)
            severity = current_temp - baseline

            root_cause, reason = SmartAnalysisService.identify_root_cause(
                MetricType.TEMPERATURE, telemetry_map
            )
            action = SmartAnalysisService.get_countermeasures(severity, rul_seconds)

        return PredictionResponse(
            remaining_life_seconds=rul_seconds,
            is_drifting=rul_seconds is not None,
            root_cause=root_cause,
            reason=reason,
            recommended_action=action,
        )

    @staticmethod
    def _build_telemetry_map(
        tool_id: str, raw_history: List[dict]
    ) -> Dict[MetricType, List[float]]:
        """Helper to group data by metric type in a single pass."""
        t_map: Dict[MetricType, List[float]] = {}
        for entry in raw_history:
            if entry.get("tool_id") == tool_id:
                try:
                    m_type = MetricType(entry["metric"])
                    if m_type not in t_map:
                        t_map[m_type] = []
                    t_map[m_type].append(entry["value"])
                except (ValueError, KeyError):
                    continue
        return t_map
