"""LangGraph Orchestrator Workflow — Contract Compliance Pipeline.

Coordinates the contract analysis pipeline using LangGraph's StateGraph with
conditional routing, specialist dispatch, verification gating, and human-review
escalation paths.

Pipeline:
  START → parse_contract (includes classification) → [route specialist]
       → evaluate_risk → [verification gate] → verify_findings
       → generate_decisions → finalize → END

All components run in-process. The Risk & Compliance agent uses a ReAct
reasoning loop with tool calling; other components are single-pass LLM calls.
"""

import json
import time
from datetime import UTC, datetime
from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from contract_analyzer.agents.contract_understanding import processor as contract_processor
from contract_analyzer.agents.decision_recommendation import decision_processor
from contract_analyzer.agents.risk_compliance import (
    risk_processor,
    risk_processor_financial,
    risk_processor_privacy,
)
from contract_analyzer.agents.verification import verification_processor
from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.models.output import (
    ContractAnalysis,
    Finding,
    ParsedClause,
    Recommendation,
    VerificationReport,
)
from contract_analyzer.models.state import OrchestratorState

logger = AuditLogger(__name__, "orchestrator")


class Orchestrator:
    """LangGraph-based orchestrator with dynamic routing and verification."""

    def __init__(self) -> None:
        self.workflow = self._build_workflow()

    def _pick_risk_processor(self, state: OrchestratorState):
        """Return the risk processor for the selected specialist domain."""
        specialist = state.get("specialist_domain", "generalist")
        if specialist == "privacy":
            return risk_processor_privacy
        elif specialist == "financial":
            return risk_processor_financial
        return risk_processor

    def _build_workflow(self) -> StateGraph:
        """Build the dynamic LangGraph StateGraph for contract analysis."""
        graph = StateGraph(dict)

        graph.add_node("parse_contract", self._node_parse_contract)
        graph.add_node("evaluate_risk", self._node_evaluate_risk)
        graph.add_node("verify_findings", self._node_verify_findings)
        graph.add_node("generate_decisions", self._node_generate_decisions)
        graph.add_node("human_review", self._node_human_review)
        graph.add_node("finalize", self._node_finalize)
        graph.add_node("handle_error", self._node_handle_error)

        graph.add_edge(START, "parse_contract")

        graph.add_conditional_edges(
            "parse_contract",
            self._route_after_parse,
            {"evaluate_risk": "evaluate_risk", "handle_error": "handle_error"},
        )

        graph.add_conditional_edges(
            "evaluate_risk",
            self._route_after_risk,
            {
                "verify_findings": "verify_findings",
                "generate_decisions": "generate_decisions",
                "finalize": "finalize",
                "human_review": "human_review",
                "handle_error": "handle_error",
            },
        )

        graph.add_conditional_edges(
            "verify_findings",
            self._route_after_verify,
            {
                "generate_decisions": "generate_decisions",
                "human_review": "human_review",
                "finalize": "finalize",
                "handle_error": "handle_error",
            },
        )

        graph.add_edge("generate_decisions", "finalize")
        graph.add_edge("finalize", END)
        graph.add_edge("human_review", END)
        graph.add_edge("handle_error", END)

        return graph.compile()

    # ── Node implementations ─────────────────────────────────

    async def _node_parse_contract(self, state: OrchestratorState) -> dict:
        """Parse contract via LLM, then classify content for specialist routing."""
        logger.info("Parsing contract", contract_name=state["contract_name"])
        state["current_stage"] = "parsing"
        state["job_status"] = "running"
        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "contract_parsing",
            "action": "parsing_contract",
        })

        try:
            result = await contract_processor.process(state["contract_text"])

            state["clauses"] = [
                ParsedClause(**c) for c in result.get("clauses", [])
            ]
            state["governing_law"] = result.get("governing_law", "")
            state["party_a_location"] = result.get("party_a_location", "")
            state["party_b_location"] = result.get("party_b_location", "")
            state["contract_type"] = result.get("contract_type", "")
            state["subject_matter"] = result.get("subject_matter", "")
            state["data_involved"] = result.get("data_involved", [])

            state["audit_trail"].append({
                "timestamp": datetime.now(UTC).isoformat(),
                "stage": "contract_parsing",
                "action": "parsing_complete",
                "clause_count": len(state["clauses"]),
                "contract_type": state["contract_type"],
                "governing_law_extracted": bool(state["governing_law"]),
            })

            # ── Classify content for specialist routing (keyword-based) ──
            self._classify_for_routing(state)

        except Exception as e:
            state["errors"].append(f"Contract parsing failed: {e}")
            logger.error(f"Contract parsing failed: {e}")

        return state

    def _classify_for_routing(self, state: OrchestratorState) -> None:
        """Simple keyword-based classification to pick specialist risk agent.

        Merged into parse_contract — not a separate node since it's deterministic
        keyword matching, not an agentic operation.
        """
        contract_type = (state.get("contract_type") or "").lower()
        subject_matter = (state.get("subject_matter") or "").lower()
        raw_data = [d.lower().replace("_", " ") for d in (state.get("data_involved") or [])]
        contract_text = (state.get("contract_text") or "").lower()[:5000]

        combined_text = f"{contract_type} {subject_matter} {' '.join(raw_data)} {contract_text}"

        privacy_signals = [
            "data protection", "data processing", "personal data",
            "gdpr", "ccpa", "dpdpa", "privacy", "data subject",
            "cross-border", "data transfer", "processor", "controller",
            "hipaa", "protected health", "phi", "health data",
            "breach notification", "data subject request",
        ]
        financial_signals = [
            "financial", "sox", "pci dss", "payment card", "cardholder",
            "internal control", "icfr", "itgc", "safeguards",
            "glba", "nonpublic personal", "financial reporting",
            "payment", "tax", "invoice",
        ]

        privacy_score = sum(1 for sig in privacy_signals if sig in combined_text)
        financial_score = sum(1 for sig in financial_signals if sig in combined_text)

        if privacy_score >= 2:
            specialist = "privacy"
        elif financial_score >= 2:
            specialist = "financial"
        else:
            specialist = "generalist"

        state["specialist_domain"] = specialist
        state["routing_decision"] = specialist
        state["routing_reason"] = (
            f"privacy_score={privacy_score}, financial_score={financial_score}"
        )

        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "content_classification",
            "action": "routing_decided",
            "specialist": specialist,
            "privacy_score": privacy_score,
            "financial_score": financial_score,
        })

        logger.info("Content classified", specialist=specialist,
                    privacy_score=privacy_score, financial_score=financial_score)

    async def _node_evaluate_risk(self, state: OrchestratorState) -> dict:
        """Evaluate risk via the Risk & Compliance Agent (ReAct loop with tools).

        Runs in-process — the LLM uses a ReAct reasoning loop with dynamic
        tool calling to retrieve standards and produce findings.
        """
        specialist = state.get("specialist_domain", "generalist")
        state["current_stage"] = "risk_evaluation"

        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "risk_evaluation",
            "action": "calling_risk_agent",
            "specialist": specialist,
        })

        clauses_json = json.dumps({
            "clauses": [c.model_dump() for c in state["clauses"]],
            "contract_name": state.get("contract_name", ""),
            "governing_law": state.get("governing_law", ""),
            "party_a_location": state.get("party_a_location", ""),
            "party_b_location": state.get("party_b_location", ""),
            "data_subject_locations": "",
            "subject_matter": state.get("subject_matter", ""),
        })

        try:
            processor = self._pick_risk_processor(state)
            result = await processor.process(clauses_json)

            findings = [Finding(**f) for f in result.get("findings", [])]
            state["findings"] = findings
            state["retrieved_evidence"] = result.get("retrieved_evidence", [])
            state["jurisdiction_analysis"] = result.get("jurisdiction_analysis", {})
            state["standards_applicability"] = result.get("standards_applicability", [])

            tickets = [
                f.escalation_ticket for f in findings if f.escalation_ticket
            ]
            state["escalation_tickets"] = tickets
            state["human_review_required"] = len(tickets) > 0

            state["audit_trail"].append({
                "timestamp": datetime.now(UTC).isoformat(),
                "stage": "risk_evaluation",
                "action": "risk_evaluation_complete",
                "finding_count": len(findings),
                "react_iterations": result.get("react_iterations", 0),
                "escalation_tickets": len(tickets),
                "specialist": specialist,
            })

            logger.info(
                "Risk evaluation complete",
                findings=len(findings),
                specialist=specialist,
                tickets=len(tickets),
            )
        except Exception as e:
            state["errors"].append(f"Risk evaluation failed: {e}")
            logger.error(f"Risk evaluation failed: {e}")

        return state

    async def _node_verify_findings(self, state: OrchestratorState) -> dict:
        """Verify findings via direct LLM call (not an agentic operation)."""
        if not state.get("verification_enabled", True):
            state["audit_trail"].append({
                "timestamp": datetime.now(UTC).isoformat(),
                "stage": "verification",
                "action": "verification_skipped",
                "reason": "verification_disabled",
            })
            return state

        findings = state.get("findings", [])
        evidence = state.get("retrieved_evidence", [])
        state["current_stage"] = "verifying"

        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "verification",
            "action": "verifying_findings",
            "finding_count": len(findings),
            "evidence_count": len(evidence),
        })

        logger.info("Verifying findings", finding_count=len(findings), evidence_count=len(evidence))

        try:
            result = await verification_processor.process(
                findings_json=json.dumps([f.model_dump() for f in findings]),
                evidence_json=json.dumps(evidence),
            )

            report_data = result.get("verification_report", {})
            state["verification_report"] = VerificationReport(**report_data)

            flags = state["verification_report"].flags
            flagged_ids = {f.finding_id for f in flags}
            for finding in state["findings"]:
                finding.verification_status = (
                    "verified_with_flags" if finding.id in flagged_ids else "verified_clean"
                )

            state["audit_trail"].append({
                "timestamp": datetime.now(UTC).isoformat(),
                "stage": "verification",
                "action": "verification_complete",
                "verified": state["verification_report"].verified,
                "flag_count": len(flags),
                "hallucination_count": state["verification_report"].hallucination_count,
            })

            logger.info(
                "Verification complete",
                verified=state["verification_report"].verified,
                flags=len(flags),
            )
        except Exception as e:
            state["errors"].append(f"Verification failed: {e}")
            logger.error(f"Verification failed: {e}")

        return state

    async def _node_generate_decisions(self, state: OrchestratorState) -> dict:
        """Generate decisions via direct LLM call (not an agentic operation)."""
        findings = state.get("findings", [])
        logger.info("Generating decisions", finding_count=len(findings))
        state["current_stage"] = "decision_generation"
        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "decision_generation",
            "action": "generating_recommendations",
        })

        try:
            result = await decision_processor.process(
                findings_json=json.dumps([f.model_dump() for f in findings]),
                clauses_json=json.dumps([c.model_dump() for c in state["clauses"]]),
                contract_name=state["contract_name"],
            )

            state["recommendations"] = [
                Recommendation(**r) for r in result.get("recommendations", [])
            ]
            state["audit_trail"].append({
                "timestamp": datetime.now(UTC).isoformat(),
                "stage": "decision_generation",
                "action": "decisions_complete",
                "recommendation_count": len(state["recommendations"]),
            })
        except Exception as e:
            state["errors"].append(f"Decision generation failed: {e}")
            logger.error(f"Decision generation failed: {e}")

        return state

    async def _node_human_review(self, state: OrchestratorState) -> dict:
        """Mark analysis as requiring human review, but still generate recommendations."""
        state["current_stage"] = "human_review"
        state["analysis_complete"] = True
        state["human_review_required"] = True
        state["job_status"] = "needs_review"

        # Generate recommendations even when human review is required —
        # the recommendations will be flagged for review rather than absent.
        findings = state.get("findings", [])
        if findings:
            logger.info("Generating decisions (human review path)", finding_count=len(findings))
            try:
                result = await decision_processor.process(
                    findings_json=json.dumps([f.model_dump() for f in findings]),
                    clauses_json=json.dumps([c.model_dump() for c in state["clauses"]]),
                    contract_name=state["contract_name"],
                )
                state["recommendations"] = [
                    Recommendation(**r) for r in result.get("recommendations", [])
                ]
                state["audit_trail"].append({
                    "timestamp": datetime.now(UTC).isoformat(),
                    "stage": "human_review",
                    "action": "recommendations_generated",
                    "recommendation_count": len(state["recommendations"]),
                })
            except Exception as e:
                state["errors"].append(f"Decision generation failed: {e}")
                logger.error(f"Decision generation failed (human review path): {e}")

        tickets = state.get("escalation_tickets", [])
        verification = state.get("verification_report")

        reasons = []
        if tickets:
            reasons.append(f"{len(tickets)} escalation ticket(s)")
        if verification and not verification.verified:
            reasons.append(f"verification failed with {len(verification.flags)} flag(s)")

        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "human_review",
            "action": "human_review_required",
            "reasons": reasons,
            "escalation_tickets": [t.model_dump() for t in tickets] if tickets else [],
        })

        logger.warning("Human review required", reasons=reasons, ticket_count=len(tickets))
        return state

    async def _node_finalize(self, state: OrchestratorState) -> dict:
        """Assemble final output."""
        state["current_stage"] = "complete"
        state["analysis_complete"] = True
        state["job_status"] = "completed"
        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "finalize",
            "action": "analysis_complete",
        })
        return state

    async def _node_handle_error(self, state: OrchestratorState) -> dict:
        """Handle errors gracefully with partial results."""
        state["current_stage"] = "error"
        state["analysis_complete"] = True
        state["job_status"] = "failed"
        logger.warning(
            "Analysis completed with errors",
            error_count=len(state["errors"]),
            errors=state["errors"],
        )
        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "error",
            "action": "error_handler",
            "errors": state["errors"],
        })
        return state

    # ── Routing functions ────────────────────────────────────

    def _route_after_parse(
        self, state: OrchestratorState
    ) -> Literal["evaluate_risk", "handle_error"]:
        if state.get("errors"):
            return "handle_error"
        if not state.get("clauses"):
            state["errors"].append("No clauses extracted from contract text")
            return "handle_error"
        return "evaluate_risk"

    def _route_after_risk(
        self, state: OrchestratorState
    ) -> Literal["verify_findings", "generate_decisions", "finalize", "human_review", "handle_error"]:
        if state.get("errors"):
            return "handle_error"

        findings = state.get("findings", [])
        tickets = state.get("escalation_tickets", [])

        if not findings and tickets:
            return "human_review"
        if not findings:
            return "finalize"
        if tickets:
            return "human_review"
        if state.get("verification_enabled", True):
            return "verify_findings"
        return "generate_decisions"

    def _route_after_verify(
        self, state: OrchestratorState
    ) -> Literal["generate_decisions", "human_review", "finalize", "handle_error"]:
        if state.get("errors"):
            return "handle_error"

        report = state.get("verification_report")
        if report is None:
            return "generate_decisions"

        block_flags = [f for f in report.flags if f.severity == "block"]
        if block_flags and len(block_flags) >= config.verification_flag_threshold:
            logger.warning(
                "Verification gate blocked",
                block_count=len(block_flags),
                threshold=config.verification_flag_threshold,
            )
            return "human_review"

        if not state.get("findings"):
            return "finalize"

        return "generate_decisions"

    # ── Public API ───────────────────────────────────────────

    async def analyze(
        self,
        contract_text: str,
        contract_name: str = "",
        verification_enabled: bool | None = None,
    ) -> ContractAnalysis:
        """Run the full contract analysis pipeline."""
        total_start = time.monotonic()

        if verification_enabled is None:
            verification_enabled = config.verification_enabled

        initial_state = {
            "contract_text": contract_text,
            "contract_name": contract_name or "Unnamed Contract",
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
            "verification_enabled": verification_enabled,
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

        logger.info(
            "Starting analysis",
            contract_name=contract_name,
            contract_length=len(contract_text),
            verification_enabled=verification_enabled,
        )

        final_state = await self.workflow.ainvoke(initial_state)
        total_duration_ms = (time.monotonic() - total_start) * 1000

        analysis = ContractAnalysis(
            contract_name=contract_name,
            contract_text=contract_text,
            clauses=final_state.get("clauses", []),
            findings=final_state.get("findings", []),
            recommendations=final_state.get("recommendations", []),
            audit_trail=final_state.get("audit_trail", []),
            jurisdiction_analysis=final_state.get("jurisdiction_analysis", {}),
            standards_applicability=final_state.get("standards_applicability", []),
            total_duration_ms=total_duration_ms,
            verification_report=final_state.get("verification_report"),
            escalation_tickets=final_state.get("escalation_tickets", []),
        )

        logger.info(
            "Analysis complete",
            analysis_id=analysis.analysis_id,
            total_duration_ms=total_duration_ms,
            clauses=len(analysis.clauses),
            findings=len(analysis.findings),
            recommendations=len(analysis.recommendations),
            errors=len(final_state.get("errors", [])),
            stage=final_state.get("current_stage", "unknown"),
        )

        return analysis

# Global orchestrator instance (clients created lazily)
orchestrator = Orchestrator()
