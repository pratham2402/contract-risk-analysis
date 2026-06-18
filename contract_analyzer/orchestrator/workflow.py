"""LangGraph Orchestrator Workflow — Dynamic Agentic Routing.

Coordinates the multi-agent contract analysis pipeline using LangGraph's
StateGraph with conditional routing, specialist dispatch, verification gating,
and human-review escalation paths.

Pipeline:
  START → parse_contract → classify_content → [route specialist]
       → evaluate_risk → verify_findings → [verification gate]
       → generate_decisions → finalize → END

Only the Risk & Compliance agent uses the A2A protocol — it's the only
component that runs a genuine ReAct reasoning loop with tool calling.
The other components are direct LLM calls run in-process.
"""

import asyncio
import json
import time
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from a2a.client.client import ClientCallContext
from a2a.client.client_factory import create_client
from a2a.types import (
    Message,
    Part,
    Role,
    SendMessageConfiguration,
    SendMessageRequest,
)
from langgraph.graph import END, START, StateGraph

from contract_analyzer.agents.contract_understanding import processor as contract_processor
from contract_analyzer.agents.decision_recommendation import decision_processor
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

DEFAULT_TIMEOUT = 120.0  # seconds per A2A agent call


class Orchestrator:
    """LangGraph-based orchestrator with dynamic routing and verification."""

    def __init__(self) -> None:
        self.workflow = self._build_workflow()
        self._clients: dict[str, Any] = {}
        self._client_lock = asyncio.Lock()

    async def _get_client(self, url: str, name: str) -> Any:
        """Get or lazily create an A2A client for the given agent URL."""
        if name not in self._clients:
            async with self._client_lock:
                if name not in self._clients:
                    self._clients[name] = await create_client(url)
                    logger.info(f"Created A2A client for {name}", url=url)
        return self._clients[name]

    async def _call_agent(
        self, agent_url: str, agent_name: str, payload: str
    ) -> dict:
        """Call an A2A agent and return the structured result."""
        start = time.monotonic()

        client = await self._get_client(agent_url, agent_name)

        message = Message(
            message_id=str(uuid4()),
            role=Role.ROLE_USER,
            parts=[Part(text=payload, media_type="text/plain")],
        )

        request = SendMessageRequest(
            message=message,
            configuration=SendMessageConfiguration(return_immediately=False),
        )

        result_text = ""
        ctx = ClientCallContext(timeout=DEFAULT_TIMEOUT)
        async for stream_response in client.send_message(request, context=ctx):
            if stream_response.HasField("task"):
                for artifact in stream_response.task.artifacts:
                    for part in artifact.parts:
                        if part.text:
                            result_text += part.text
            elif stream_response.HasField("message"):
                for part in stream_response.message.parts:
                    if part.text:
                        result_text += part.text
            elif stream_response.HasField("artifact_update"):
                for part in stream_response.artifact_update.artifact.parts:
                    if part.text:
                        result_text += part.text

        try:
            result = json.loads(result_text) if result_text else {}
        except json.JSONDecodeError:
            result = {"raw_response": result_text}

        duration_ms = (time.monotonic() - start) * 1000
        logger.agent_call(agent_name, "a2a_call", duration_ms, True)

        return result

    async def close(self) -> None:
        """Close all A2A client connections."""
        for name, client in self._clients.items():
            try:
                await client.close()
            except Exception:
                pass
        self._clients.clear()

    def _build_workflow(self) -> StateGraph:
        """Build the dynamic LangGraph StateGraph for contract analysis."""
        graph = StateGraph(dict)

        graph.add_node("parse_contract", self._node_parse_contract)
        graph.add_node("classify_content", self._node_classify_content)
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
            {"classify_content": "classify_content", "handle_error": "handle_error"},
        )

        graph.add_conditional_edges(
            "classify_content",
            self._route_after_classify,
            {"evaluate_risk": "evaluate_risk", "human_review": "human_review", "handle_error": "handle_error"},
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
        """Parse contract via direct LLM call (not an agentic operation)."""
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
            state["party_a_name"] = result.get("party_a_name", "")
            state["party_a_location"] = result.get("party_a_location", "")
            state["party_b_name"] = result.get("party_b_name", "")
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
        except Exception as e:
            state["errors"].append(f"Contract parsing failed: {e}")
            logger.error(f"Contract parsing failed: {e}")

        return state

    async def _node_classify_content(self, state: OrchestratorState) -> dict:
        """Classify contract content to determine specialist routing."""
        logger.info("Classifying contract content for routing")
        state["current_stage"] = "classifying"
        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "content_classification",
            "action": "analyzing_contract_domain",
        })

        contract_type = (state.get("contract_type") or "").lower()
        subject_matter = (state.get("subject_matter") or "").lower()
        raw_data = [d.lower().replace("_", " ") for d in (state.get("data_involved") or [])]
        contract_text = (state.get("contract_text") or "").lower()

        # Build a combined search text from metadata + first 5KB of contract
        combined_text = f"{contract_type} {subject_matter} {' '.join(raw_data)} {contract_text[:5000]}"

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

        privacy_score = sum(
            1 for sig in privacy_signals
            if sig in combined_text
        )
        financial_score = sum(
            1 for sig in financial_signals
            if sig in combined_text
        )

        logger.info(
            "Classification scores",
            privacy_score=privacy_score,
            financial_score=financial_score,
            contract_type=contract_type,
            data_involved=raw_data[:5],
        )

        if privacy_score >= 2:
            specialist = "privacy"
            reason = f"Contract has privacy signals (score={privacy_score}, data_involved={raw_data[:3]})"
        elif financial_score >= 2:
            specialist = "financial"
            reason = f"Contract has financial compliance signals (score={financial_score}, subject={subject_matter})"
        else:
            specialist = "generalist"
            reason = "Contract does not strongly signal privacy or financial domain"

        risk_url = {
            "privacy": config.risk_privacy_agent_url,
            "financial": config.risk_financial_agent_url,
        }.get(specialist, config.risk_agent_url)

        state["specialist_domain"] = specialist
        state["routing_decision"] = specialist
        state["routing_reason"] = reason
        state["risk_agent_url"] = risk_url

        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "content_classification",
            "action": "routing_decided",
            "specialist": specialist,
            "risk_agent_url": risk_url,
            "reason": reason,
        })

        logger.info(
            "Content classified",
            specialist=specialist,
            privacy_score=privacy_score,
            financial_score=financial_score,
        )

        return state

    async def _node_evaluate_risk(self, state: OrchestratorState) -> dict:
        """Evaluate risk via the Risk & Compliance Agent (A2A).

        This is the only genuinely agentic component — the LLM runs a ReAct
        loop with dynamic tool calling, so it must run as a separate service.
        """
        specialist = state.get("specialist_domain", "generalist")
        risk_url = state.get("risk_agent_url", config.risk_agent_url)
        state["current_stage"] = "risk_evaluation"

        state["audit_trail"].append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": "risk_evaluation",
            "action": "calling_risk_agent",
            "specialist": specialist,
            "agent_url": risk_url,
        })

        contract_context = json.dumps({
            "clauses": [c.model_dump() for c in state["clauses"]],
            "contract_name": state.get("contract_name", ""),
            "governing_law": state.get("governing_law", ""),
            "party_a_location": state.get("party_a_location", ""),
            "party_b_location": state.get("party_b_location", ""),
            "data_subject_locations": "",
            "subject_matter": state.get("subject_matter", ""),
        })

        try:
            result = await self._call_agent(
                risk_url,
                f"risk_compliance_{specialist}",
                contract_context,
            )

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
                "reaact_iterations": result.get("reaact_iterations", 0),
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
    ) -> Literal["classify_content", "handle_error"]:
        if state.get("errors"):
            return "handle_error"
        if not state.get("clauses"):
            state["errors"].append("No clauses extracted from contract text")
            return "handle_error"
        return "classify_content"

    def _route_after_classify(
        self, state: OrchestratorState
    ) -> Literal["evaluate_risk", "human_review", "handle_error"]:
        if state.get("errors"):
            return "handle_error"
        if state.get("routing_decision") == "block":
            state["errors"].append("Contract domain blocked: cannot be analyzed automatically")
            return "human_review"
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
        status_callback_url: str | None = None,
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
            "risk_agent_url": config.risk_agent_url,
            "job_status": "pending",
            "status_callback_url": status_callback_url,
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

    async def submit(
        self,
        contract_text: str,
        contract_name: str = "",
        verification_enabled: bool | None = None,
        status_callback_url: str | None = None,
    ) -> dict:
        """Submit an analysis job and return immediately with a job ID."""
        job_id = str(uuid4())

        asyncio.create_task(
            self._run_job(
                job_id=job_id,
                contract_text=contract_text,
                contract_name=contract_name,
                verification_enabled=verification_enabled,
                status_callback_url=status_callback_url,
            )
        )

        logger.info("Analysis job submitted", job_id=job_id, name=contract_name)
        return {"job_id": job_id, "status": "pending", "contract_name": contract_name}

    async def _run_job(
        self,
        job_id: str,
        contract_text: str,
        contract_name: str,
        verification_enabled: bool | None,
        status_callback_url: str | None,
    ) -> None:
        """Background job runner."""
        try:
            await self.analyze(
                contract_text=contract_text,
                contract_name=contract_name,
                verification_enabled=verification_enabled,
                status_callback_url=status_callback_url,
            )
            logger.info("Background job completed", job_id=job_id)
        except Exception as e:
            logger.error(f"Background job failed: {e}", job_id=job_id)


# Global orchestrator instance (clients created lazily)
orchestrator = Orchestrator()
