"""Risk and Compliance Agent — Genuinely Agentic.

Uses an internal LangGraph ReAct graph where the LLM dynamically decides:
- whether to retrieve standards
- what retrieval queries to issue
- how many retrieval rounds to perform
- when evidence is sufficient
- whether to escalate to human review

LLM-controlled tool invocation within a bounded reasoning cycle.
"""

import json
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from contract_analyzer.agents.react_graph import (
    REACT_SYSTEM_PROMPT,
    AgentState,
    build_react_agent,
)
from contract_analyzer.agents.tools import RISK_AGENT_TOOLS
from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.models.output import Finding, RiskLevel, StandardRef

logger = AuditLogger(__name__, "risk_compliance_agent")


class RiskComplianceProcessor:
    """Agentic risk evaluation using ReAct tool-calling loop.

    The LLM is given tools and decides the retrieval strategy within
    a bounded iteration cap — no hardcoded retrieval in Python.
    """

    def __init__(
        self,
        specialist_domain: str | None = None,
    ) -> None:
        self.llm = ChatOpenAI(
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            temperature=config.llm_temperature,
        )
        self.specialist_domain = specialist_domain
        self.graph = build_react_agent(
            llm=self.llm,
            tools=RISK_AGENT_TOOLS,
        )

    def _build_system_message(self) -> SystemMessage:
        """Build system message with optional specialist domain emphasis."""
        prompt = REACT_SYSTEM_PROMPT
        if self.specialist_domain == "privacy":
            prompt += (
                "\n\n## SPECIALIST FOCUS: DATA PROTECTION & PRIVACY\n"
                "You specialize in GDPR, DPDPA, CCPA/CPRA, HIPAA, FERPA, and GLBA.\n"
                "Prioritize data protection standards over other frameworks.\n"
                "Pay special attention to: personal data definitions, cross-border\n"
                "transfer restrictions, data subject rights, breach notification\n"
                "timelines, and processor obligations.\n"
            )
        elif self.specialist_domain == "financial":
            prompt += (
                "\n\n## SPECIALIST FOCUS: FINANCIAL COMPLIANCE\n"
                "You specialize in SOX, PCI DSS, GLBA Safeguards Rule, and financial\n"
                "reporting controls. Prioritize financial compliance standards.\n"
                "Pay special attention to: ICFR, ITGCs, payment security, internal\n"
                "controls documentation, and auditor attestation requirements.\n"
            )
        return SystemMessage(content=prompt)

    def _format_context_message(
        self,
        clauses: list[dict],
        contract_name: str,
        governing_law: str,
        party_a_location: str,
        party_b_location: str,
        data_subject_locations: str,
        subject_matter: str,
    ) -> HumanMessage:
        """Build the initial context message for the agent."""
        context = {
            "contract_name": contract_name or "Unnamed Contract",
            "governing_law": governing_law or "Not specified",
            "party_a_location": party_a_location or "Not specified",
            "party_b_location": party_b_location or "Not specified",
            "data_subject_locations": data_subject_locations or "Not specified",
            "subject_matter": subject_matter or "Not specified",
            "clauses": clauses,
        }

        return HumanMessage(content=json.dumps({
            "task": "Analyze the following contract clauses for compliance risks.",
            "contract_context": {
                k: v for k, v in context.items() if k != "clauses"
            },
            "clauses": context["clauses"],
            "instructions": (
                "Use your tools to retrieve relevant standards. For each clause, "
                "apply the 3-layer trigger test. Only cite standards you have "
                "actually retrieved. Produce findings in the required JSON format "
                "when you have sufficient evidence."
            ),
        }, indent=2))

    async def process(
        self,
        clauses_json: str,
        contract_name: str = "",
        governing_law: str = "",
        party_a_location: str = "",
        party_b_location: str = "",
        data_subject_locations: str = "",
        subject_matter: str = "",
    ) -> dict:
        """Process clauses through the agentic ReAct loop.

        Same interface for drop-in compatibility with the orchestrator.
        """
        start = time.monotonic()

        # Parse input
        raw_input = json.loads(clauses_json) if isinstance(clauses_json, str) else clauses_json
        if isinstance(raw_input, dict):
            if "contract_name" in raw_input or "governing_law" in raw_input:
                clauses = raw_input.get("clauses", [])
                contract_name = raw_input.get("contract_name", contract_name)
                governing_law = raw_input.get("governing_law", governing_law)
                party_a_location = raw_input.get("party_a_location", party_a_location)
                party_b_location = raw_input.get("party_b_location", party_b_location)
                data_subject_locations = raw_input.get("data_subject_locations", data_subject_locations)
                subject_matter = raw_input.get("subject_matter", subject_matter)
            elif "clauses" in raw_input:
                clauses = raw_input["clauses"]
            else:
                clauses = [raw_input]
        elif isinstance(raw_input, list):
            clauses = raw_input
        else:
            clauses = [raw_input]

        # Initialize ReAct state
        initial_state: AgentState = {
            "messages": [
                self._build_system_message(),
                self._format_context_message(
                    clauses=clauses,
                    contract_name=contract_name,
                    governing_law=governing_law,
                    party_a_location=party_a_location,
                    party_b_location=party_b_location,
                    data_subject_locations=data_subject_locations,
                    subject_matter=subject_matter,
                ),
            ],
            "iteration_count": 0,
            "contract_context": {
                "contract_name": contract_name,
                "governing_law": governing_law,
                "party_a_location": party_a_location,
                "party_b_location": party_b_location,
                "subject_matter": subject_matter,
            },
            "clauses": clauses,
            "tool_call_history": [],
            "escalation_tickets": [],
            "final_output": {},
        }

        # Run ReAct loop
        logger.info(
            "Starting ReAct analysis",
            clause_count=len(clauses),
            governing_law=governing_law,
            specialist=self.specialist_domain,
        )

        final_state = await self.graph.ainvoke(initial_state)

        # Extract output
        final_output = final_state.get("final_output", {})
        iteration_count = final_state.get("iteration_count", 0)

        # ── Collect retrieved evidence from tool messages ─────────
        retrieved_evidence: list[dict] = []
        seen_keys: set[str] = set()
        for msg in final_state.get("messages", []):
            if hasattr(msg, "content") and hasattr(msg, "name") and msg.name == "retrieve_standards":
                try:
                    data = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                    for r in data.get("results", []):
                        key = f"{r.get('standard', '')}|{r.get('article') or 'none'}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            retrieved_evidence.append({
                                "standard": r.get("standard", ""),
                                "article": r.get("article"),
                                "title": r.get("title", ""),
                                "content": r.get("content", ""),
                                "score": r.get("score", 0),
                                "jurisdiction": r.get("jurisdiction", "Global"),
                                "category": r.get("category", "general"),
                            })
                except (json.JSONDecodeError, TypeError, AttributeError):
                    pass

        # Parse findings into Pydantic models
        data = final_output if isinstance(final_output, dict) else {}
        findings = []
        for item in data.get("findings", []):
            try:
                risk_level = RiskLevel(item.get("risk_level", "info"))
            except ValueError:
                risk_level = RiskLevel.INFO

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

            findings.append(
                Finding(
                    clause_id=item.get("clause_id"),
                    issue_description=item.get("issue_description", ""),
                    risk_level=risk_level,
                    category=item.get("category", ""),
                    referenced_standards=std_refs,
                    explanation=item.get("explanation", ""),
                    reasoning_trace=item.get("reasoning_trace", ""),
                    confidence=item.get("confidence", 1.0),
                )
            )

        duration_ms = (time.monotonic() - start) * 1000
        logger.agent_call(
            "risk_compliance",
            "process",
            duration_ms,
            True,
            finding_count=len(findings),
            react_iterations=iteration_count,
            specialist=self.specialist_domain,
        )

        return {
            "findings": [f.model_dump() for f in findings],
            "total_findings": len(findings),
            "retrieved_evidence": retrieved_evidence,
            "jurisdiction_analysis": data.get("jurisdiction_analysis", {}),
            "standards_applicability": data.get("standards_applicability", []),
            "processing_time_ms": duration_ms,
            "react_iterations": iteration_count,
        }

# Global processor instances
risk_processor = RiskComplianceProcessor()
risk_processor_privacy = RiskComplianceProcessor(specialist_domain="privacy")
risk_processor_financial = RiskComplianceProcessor(specialist_domain="financial")
