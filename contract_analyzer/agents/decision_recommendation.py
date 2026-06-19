"""Decision and Recommendation Agent.

Converts risk findings into actionable recommendations with clear ownership,
priority, negotiation suggestions, and final decisions.
"""

import json
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.models.output import Decision, Owner, Recommendation, RiskLevel, StandardRef

logger = AuditLogger(__name__, "decision_recommendation_agent")

SYSTEM_PROMPT = """You are a senior contract negotiator and legal strategist. Your job
is to convert risk and compliance findings into concrete, actionable recommendations.

For each finding, produce a recommendation with:

- issue_description: same as the finding
- risk_level: same as the finding
- referenced_standards: same as the finding
- explanation: summary of the risk
- reasoning_trace: summary of how the conclusion was reached

- recommended_action: specific, concrete action to address the issue. Include exact
  language changes to propose, specific contract clauses to add/modify, or concrete
  operational measures to implement. Be prescriptive, not vague.

- negotiation_suggestion: if applicable, what to say or propose in negotiation.
  Include fallback positions and red lines. Set to null if negotiation is not the
  remedy (e.g., the clause is simply non-compliant and must be fixed).

- owner: who is responsible. One of:
  - legal: contract terms, liability, indemnification, IP, governing law
  - finance: payment terms, financial exposure, insurance requirements
  - procurement: vendor management, SLA terms, delivery obligations
  - security: data security, encryption, access controls, incident response
  - compliance: regulatory obligations, data protection, audit requirements
  - executive: critical issues requiring senior leadership decision

- priority: integer 1-5. 1=immediate action required (critical regulatory violation),
  2=address before signing, 3=address within 30 days after signing, 4=monitor and
  address at next review, 5=acknowledge, no immediate action needed

- decision: one of:
  - block: cannot proceed, issue must be resolved before any further steps
  - escalate: requires senior review and sign-off before proceeding
  - approve: acceptable as-is or with recommended changes

Rules:
- Match the decision to the risk level: critical findings generally require block or
  escalate; high findings escalate or approve with action; medium/low findings usually
  approve with recommended changes
- Be practical: recommendations should be implementable
- Prioritize regulatory compliance over business convenience
- Every recommendation must have a single clear owner
- Multiple findings may be consolidated if they relate to the same underlying issue

Output a JSON object with a "recommendations" array. Return ONLY valid JSON."""


USER_PROMPT_TEMPLATE = """## Contract Name
{contract_name}

## Risk and Compliance Findings

{findings_json}

## Contract Clauses

{clauses_json}

Convert each finding into an actionable recommendation. Be specific and prescriptive.
For regulatory findings, recommend exact language compliant with the specific standard
cited (GDPR, DPDPA, CCPA, HIPAA, PCI DSS, etc.). For security findings, recommend
specific controls from the applicable framework (ISO 27001, NIST CSF, SOC 2, FedRAMP).
For contract law findings, cite specific sections of the applicable contract law
(US_RESTATEMENT, US_UCC, US_DGCL for US-governed contracts; IND_CONTRACT, IT_ACT
for Indian-law-governed contracts). For service delivery issues, recommend specific
SLA language.

Output JSON with a "recommendations" array."""


class DecisionRecommendationProcessor:
    """Core logic for converting findings into actionable recommendations."""

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            temperature=config.llm_temperature,
        )

    async def process(self, findings_json: str, clauses_json: str = "[]", contract_name: str = "") -> dict:
        """Convert findings into recommendations with decisions."""
        start = time.monotonic()

        findings = json.loads(findings_json) if isinstance(findings_json, str) else findings_json
        if isinstance(findings, dict) and "findings" in findings:
            findings = findings["findings"]

        clauses = json.loads(clauses_json) if isinstance(clauses_json, str) else clauses_json
        if isinstance(clauses, dict) and "clauses" in clauses:
            clauses = clauses["clauses"]

        if not findings:
            return {
                "recommendations": [],
                "total_recommendations": 0,
                "processing_time_ms": 0,
            }

        response = await self.llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=USER_PROMPT_TEMPLATE.format(
                    contract_name=contract_name or "Unnamed Contract",
                    findings_json=json.dumps(findings, indent=2),
                    clauses_json=json.dumps(clauses, indent=2),
                )
            ),
        ])

        try:
            raw = response.content.strip()  # type: ignore[union-attr]
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try json_repair before giving up
            try:
                from json_repair import repair_json
                fixed = repair_json(raw)
                data = json.loads(fixed)
            except Exception as e2:
                logger.error(f"Failed to parse LLM output: {e2}", raw=raw[:500])
                return {"recommendations": [], "error": str(e2), "raw_output": raw[:1000]}

        recommendations = []
        for item in data.get("recommendations", []):
            try:
                risk_level = RiskLevel(item.get("risk_level", "info"))
            except ValueError:
                risk_level = RiskLevel.INFO

            try:
                owner = Owner(item.get("owner", "legal"))
            except ValueError:
                owner = Owner.LEGAL

            try:
                decision = Decision(item.get("decision", "approve"))
            except ValueError:
                decision = Decision.APPROVE

            std_refs = []
            for ref in item.get("referenced_standards", []):
                std_refs.append(
                    StandardRef(
                        standard=ref.get("standard", ""),
                        article=ref.get("article"),
                        clause=ref.get("clause"),
                        description=ref.get("description", ""),
                        relevance_score=ref.get("relevance_score", 0.0),
                    )
                )

            recommendations.append(
                Recommendation(
                    finding_id=item.get("finding_id", ""),
                    issue_description=item.get("issue_description", ""),
                    risk_level=risk_level,
                    referenced_standards=std_refs,
                    explanation=item.get("explanation", ""),
                    reasoning_trace=item.get("reasoning_trace", ""),
                    recommended_action=item.get("recommended_action", ""),
                    negotiation_suggestion=item.get("negotiation_suggestion"),
                    owner=owner,
                    priority=item.get("priority", 3),
                    decision=decision,
                )
            )

        duration_ms = (time.monotonic() - start) * 1000
        logger.agent_call(
            "decision_recommendation",
            "process",
            duration_ms,
            True,
            recommendation_count=len(recommendations),
        )

        return {
            "recommendations": [r.model_dump() for r in recommendations],
            "total_recommendations": len(recommendations),
            "processing_time_ms": duration_ms,
        }

decision_processor = DecisionRecommendationProcessor()
