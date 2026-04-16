import logging
import json
import sys
import socket
import os
from datetime import datetime, timezone
from typing import Any

from src.shared.config import settings, LogContext

# ANSI color codes for terminal output
COLORS = {
    "DEBUG": "\033[36m",     # Cyan
    "INFO": "\033[32m",      # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[1;31m",  # Bold Red
}
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"


def _colorize(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter with support for local and k8s contexts."""

    def __init__(self, context: LogContext) -> None:
        super().__init__()
        self.context = context
        self.use_color = settings.log_color and context == LogContext.LOCAL

    def _base_fields(self, record: logging.LogRecord) -> dict[str, Any]:
        return {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

    def _local_fields(self) -> dict[str, Any]:
        return {
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
            "environment": "local",
        }

    def _k8s_fields(self) -> dict[str, Any]:
        return {
            "environment": "k8s",
            "k8s": {
                "namespace": settings.k8s_namespace,
                "pod": settings.k8s_pod_name,
                "node": settings.k8s_node_name,
            },
        }

    def _colorize_json(self, log_entry: dict[str, Any]) -> str:
        """Apply ANSI colors to the JSON output for local terminal readability."""
        level = log_entry.get("level", "INFO")
        color = COLORS.get(level, "")

        timestamp = _colorize(log_entry["timestamp"], DIM)
        level_str = _colorize(f"{level:<8}", color)
        logger_name = _colorize(log_entry["logger"], DIM)
        message = _colorize(log_entry["message"], BOLD)

        # Build the remaining fields as dimmed JSON
        extra = {k: v for k, v in log_entry.items() if k not in ("timestamp", "level", "logger", "message")}
        extra_str = ""
        if extra:
            extra_str = f" {_colorize(json.dumps(extra, default=str), DIM)}"

        return f"{timestamp} {level_str} {logger_name} {message}{extra_str}"

    def format(self, record: logging.LogRecord) -> str:
        log_entry = self._base_fields(record)

        if self.context == LogContext.K8S:
            log_entry.update(self._k8s_fields())
        else:
            log_entry.update(self._local_fields())

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include extra structured data passed via `extra={"data": {...}}`
        if hasattr(record, "data"):
            log_entry["data"] = record.data

        if self.use_color:
            return self._colorize_json(log_entry)

        return json.dumps(log_entry, default=str)


def get_logger(name: str) -> logging.Logger:
    """Create a logger with a structured JSON handler based on the active context."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter(context=settings.log_context))
        logger.addHandler(handler)
        logger.setLevel(settings.log_level.upper())
        logger.propagate = False

    return logger
