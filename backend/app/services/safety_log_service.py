import logging
import sys
import os
from datetime import datetime


class SafetyLogService:
    """
    Service responsible for logging critical safety events and tool shutdowns.
    """

    _logger = None

    @classmethod
    def _get_logger(cls):
        if cls._logger:
            return cls._logger

        logger = logging.getLogger("safety_service")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            log_dir = os.path.join(base_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)

            log_filename = f"safety_shutdowns_{datetime.now().strftime('%Y-%m-%d')}.log"
            file_handler = logging.FileHandler(os.path.join(log_dir, log_filename))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._logger = logger
        return cls._logger

    @classmethod
    def log_shutdown(
        cls, tool_id: str, wafer_id: str, metric: str, value: float, threshold: float
    ) -> None:

        cls._get_logger().critical(
            f"SHUTDOWN TRIGGERED | Tool: {tool_id} | Wafer: {wafer_id} | "
            f"Metric: {metric} | Value: {value:.2f} > Limit: {threshold}"
        )

    @classmethod
    def log_reset(cls) -> None:
        cls._get_logger().info(
            "SYSTEM RESET | Action: Manual Override | State: Cleared"
        )
