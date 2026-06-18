"""LangGraph workflow state — just a typed dict to guide the StateGraph."""

from typing import Any

# The orchestrator uses a plain dict for LangGraph state so that add_messages
# reducer semantics work correctly without subclassing.
OrchestratorState = dict[str, Any]
