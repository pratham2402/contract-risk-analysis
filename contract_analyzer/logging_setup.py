"""Structured logging with audit trail support."""

import json
import logging
import sys
import time
import uuid
from datetime import UTC, datetime
from typing import Any


class AuditLogger:
    """JSON-structured logger with built-in audit trail capabilities."""

    def __init__(self, name: str, component: str) -> None:
        self.logger = logging.getLogger(name)
        self.component = component

    def _log(
        self,
        level: int,
        msg: str,
        event: str,
        trace_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": self.component,
            "event": event,
            "message": msg,
            "trace_id": trace_id or str(uuid.uuid4()),
            **kwargs,
        }
        self.logger.log(level, json.dumps(record, default=str))

    def info(self, msg: str, event: str = "info", **kwargs: Any) -> None:
        self._log(logging.INFO, msg, event, **kwargs)

    def warning(self, msg: str, event: str = "warning", **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, event, **kwargs)

    def error(self, msg: str, event: str = "error", **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, event, **kwargs)

    def audit(self, msg: str, event: str = "audit", **kwargs: Any) -> None:
        """Permanent audit trail entry."""
        self._log(logging.INFO, msg, event, **kwargs)

    def agent_call(
        self,
        agent: str,
        call_type: str,
        duration_ms: float,
        success: bool,
        **kwargs: Any,
    ) -> None:
        self.audit(
            f"{call_type} call to {agent} {'succeeded' if success else 'failed'}",
            event="agent_call",
            agent=agent,
            call_type=call_type,
            duration_ms=duration_ms,
            success=success,
            **kwargs,
        )


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with JSON formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
