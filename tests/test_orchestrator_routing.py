"""Tests for orchestrator routing decisions (pure logic, no LLM/network).

These test the route_after_* methods directly by constructing state dicts.
The orchestrator's ainvoke path is not tested here — it requires live LLM
services. Instead we verify the routing logic is correct.
"""

import pytest

from contract_analyzer.models.output import (
    ClauseType,
    EscalationTicket,
    Finding,
    ParsedClause,
    RiskLevel,
    VerificationFlag,
    VerificationReport,
)
from contract_analyzer.orchestrator.workflow import Orchestrator


def _make_state(**overrides) -> dict:
    """Build a minimal state dict for routing tests."""
    state = {
        "contract_text": "Test contract",
        "contract_name": "Test",
        "messages": [],
        "clauses": [],
        "findings": [],
        "recommendations": [],
        "errors": [],
        "audit_trail": [],
        "current_stage": "init",
        "analysis_complete": False,
        "governing_law": "",
        "party_a_location": "",
        "party_b_location": "",
        "subject_matter": "",
        "verification_enabled": True,
        "verification_report": None,
        "retrieved_evidence": [],
        "escalation_tickets": [],
        "human_review_required": False,
        "jurisdiction_analysis": {},
        "standards_applicability": [],
        "specialist_domain": "",
        "routing_decision": "",
        "routing_reason": "",
        "job_status": "pending",
    }
    state.update(overrides)
    return state


@pytest.fixture
def orch():
    return Orchestrator()


class TestRouteAfterParse:
    def test_route_to_evaluate_risk(self, orch):
        state = _make_state(
            clauses=[
                ParsedClause(
                    id="c1",
                    clause_type=ClauseType.CONFIDENTIALITY,
                    text="Confidentiality obligations here.",
                )
            ]
        )
        result = orch._route_after_parse(state)
        assert result == "evaluate_risk"

    def test_route_to_error_on_empty_clauses(self, orch):
        state = _make_state(clauses=[])
        result = orch._route_after_parse(state)
        assert result == "handle_error"
        assert "No clauses extracted" in state["errors"][-1]

    def test_route_to_error_when_errors_present(self, orch):
        state = _make_state(errors=["Parsing failed"])
        result = orch._route_after_parse(state)
        assert result == "handle_error"

class TestRouteAfterRisk:
    def test_route_to_verify(self, orch):
        finding = Finding(
            issue_description="Issue",
            risk_level=RiskLevel.MEDIUM,
            category="security",
            explanation="E",
            reasoning_trace="T",
        )
        state = _make_state(findings=[finding])
        result = orch._route_after_risk(state)
        assert result == "verify_findings"

    def test_route_to_generate_when_verification_disabled(self, orch):
        finding = Finding(
            issue_description="Issue",
            risk_level=RiskLevel.LOW,
            category="general",
            explanation="E",
            reasoning_trace="T",
        )
        state = _make_state(findings=[finding], verification_enabled=False)
        result = orch._route_after_risk(state)
        assert result == "generate_decisions"

    def test_route_to_finalize_when_no_findings(self, orch):
        state = _make_state()
        result = orch._route_after_risk(state)
        assert result == "finalize"

    def test_route_to_human_review_when_tickets_no_findings(self, orch):
        ticket = EscalationTicket(ticket_id="t1", reason="Uncertain")
        state = _make_state(escalation_tickets=[ticket])
        result = orch._route_after_risk(state)
        assert result == "human_review"

    def test_route_to_human_review_when_findings_and_tickets_and_verification_disabled(self, orch):
        finding = Finding(
            issue_description="Issue",
            risk_level=RiskLevel.MEDIUM,
            category="security",
            explanation="E",
            reasoning_trace="T",
        )
        ticket = EscalationTicket(ticket_id="t1", reason="Uncertain")
        state = _make_state(
            findings=[finding],
            escalation_tickets=[ticket],
            verification_enabled=False,
        )
        result = orch._route_after_risk(state)
        assert result == "human_review"

    def test_route_to_generate_when_findings_no_tickets_and_verification_disabled(self, orch):
        finding = Finding(
            issue_description="Issue",
            risk_level=RiskLevel.LOW,
            category="general",
            explanation="E",
            reasoning_trace="T",
        )
        state = _make_state(findings=[finding], verification_enabled=False)
        result = orch._route_after_risk(state)
        assert result == "generate_decisions"

    def test_route_to_error(self, orch):
        state = _make_state(errors=["Risk eval failed"])
        result = orch._route_after_risk(state)
        assert result == "handle_error"


class TestRouteAfterVerify:
    def test_route_to_generate(self, orch):
        finding = Finding(
            issue_description="Issue",
            risk_level=RiskLevel.MEDIUM,
            category="security",
            explanation="E",
            reasoning_trace="T",
        )
        report = VerificationReport(verified=True, total_citations=5)
        state = _make_state(
            findings=[finding],
            verification_report=report,
        )
        result = orch._route_after_verify(state)
        assert result == "generate_decisions"

    def test_route_to_generate_when_no_report(self, orch):
        state = _make_state()
        result = orch._route_after_verify(state)
        assert result == "generate_decisions"

    def test_route_to_finalize_when_no_findings(self, orch):
        report = VerificationReport(verified=True)
        state = _make_state(verification_report=report)
        result = orch._route_after_verify(state)
        assert result == "finalize"

    def test_route_to_human_review_when_block_threshold_exceeded(self, orch):
        flags = [
            VerificationFlag(finding_id="f1", flag_type="hallucinated_citation", severity="block"),
            VerificationFlag(finding_id="f2", flag_type="unsupported_citation", severity="block"),
            VerificationFlag(finding_id="f3", flag_type="disconnected_reasoning", severity="block"),
        ]
        report = VerificationReport(verified=False, flags=flags)
        state = _make_state(verification_report=report)
        result = orch._route_after_verify(state)
        assert result == "human_review"

    def test_route_to_generate_when_below_threshold(self, orch):
        finding = Finding(
            issue_description="Issue",
            risk_level=RiskLevel.MEDIUM,
            category="security",
            explanation="E",
            reasoning_trace="T",
        )
        flags = [
            VerificationFlag(finding_id="f1", flag_type="generic_exclusion", severity="warn"),
            VerificationFlag(finding_id="f2", flag_type="risk_level_mismatch", severity="warn"),
        ]
        report = VerificationReport(verified=True, flags=flags)
        state = _make_state(findings=[finding], verification_report=report)
        result = orch._route_after_verify(state)
        assert result == "generate_decisions"

    def test_route_to_error(self, orch):
        state = _make_state(errors=["Verification failed"])
        result = orch._route_after_verify(state)
        assert result == "handle_error"


class TestNodeFinalize:
    """Test the finalize node sets correct state markers."""

    @pytest.mark.asyncio
    async def test_finalize_sets_complete(self, orch):
        state = _make_state()
        result = await orch._node_finalize(state)
        assert result["current_stage"] == "complete"
        assert result["analysis_complete"] is True
        assert result["job_status"] == "completed"


class TestNodeHumanReview:
    @pytest.mark.asyncio
    async def test_human_review_sets_state(self, orch):
        state = _make_state()
        result = await orch._node_human_review(state)
        assert result["human_review_required"] is True
        assert result["job_status"] == "needs_review"

    @pytest.mark.asyncio
    async def test_human_review_mentions_escalation_tickets(self, orch):
        ticket = EscalationTicket(ticket_id="t1", reason="Ambiguous clause")
        state = _make_state(escalation_tickets=[ticket])
        result = await orch._node_human_review(state)
        assert "1 escalation ticket" in result["audit_trail"][-1]["reasons"][0]


class TestNodeHandleError:
    @pytest.mark.asyncio
    async def test_handle_error_sets_failed(self, orch):
        state = _make_state(errors=["Something broke"])
        result = await orch._node_handle_error(state)
        assert result["job_status"] == "failed"
        assert result["analysis_complete"] is True
        assert result["current_stage"] == "error"
