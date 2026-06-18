"""A2A server wrappers for the Risk & Compliance Agent family.

Only the Risk agent is wrapped as an A2A service — it's the only component
that genuinely needs the protocol: the LLM runs a ReAct reasoning loop with
dynamic tool calling, making it a true AI agent.

The other components (contract parsing, verification, decision generation)
are single-pass LLM calls and run directly in-process inside the orchestrator.
"""

import json
import time
from uuid import uuid4

from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue_v2 import EventQueue
from a2a.server.request_handlers.default_request_handler import LegacyRequestHandler
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Artifact,
    Part,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
)
from starlette.applications import Starlette

from contract_analyzer.agents.risk_compliance import (
    risk_processor,
    risk_processor_privacy,
    risk_processor_financial,
)
from contract_analyzer.logging_setup import AuditLogger

logger = AuditLogger(__name__, "a2a_servers")


class RiskAgentExecutor(AgentExecutor):
    """A2A executor for the agentic Risk & Compliance Agent.

    This is the only executor needed — contract parsing, verification, and
    decision generation are single-pass LLM calls that run directly in the
    orchestrator process. Only the ReAct tool-calling loop warrants A2A.
    """

    def __init__(self, specialist: str | None = None) -> None:
        super().__init__()
        if specialist == "privacy":
            self.processor = risk_processor_privacy
            self.agent_name = "risk_compliance_privacy"
        elif specialist == "financial":
            self.processor = risk_processor_financial
            self.agent_name = "risk_compliance_financial"
        else:
            self.processor = risk_processor
            self.agent_name = "risk_compliance"

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()
        task_id = context.task_id or str(uuid4())
        ctx_id = context.context_id or ""

        logger.info(f"[{self.agent_name}] Processing request", task_id=task_id, input_length=len(user_input))

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=ctx_id,
                status=TaskStatus(state=TaskState.TASK_STATE_WORKING),
            )
        )

        try:
            start = time.monotonic()
            result = await self.processor.process(user_input)
            duration_ms = (time.monotonic() - start) * 1000

            artifact = Artifact(
                artifact_id=str(uuid4()),
                name=f"{self.agent_name}_result",
                parts=[Part(text=json.dumps(result, default=str), media_type="application/json")],
            )
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(task_id=task_id, context_id=ctx_id, artifact=artifact)
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=task_id,
                    context_id=ctx_id,
                    status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
                )
            )

            logger.info(f"[{self.agent_name}] Completed successfully", task_id=task_id, duration_ms=duration_ms)

        except Exception as e:
            logger.error(f"[{self.agent_name}] Execution failed: {e}", task_id=task_id)
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=task_id,
                    context_id=ctx_id,
                    status=TaskStatus(state=TaskState.TASK_STATE_FAILED),
                )
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id or ""
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context.context_id or "",
                status=TaskStatus(state=TaskState.TASK_STATE_CANCELED),
            )
        )


# ── Agent Card ────────────────────────────────────────────────

def _build_risk_agent_card(url: str) -> AgentCard:
    from a2a.types import AgentInterface
    from a2a.utils.constants import TransportProtocol

    return AgentCard(
        name="Risk and Compliance Agent",
        description="Agentic compliance evaluation using ReAct reasoning with dynamic "
        "tool-based retrieval. The LLM decides when to retrieve, what to query, and "
        "when evidence is sufficient. Supports specialist routing for privacy and "
        "financial compliance domains.",
        version="2.0.0",
        supported_interfaces=[
            AgentInterface(url=url, protocol_binding=TransportProtocol.JSONRPC)
        ],
        capabilities=AgentCapabilities(streaming=True, push_notifications=False),
        default_input_modes=["text", "text/plain"],
        default_output_modes=["application/json"],
        skills=[
            AgentSkill(
                id="evaluate_risk",
                name="Agentic Risk and Compliance Evaluation",
                description="Evaluates contract clauses against regulatory standards "
                "using LLM-controlled iterative retrieval with tool invocation, escalation, "
                "and confidence-based reasoning.",
                tags=["risk", "compliance", "react", "agentic", "tool-use",
                      "GDPR", "DPDPA", "CCPA", "HIPAA", "PCI_DSS",
                      "ISO27001", "SOC2", "NIST", "SOX", "FedRAMP",
                      "US_RESTATEMENT", "US_UCC", "US_DGCL",
                      "IND_CONTRACT", "IT_ACT", "audit"],
                examples=[
                    "Evaluate these contract clauses and retrieve applicable standards dynamically",
                    "Analyze an NDA under Delaware law with iterative compliance research",
                ],
            )
        ],
    )


def _create_agent_app(executor: RiskAgentExecutor, agent_card: AgentCard) -> Starlette:
    task_store = InMemoryTaskStore()
    request_handler = LegacyRequestHandler(
        agent_executor=executor,
        task_store=task_store,
        agent_card=agent_card,
    )
    card_routes = create_agent_card_routes(agent_card)
    rpc_routes = create_jsonrpc_routes(request_handler, rpc_url="/")
    return Starlette(routes=card_routes + rpc_routes)


def _warmup_indices() -> None:
    """Eagerly load retrieval indices to avoid lazy-load race conditions."""
    from contract_analyzer.retrieval.hybrid_retriever import get_hybrid_retriever
    logger.info("Warming up retrieval indices (BM25 + FAISS)")
    get_hybrid_retriever()
    logger.info("Retrieval indices ready")


def create_risk_agent_app(port: int = 8005) -> Starlette:
    _warmup_indices()
    card = _build_risk_agent_card(f"http://localhost:{port}")
    return _create_agent_app(RiskAgentExecutor(), card)


def create_risk_privacy_agent_app(port: int = 8006) -> Starlette:
    _warmup_indices()
    card = _build_risk_agent_card(f"http://localhost:{port}")
    return _create_agent_app(RiskAgentExecutor(specialist="privacy"), card)


def create_risk_financial_agent_app(port: int = 8007) -> Starlette:
    _warmup_indices()
    card = _build_risk_agent_card(f"http://localhost:{port}")
    return _create_agent_app(RiskAgentExecutor(specialist="financial"), card)
