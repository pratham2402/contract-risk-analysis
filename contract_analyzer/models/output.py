"""Core data models for contract analysis output."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Decision(str, Enum):
    APPROVE = "approve"
    ESCALATE = "escalate"
    BLOCK = "block"


class Owner(str, Enum):
    LEGAL = "legal"
    FINANCE = "finance"
    PROCUREMENT = "procurement"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    EXECUTIVE = "executive"


class ClauseType(str, Enum):
    LIABILITY = "liability"
    INDEMNIFICATION = "indemnification"
    DATA_PROTECTION = "data_protection"
    TERMINATION = "termination"
    PAYMENT = "payment"
    CONFIDENTIALITY = "confidentiality"
    IP_RIGHTS = "ip_rights"
    SERVICE_LEVEL = "service_level"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    INSURANCE = "insurance"
    WARRANTY = "warranty"
    AUDIT_RIGHTS = "audit_rights"
    SUBCONTRACTING = "subcontracting"
    OTHER = "other"


class StandardRef(BaseModel):
    """Reference to a compliance standard."""

    standard: str
    article: str | None = None
    clause: str | None = None
    description: str
    relevance_score: float = 0.0


class ParsedClause(BaseModel):
    """A clause extracted from a contract."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    clause_type: ClauseType
    clause_number: str | None = None
    title: str = ""
    text: str
    start_line: int = 0
    end_line: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class EscalationTicket(BaseModel):
    """Created when escalate_to_human is called."""

    ticket_id: str
    reason: str
    clause_id: str | None = None
    standard: str | None = None
    severity: str = "medium"
    timestamp: str = ""


class VerificationFlag(BaseModel):
    """A single issue found during verification."""

    finding_id: str
    flag_type: str  # "hallucinated_citation", "unsupported_citation",
                    # "disconnected_reasoning", "risk_level_mismatch",
                    # "generic_exclusion"
    severity: str = "warn"  # "block", "warn", "info"
    detail: str = ""


class VerificationReport(BaseModel):
    """Output of the Verification Agent."""

    verified: bool = True
    total_findings: int = 0
    total_citations: int = 0
    flags: list[VerificationFlag] = Field(default_factory=list)
    hallucination_count: int = 0
    adjusted_confidence: float = 0.0


class Finding(BaseModel):
    """A risk or compliance finding."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    clause_id: str | None = None
    issue_description: str
    risk_level: RiskLevel
    category: str
    referenced_standards: list[StandardRef] = Field(default_factory=list)
    explanation: str
    reasoning_trace: str
    confidence: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)
    verification_status: str = "unverified"  # "unverified", "verified_clean",
                                              # "verified_with_flags", "escalated"
    escalation_ticket: EscalationTicket | None = None


class Recommendation(BaseModel):
    """An actionable recommendation derived from findings."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    finding_id: str
    issue_description: str
    risk_level: RiskLevel
    referenced_standards: list[StandardRef] = Field(default_factory=list)
    explanation: str
    reasoning_trace: str
    recommended_action: str
    negotiation_suggestion: str | None = None
    owner: Owner
    priority: int = Field(ge=1, le=5)
    decision: Decision
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContractAnalysis(BaseModel):
    """Complete contract analysis output."""

    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    contract_name: str = ""
    contract_text: str = ""
    clauses: list[ParsedClause] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    audit_trail: list[dict[str, Any]] = Field(default_factory=list)
    jurisdiction_analysis: dict[str, Any] = Field(default_factory=dict)
    standards_applicability: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    total_duration_ms: float = 0.0
    verification_report: VerificationReport | None = None
    escalation_tickets: list[EscalationTicket] = Field(default_factory=list)

    @model_validator(mode="after")
    def compute_summary(self) -> "ContractAnalysis":
        if not self.summary:
            self.summary = {
                "total_clauses": len(self.clauses),
                "total_findings": len(self.findings),
                "total_recommendations": len(self.recommendations),
                "risk_counts": {
                    level.value: sum(
                        1 for f in self.findings if f.risk_level == level
                    )
                    for level in RiskLevel
                },
                "decision_counts": {
                    d.value: sum(
                        1 for r in self.recommendations if r.decision == d
                    )
                    for d in Decision
                },
            }
        return self
