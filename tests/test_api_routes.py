"""Tests for API route pydantic models (unit tests, no server needed)."""

import json

import pytest

from contract_analyzer.api.routes import (
    ContractSubmitRequest,
    ContractSubmitResponse,
    JobStatusResponse,
    JobSubmitResponse,
)


class TestContractSubmitRequest:
    def test_minimal_valid(self):
        req = ContractSubmitRequest(text="x" * 10)
        assert req.name == ""
        assert req.async_mode is False

    def test_full(self):
        req = ContractSubmitRequest(name="Test Contract", text="x" * 100, async_mode=True)
        assert req.name == "Test Contract"
        assert req.async_mode is True

    def test_text_too_short(self):
        with pytest.raises(Exception):
            ContractSubmitRequest(text="short")  # less than 10 chars

    def test_empty_text(self):
        with pytest.raises(Exception):
            ContractSubmitRequest(text="")


class TestContractSubmitResponse:
    def test_minimal(self):
        resp = ContractSubmitResponse(
            analysis_id="a1",
            status="completed",
            clause_count=5,
            finding_count=3,
            recommendation_count=2,
            total_duration_ms=1500.0,
            summary={"total_clauses": 5},
        )
        assert resp.analysis_id == "a1"
        assert resp.status == "completed"
        assert resp.clauses == []
        assert resp.findings == []
        assert resp.verification_report is None

    def test_with_optional_fields(self):
        resp = ContractSubmitResponse(
            analysis_id="a2",
            status="completed",
            clause_count=1,
            finding_count=1,
            recommendation_count=1,
            total_duration_ms=800.0,
            summary={"total_clauses": 1},
            clauses=[{"id": "c1", "clause_type": "confidentiality", "text": "Test"}],
            findings=[{"id": "f1", "issue_description": "Issue"}],
            recommendations=[{"id": "r1", "issue_description": "Rec"}],
            jurisdiction_analysis={"governing_law": "Delaware"},
            human_review_required=True,
        )
        assert len(resp.clauses) == 1
        assert resp.human_review_required is True


class TestJobSubmitResponse:
    def test_fields(self):
        resp = JobSubmitResponse(
            job_id="j1",
            status="pending",
            contract_name="Test",
        )
        assert resp.job_id == "j1"
        assert resp.status == "pending"


class TestJobStatusResponse:
    def test_pending_job(self):
        resp = JobStatusResponse(
            job_id="j1",
            contract_name="Test",
            status="pending",
            created_at="2026-01-01T00:00:00Z",
        )
        assert resp.started_at is None
        assert resp.completed_at is None
        assert resp.error is None
        assert resp.result is None

    def test_completed_job(self):
        resp = JobStatusResponse(
            job_id="j2",
            contract_name="Test2",
            status="completed",
            created_at="2026-01-01T00:00:00Z",
            started_at="2026-01-01T00:00:01Z",
            completed_at="2026-01-01T00:00:05Z",
            result={"analysis_id": "a1"},
        )
        assert resp.started_at is not None
        assert resp.completed_at is not None
        assert resp.result is not None
        assert resp.error is None

    def test_failed_job(self):
        resp = JobStatusResponse(
            job_id="j3",
            contract_name="Test3",
            status="failed",
            created_at="2026-01-01T00:00:00Z",
            error="Analysis failed: timeout",
        )
        assert resp.status == "failed"
        assert resp.error == "Analysis failed: timeout"

