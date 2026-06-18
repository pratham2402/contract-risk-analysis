"""Tests for structured logging / audit logger."""

import json
import logging

import pytest

from contract_analyzer.logging_setup import AuditLogger, setup_logging


class TestAuditLogger:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Capture log output."""
        self.logger_name = "test_audit"
        self.audit = AuditLogger(self.logger_name, "test_component")
        self.stream = logging.StreamHandler
        # Attach a list handler to capture output
        self.records = []
        self.handler = logging.Handler()
        self.handler.emit = lambda r: self.records.append(r)
        logging.getLogger(self.logger_name).addHandler(self.handler)
        logging.getLogger(self.logger_name).setLevel(logging.DEBUG)
        yield
        logging.getLogger(self.logger_name).removeHandler(self.handler)

    def _last_record(self) -> dict:
        assert self.records, "No log records captured"
        return json.loads(self.records[-1].getMessage())

    def test_info(self):
        self.audit.info("Test message")
        record = self._last_record()
        assert record["component"] == "test_component"
        assert record["event"] == "info"
        assert record["message"] == "Test message"
        assert "trace_id" in record
        assert "timestamp" in record

    def test_info_with_kwargs(self):
        self.audit.info("Analysis complete", findings=5, duration_ms=120.5)
        record = self._last_record()
        assert record["findings"] == 5
        assert record["duration_ms"] == 120.5

    def test_warning(self):
        self.audit.warning("Low confidence finding", confidence=0.4)
        record = self._last_record()
        assert record["event"] == "warning"
        assert record["confidence"] == 0.4

    def test_error(self):
        self.audit.error("Connection failed", service="database")
        record = self._last_record()
        assert record["event"] == "error"
        assert record["service"] == "database"

    def test_audit(self):
        self.audit.audit("User action logged", action="delete", user="admin")
        record = self._last_record()
        assert record["event"] == "audit"
        assert record["action"] == "delete"
        assert record["user"] == "admin"

    def test_agent_call_success(self):
        self.audit.agent_call("risk_compliance", "a2a_call", 250.0, True, specialist="privacy")
        record = self._last_record()
        assert record["event"] == "agent_call"
        assert record["agent"] == "risk_compliance"
        assert record["call_type"] == "a2a_call"
        assert record["duration_ms"] == 250.0
        assert record["success"] is True
        assert record["specialist"] == "privacy"

    def test_agent_call_failure(self):
        self.audit.agent_call("risk_compliance", "a2a_call", 5000.0, False)
        record = self._last_record()
        assert record["success"] is False
        assert record["duration_ms"] == 5000.0

    def test_messages_are_valid_json(self):
        self.audit.info("Message with special chars: / \\ \" '")
        raw = self.records[-1].getMessage()
        parsed = json.loads(raw)
        assert parsed["message"] == "Message with special chars: / \\ \" '"


def test_setup_logging_does_not_crash():
    setup_logging()
    # Verify root logger has a handler
    root = logging.getLogger()
    assert len(root.handlers) >= 1
