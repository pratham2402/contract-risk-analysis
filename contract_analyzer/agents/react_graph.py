"""ReAct-style LangGraph for the Risk & Compliance Agent.

Builds a tool-calling agent graph where the LLM makes decisions about
when to retrieve, what to query, and when to produce final answers.

Graph: START → analyze → [tools?] → execute_tools → observe → analyze
                                              ↘ finalize → END

The LLM controls retrieval behavior within a bounded iteration cap.
"""

import json
from typing import Annotated, Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger

logger = AuditLogger(__name__, "react_graph")

REACT_SYSTEM_PROMPT = """You are a senior compliance analyst with access to a curated
legal standards database. You analyze contract clauses using a rigorous applicability
framework. You have tools to retrieve standards, examine clauses, compare jurisdictions,
and escalate when uncertain.

## REASONING PROTOCOL

You work in a Thought → Action → Observation cycle:

Thought: Analyze what you know and what you need to know. State your reasoning clearly.
  - Which clause are you analyzing?
  - What jurisdiction applies?
  - What could be relevant? What can you rule out?
  - What do you need to retrieve to be certain?

Action: Invoke ONE tool at a time. Choose the most useful next step.
  - retrieve_standards: when you need regulatory or legal context
  - retrieve_clause: when you need to re-read exact clause text
  - compare_jurisdictions: when you need to check cross-jurisdictional issues
  - escalate_to_human: when you cannot reach a confident conclusion
  - request_more_context: when the contract metadata is insufficient

Observation: The tool result. Incorporate this evidence into your next thought.

When you have sufficient evidence, produce your final answer as a JSON object
with jurisdiction_analysis, standards_applicability, and findings.

## RULES

1. Apply the 3-layer trigger test before citing ANY regulatory standard:
   (a) Subject Matter (b) Jurisdictional Nexus (c) Materiality
   ALL THREE must pass. If any fails, the standard does NOT apply.

2. Jurisdictional Nexus is the most important filter:
   - US/state-law contracts: require US_RESTATEMENT baseline. Add US_UCC if
     goods are involved. Add US_DGCL if a party is a Delaware entity.
     Do NOT include HIPAA, CCPA, GLBA, or FERPA unless the contract explicitly
     involves US healthcare, California consumers, US financial data, or
     US educational records respectively.
   - Indian-law contracts: require IND_CONTRACT + IT_ACT baseline. Add DPDPA
     if personal data is involved. Do NOT apply US or EU standards to an
     India-only contract unless the contract explicitly involves US or EU
     entities, data subjects, or operations.
   - EU-law contracts: require GDPR if personal data is involved. Do NOT
     apply US or India standards unless the contract has US or India nexus.

3. PCI DSS applies ONLY when payment card data is specifically mentioned.
   Do NOT apply PCI DSS for general data protection or security clauses.

4. NEVER cite an article number you did not retrieve. Every citation must match
   a retrieved excerpt. If you need a standard but it wasn't retrieved, retrieve
   it now - do not fabricate.

5. If confidence is below 0.6, call escalate_to_human. Do not produce low-quality
   findings.

6. After retrieving standards, cross-check: does the standard's actual content
   support the finding you're considering? If the match is weak, retrieve more
   or exclude the standard.

7. In your standards_applicability output, list both applicable and excluded
   standards. For excluded standards, provide a clear reason (e.g., "No US nexus",
   "Not a Delaware entity", "Payment card data not involved").

8. You have a limited number of reasoning cycles. Use them efficiently.

## OUTPUT FORMAT (final answer only)

{
  "jurisdiction_analysis": {"governing_law": "...", "party_locations": "...", "notes": "..."},
  "standards_applicability": [
    {"standard": "...", "applies": true/false, "reason": "..."}
  ],
  "findings": [
    {
      "clause_id": "...",
      "issue_description": "...",
      "risk_level": "critical|high|medium|low|info",
      "category": "data_protection|security|liability|contract_formation|...",
      "referenced_standards": [
        {"standard": "...", "article": "...", "description": "...", "relevance_score": 0.0}
      ],
      "standards_reviewed_and_excluded": [
        {"standard": "...", "reason_excluded": "..."}
      ],
      "explanation": "...",
      "reasoning_trace": "step-by-step reasoning with tool calls made",
      "confidence": 0.0
    }
  ]
}"""


class AgentState(TypedDict):
    """State carried through the ReAct reasoning loop."""
    messages: Annotated[list, add_messages]
    iteration_count: int
    contract_context: dict[str, Any]
    clauses: list[dict[str, Any]]
    tool_call_history: list[dict[str, Any]]
    escaalation_tickets: list[dict[str, Any]]
    final_output: dict[str, Any]


def _analyze_node(llm_with_tools):
    """Node that calls the LLM with tools bound."""
    async def analyze(state: AgentState) -> dict:
        messages = state["messages"]
        iteration = state.get("iteration_count", 0) + 1

        logger.info(f"ReAct analyze iteration {iteration}")

        response = await llm_with_tools.ainvoke(messages)

        return {
            "messages": [response],
            "iteration_count": iteration,
        }
    return analyze


def _should_continue(
    state: AgentState,
) -> Literal["execute_tools", "finalize", "loop"]:
    """Decide whether to call tools, finalize, or continue looping."""
    messages = state["messages"]
    last_message = messages[-1]
    iteration = state.get("iteration_count", 0)
    max_iterations = config.risk_agent_max_iterations

    # Force finalize if we hit the iteration cap
    if iteration >= max_iterations:
        logger.warning(f"ReAct loop hit iteration cap ({max_iterations}), forcing finalize")
        return "finalize"

    # If the last message has tool calls, execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "execute_tools"

    # If no tool calls and the message looks like a final answer, finalize.
    # Otherwise loop back for more reasoning.
    content = getattr(last_message, "content", "") or ""

    if isinstance(content, str) and content.strip():
        # Only finalize if the content actually contains a JSON findings object
        # (braces + "findings" key), not just a mention of "findings" in prose.
        stripped = content.strip()
        looks_like_json = (
            stripped.startswith("{") or "```json" in stripped
        )
        if looks_like_json and '"findings"' in stripped:
            return "finalize"

    if hasattr(last_message, "tool_calls") and not last_message.tool_calls:
        return "finalize"

    # Default: let the LLM think more
    return "loop"


def _should_continue_sync(state: AgentState) -> str:
    return _should_continue(state)


class ClauseLookupTool:
    """Injects clause text into tool observations when retrieve_clause is called.

    This is not an LLM-visible tool but a post-processing hook on the
    ToolNode output. When the LLM calls retrieve_clause(clause_id=X),
    this interceptor replaces the generic response with actual clause text.
    """

    def __init__(self, clauses: list[dict[str, Any]]):
        self._clause_map: dict[str, dict] = {
            c.get("id", ""): c for c in clauses
        }

    def enrich_observation(self, tool_message: ToolMessage) -> ToolMessage:
        """If this is a retrieve_clause response, inject the actual clause text."""
        try:
            content = json.loads(tool_message.content)
        except (json.JSONDecodeError, TypeError):
            return tool_message

        if content.get("status") != "requested":
            return tool_message

        clause_id = content.get("clause_id", "")
        clause = self._clause_map.get(clause_id)
        if clause:
            tool_message.content = json.dumps({
                "status": "found",
                "clause_id": clause_id,
                "title": clause.get("title", ""),
                "clause_type": clause.get("clause_type", ""),
                "text": clause.get("text", ""),
            })
        else:
            tool_message.content = json.dumps({
                "status": "not_found",
                "clause_id": clause_id,
                "message": f"No clause found with ID '{clause_id}'. "
                           f"Available IDs: {list(self._clause_map.keys())[:10]}",
            })

        return tool_message


def build_react_agent(
    llm: ChatOpenAI | None = None,
    tools: list[BaseTool] | None = None,
    max_iterations: int | None = None,
) -> StateGraph:
    """Build the ReAct agent LangGraph.

    Args:
        llm: ChatOpenAI instance. If None, creates from config.
        tools: List of tools to bind. If None, imports default set.
        max_iterations: Hard cap on reasoning iterations.

    Returns:
        Compiled LangGraph StateGraph.
    """
    from contract_analyzer.agents.tools import RISK_AGENT_TOOLS

    if llm is None:
        llm = ChatOpenAI(
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            temperature=config.llm_temperature,
        )

    if tools is None:
        tools = RISK_AGENT_TOOLS

    max_iterations = max_iterations or config.risk_agent_max_iterations

    llm_with_tools = llm.bind_tools(tools)

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("analyze", _analyze_node(llm_with_tools))
    graph.add_node("execute_tools", ToolNode(tools))
    graph.add_node("finalize", _finalize_node(llm))

    # Edges
    graph.set_entry_point("analyze")

    graph.add_conditional_edges(
        "analyze",
        _should_continue_sync,
        {
            "execute_tools": "execute_tools",
            "finalize": "finalize",
            "loop": "analyze",
        },
    )

    graph.add_edge("execute_tools", "analyze")
    graph.add_edge("finalize", END)

    logger.info(
        f"ReAct agent built: {len(tools)} tools, max_iterations={max_iterations}"
    )

    return graph.compile()


def _repair_and_parse(text: str) -> dict | None:
    """Attempt json.loads, then json_repair, then return None."""
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    try:
        from json_repair import repair_json  # type: ignore[import-untyped]
        repaired = repair_json(text)
        result = json.loads(repaired)
        if isinstance(result, dict):
            return result
    except Exception:
        pass

    return None


def _extract_json_from_text(text: str) -> dict | None:
    """Extract a JSON object from text that may contain markdown fences or
    surrounding prose. Uses json_repair as a fallback for malformed JSON."""
    candidates: list[str] = []

    # Try code-fenced JSON first
    if "```json" in text:
        candidates.append(text.split("```json")[1].split("```")[0])
    elif "```" in text:
        candidates.append(text.split("```")[1].split("```")[0])

    # Also try the raw text (for unfenced JSON)
    candidates.append(text)

    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate:
            continue
        result = _repair_and_parse(candidate)
        if result is not None and "findings" in result:
            return result

    # Last resort: find the outermost { } pair that contains "findings"
    try:
        start = text.index('"findings"')
        brace_start = text.rfind("{", 0, start)
        if brace_start >= 0:
            depth = 0
            for i in range(brace_start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = text[brace_start : i + 1]
                        result = _repair_and_parse(candidate)
                        if result is not None and "findings" in result:
                            return result
                        break
    except (ValueError, json.JSONDecodeError):
        pass

    return None


def _sanitize_messages_for_llm(messages: list) -> list:
    """Remove trailing messages with orphaned tool_calls that would break the API.

    API providers reject message lists where an assistant message has tool_calls
    but no tool messages follow. This strips those orphaned messages.
    """
    # Find the last AIMessage — if it has tool_calls, we need to strip it
    # (and any preceding pairs) until we reach a clean state.
    cleaned = list(messages)
    while cleaned:
        last = cleaned[-1]
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            # This AIMessage has tool_calls — remove it and any tool messages
            # that immediately follow (shouldn't exist if orphaned, but be safe)
            cleaned.pop()
        elif isinstance(last, ToolMessage):
            # Remove tool message (it was responding to a now-removed AIMessage
            # or is itself orphaned)
            cleaned.pop()
        else:
            break
    return cleaned


def _finalize_node(llm: ChatOpenAI | None = None):
    """Node that extracts structured output from final LLM message.

    When JSON extraction fails, re-prompts the LLM (without tools) for a
    structured final answer before falling back to empty findings.
    """

    async def finalize(state: AgentState) -> dict:
        messages = state["messages"]
        content = ""

        # Walk backward through messages to find the last AI message with content
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                content = msg.content
                break

        result = None
        if isinstance(content, str) and content.strip():
            result = _extract_json_from_text(content)

        # If extraction failed and we have an LLM, give it one last chance
        if result is None and llm is not None:
            logger.info(
                "ReAct finalize: JSON extraction failed, re-prompting LLM for final output",
                raw_content_preview=content[:500] if content else "",
            )
            clean_messages = _sanitize_messages_for_llm(messages)
            final_prompt = HumanMessage(
                content=(
                    "You have reached the end of your analysis cycles. "
                    "Based on ALL evidence gathered so far, produce your final "
                    "compliance analysis as a valid JSON object.\n\n"
                    "OUTPUT ONLY the JSON object. No markdown fences, no "
                    "surrounding text — start with { and end with }."
                )
            )
            try:
                # Use JSON mode for the re-prompt to force valid JSON output
                json_llm = ChatOpenAI(
                    model=config.llm_model,
                    api_key=config.llm_api_key,
                    base_url=config.llm_base_url,
                    temperature=0.0,
                    model_kwargs={"response_format": {"type": "json_object"}},
                )
                response = await json_llm.ainvoke(clean_messages + [final_prompt])
                response_content = (
                    response.content
                    if hasattr(response, "content")
                    else str(response)
                )
                if isinstance(response_content, str):
                    result = _extract_json_from_text(response_content)
                    if result is None:
                        logger.warning(
                            "ReAct finalize: re-prompt JSON still unparseable",
                            raw_content_preview=response_content[:500],
                        )
            except Exception as exc:
                logger.warning(f"ReAct finalize: LLM re-prompt failed: {exc}")

        if result is not None:
            logger.info(
                "ReAct finalize: produced structured output",
                findings=len(result.get("findings", [])),
            )
            return {
                "final_output": result,
                "iteration_count": state.get("iteration_count", 0),
            }

        logger.warning(
            "ReAct finalize: could not parse JSON from output",
            raw_content_preview=content[:500] if content else "",
        )
        return {
            "final_output": {"findings": [], "raw_output": content[:2000]},
            "iteration_count": state.get("iteration_count", 0),
        }

    return finalize
