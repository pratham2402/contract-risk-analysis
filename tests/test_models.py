"""Tests for pydantic output models."""

import pytest

from contract_analyzer.models.output import (
    ClauseType,
    ContractAnalysis,
    Decision,
    EscalationTicket,
    Finding,
    Owner,
    ParsedClause,
    Recommendation,
    RiskLevel,
    StandardRef,
    VerificationFlag,
    VerificationReport,
)


class TestRiskLevel:
    def test_all_levels_present(self):
        assert {e.value for e in RiskLevel} == {"critical", "high", "medium", "low", "info"}

    def test_comparison(self):
        levels = list(RiskLevel)
        assert levels[0] == RiskLevel.CRITICAL


class TestDecision:
    def test_all_decisions_present(self):
        assert {d.value for d in Decision} == {"approve", "escalate", "block"}


class TestOwner:
    def test_all_owners_present(self):
        assert set(Owner) == {
            Owner.LEGAL, Owner.FINANCE, Owner.PROCUREMENT,
            Owner.SECURITY, Owner.COMPLIANCE, Owner.EXECUTIVE,
        }


class TestClauseType:
    def test_all_types_present(self):
        values = {c.value for c in ClauseType}
        expected = {
            "liability", "indemnification", "data_protection", "termination",
            "payment", "confidentiality", "ip_rights", "service_level",
            "force_majeure", "governing_law", "insurance", "warranty",
            "audit_rights", "subcontracting", "other",
        }
        assert values == expected


class TestStandardRef:
    def test_minimal_ref(self):
        ref = StandardRef(standard="GDPR", description="Processing of personal data")
        assert ref.article is None
        assert ref.clause is None
        assert ref.relevance_score == 0.0

    def test_full_ref(self):
        ref = StandardRef(
            standard="GDPR",
            article="Art. 32",
            clause="1(a)",
            description="Encryption",
            relevance_score=0.92,
        )
        assert ref.standard == "GDPR"
        assert ref.article == "Art. 32"
        assert ref.clause == "1(a)"
        assert ref.relevance_score == 0.92


class TestParsedClause:
    def test_defaults(self):
        clause = ParsedClause(clause_type=ClauseType.OTHER, text="Test clause text")
        assert clause.id  # auto-generated
        assert clause.clause_number is None
        assert clause.title == ""
        assert clause.start_line == 0
        assert clause.end_line == 0
        assert clause.metadata == {}

    def test_full_clause(self):
        clause = ParsedClause(
            id="c1",
            clause_type=ClauseType.CONFIDENTIALITY,
            clause_number="2.1",
            title="Obligations",
            text="Receiving Party shall hold info in confidence.",
            start_line=10,
            end_line=12,
            metadata={"severity": "high"},
        )
        assert clause.id == "c1"
        assert clause.clause_type == ClauseType.CONFIDENTIALITY
        assert clause.metadata["severity"] == "high"


class TestEscalationTicket:
    def test_minimal(self):
        ticket = EscalationTicket(ticket_id="t1", reason="Needs human review")
        assert ticket.ticket_id == "t1"
        assert ticket.clause_id is None
        assert ticket.severity == "medium"
        assert ticket.timestamp == ""

    def test_full(self):
        ticket = EscalationTicket(
            ticket_id="t2",
            reason="Contradictory standards",
            clause_id="c5",
            standard="GDPR",
            severity="high",
            timestamp="2026-01-15T10:00:00Z",
        )
        assert ticket.severity == "high"
        assert ticket.standard == "GDPR"


class TestVerificationFlag:
    def test_defaults(self):
        flag = VerificationFlag(finding_id="f1", flag_type="hallucinated_citation")
        assert flag.severity == "warn"
        assert flag.detail == ""

    def test_block_flag(self):
        flag = VerificationFlag(
            finding_id="f2",
            flag_type="unsupported_citation",
            severity="block",
            detail="Cited GDPR Art. 99 which does not exist",
        )
        assert flag.severity == "block"
        assert "GDPR" in flag.detail


class TestVerificationReport:
    def test_defaults(self):
        report = VerificationReport()
        assert report.verified is True
        assert report.total_findings == 0
        assert report.total_citations == 0
        assert report.flags == []
        assert report.hallucination_count == 0
        assert report.adjusted_confidence == 0.0

    def test_with_flags(self):
        flags = [
            VerificationFlag(finding_id="f1", flag_type="hallucinated_citation"),
            VerificationFlag(finding_id="f2", flag_type="generic_exclusion"),
        ]
        report = VerificationReport(
            verified=False,
            total_findings=2,
            total_citations=5,
            flags=flags,
            hallucination_count=1,
            adjusted_confidence=0.6,
        )
        assert report.verified is False
        assert len(report.flags) == 2


class TestFinding:
    def test_defaults(self):
        finding = Finding(
            issue_description="Test issue",
            risk_level=RiskLevel.LOW,
            category="general",
            explanation="Test explanation",
            reasoning_trace="Step 1",
        )
        assert finding.id
        assert finding.confidence == 1.0
        assert finding.referenced_standards == []
        assert finding.verification_status == "unverified"
        assert finding.escalation_ticket is None

    def test_with_ticket(self):
        ticket = EscalationTicket(ticket_id="t1", reason="Uncertain")
        finding = Finding(
            issue_description="Ambiguous clause",
            risk_level=RiskLevel.HIGH,
            category="liability",
            explanation="Cannot determine liability cap",
            reasoning_trace="Step 1: Read clause. Step 2: Standards inconclusive.",
            confidence=0.5,
            verification_status="escalated",
            escalation_ticket=ticket,
        )
        assert finding.confidence == 0.5
        assert finding.verification_status == "escalated"
        assert finding.escalation_ticket.ticket_id == "t1"


class TestRecommendation:
    def test_valid_recommendation(self):
        rec = Recommendation(
            finding_id="f1",
            issue_description="Weak encryption clause",
            risk_level=RiskLevel.MEDIUM,
            explanation="Clause lacks specific algorithm requirements",
            reasoning_trace="Step 1: Compare with GDPR Art. 32",
            recommended_action="Mandate AES-256-GCM for data at rest",
            owner=Owner.SECURITY,
            priority=3,
            decision=Decision.ESCALATE,
        )
        assert rec.owner == Owner.SECURITY
        assert rec.priority == 3
        assert rec.decision == Decision.ESCALATE
        assert rec.negotiation_suggestion is None

    def test_priority_bounds(self):
        rec = Recommendation(
            finding_id="f1",
            issue_description="Issue",
            risk_level=RiskLevel.INFO,
            explanation="Info",
            reasoning_trace="Trace",
            recommended_action="Action",
            owner=Owner.LEGAL,
            priority=1,
            decision=Decision.APPROVE,
        )
        assert rec.priority == 1

        rec2 = Recommendation(
            finding_id="f2",
            issue_description="Critical issue",
            risk_level=RiskLevel.CRITICAL,
            explanation="Critical",
            reasoning_trace="Trace",
            recommended_action="Action",
            owner=Owner.EXECUTIVE,
            priority=5,
            decision=Decision.BLOCK,
        )
        assert rec2.priority == 5


class TestContractAnalysis:
    def test_empty_analysis(self):
        analysis = ContractAnalysis(contract_name="Test")
        assert analysis.contract_name == "Test"
        assert analysis.clauses == []
        assert analysis.findings == []
        assert analysis.recommendations == []
        # summary auto-computed by model_validator
        assert analysis.summary["total_clauses"] == 0
        assert analysis.summary["total_findings"] == 0

    def test_summary_computation(self, sample_clause, sample_finding):
        analysis = ContractAnalysis(
            contract_name="Test Contract",
            clauses=[sample_clause],
            findings=[sample_finding],
            recommendations=[],
        )
        assert analysis.summary["total_clauses"] == 1
        assert analysis.summary["total_findings"] == 1
        assert analysis.summary["risk_counts"]["medium"] == 1
        assert analysis.summary["risk_counts"]["critical"] == 0

    def test_summary_overwrites_empty(self, sample_clause, sample_finding):
        """When summary is empty dict, the validator computes it."""
        analysis = ContractAnalysis(
            contract_name="Test",
            clauses=[sample_clause],
            findings=[sample_finding],
            summary={},
        )
        assert analysis.summary["total_clauses"] == 1

    def test_summary_preserves_non_empty(self):
        """When summary already has content, it is preserved."""
        pre_summary = {"custom_key": "value"}
        analysis = ContractAnalysis(
            contract_name="Test",
            summary=pre_summary,
        )
        assert analysis.summary == {"custom_key": "value"}

    def test_timestamps(self):
        analysis = ContractAnalysis(contract_name="T")
        assert analysis.created_at is not None
        assert analysis.analysis_id  # auto-generated uuid

    def test_risk_count_distribution(self):
        f1 = Finding(
            issue_description="Critical issue",
            risk_level=RiskLevel.CRITICAL,
            category="security",
            explanation="E",
            reasoning_trace="T",
        )
        f2 = Finding(
            issue_description="High issue",
            risk_level=RiskLevel.HIGH,
            category="privacy",
            explanation="E",
            reasoning_trace="T",
        )
        f3 = Finding(
            issue_description="Info",
            risk_level=RiskLevel.INFO,
            category="general",
            explanation="E",
            reasoning_trace="T",
        )

        analysis = ContractAnalysis(contract_name="T", findings=[f1, f2, f3])
        rc = analysis.summary["risk_counts"]
        assert rc["critical"] == 1
        assert rc["high"] == 1
        assert rc["medium"] == 0
        assert rc["low"] == 0
        assert rc["info"] == 1

    def test_decision_counts(self):
        r1 = Recommendation(
            finding_id="f1",
            issue_description="Issue 1",
            risk_level=RiskLevel.HIGH,
            explanation="E",
            reasoning_trace="T",
            recommended_action="Fix",
            owner=Owner.LEGAL,
            priority=1,
            decision=Decision.APPROVE,
        )
        r2 = Recommendation(
            finding_id="f2",
            issue_description="Issue 2",
            risk_level=RiskLevel.CRITICAL,
            explanation="E",
            reasoning_trace="T",
            recommended_action="Block",
            owner=Owner.EXECUTIVE,
            priority=5,
            decision=Decision.BLOCK,
        )
        analysis = ContractAnalysis(
            contract_name="T",
            recommendations=[r1, r2],
        )
        dc = analysis.summary["decision_counts"]
        assert dc["approve"] == 1
        assert dc["block"] == 1
        assert dc["escalate"] == 0
