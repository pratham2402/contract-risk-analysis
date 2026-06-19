"""Tools available to the Risk & Compliance ReAct Agent.

Each tool is a Python function decorated with @tool that the LLM can invoke
dynamically during its reasoning loop. Tools are read-only except
escalate_to_human which creates an audit ticket.
"""

from langchain_core.tools import tool

from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.retrieval.hybrid_retriever import query_standards_hybrid

logger = AuditLogger(__name__, "risk_agent_tools")


@tool
def retrieve_standards(
    query: str,
    jurisdiction: str | None = None,
    standard_type: str | None = None,
    authority_level: str | None = None,
) -> str:
    """Search the compliance standards database for regulations, statutes,
    or legal frameworks relevant to a legal or compliance question.

    Use this tool to find applicable standards when analyzing a contract
    clause. You can filter results by jurisdiction, standard category,
    and authority level.

    Args:
        query: Natural language search query describing what you need
               (e.g., "confidentiality breach damages for NDA under US law").
        jurisdiction: Filter by governing law jurisdiction. Use "US", "EU",
                      "India", or "Global". Omit for unfiltered search.
        standard_type: Filter by category. Use "data_protection", "security",
                       "contract_law", "industry", or "financial_reporting".
        authority_level: Filter by authority. Use "statute", "regulation",
                         "framework", "common_law", or "industry_standard".

    Returns:
        JSON string with relevant standards entries including article
        citations, content summaries, and relevance scores.
    """
    import json

    logger.info(
        f"Tool: retrieve_standards query='{query[:100]}'",
        jurisdiction=jurisdiction,
        standard_type=standard_type,
    )

    results = query_standards_hybrid(
        query=query,
        top_k=10,
        min_score=0.0,
        jurisdiction=jurisdiction,
        standard_category=standard_type,
        authority_level=authority_level,
    )

    if not results:
        return json.dumps({
            "count": 0,
            "message": "No matching standards found. Try a broader query "
                       "or remove jurisdiction/type filters.",
            "results": [],
        })

    return json.dumps({
        "count": len(results),
        "results": [
            {
                "standard": r["standard"],
                "article": r.get("article"),
                "title": r["title"],
                "content": r["content"][:600],
                "score": round(r.get("score", 0), 3),
                "jurisdiction": r.get("jurisdiction", "Global"),
                "category": r.get("standard_category", "general"),
                "authority": r.get("authority_level", "framework"),
            }
            for r in results
        ],
    }, default=str)


@tool
def compare_jurisdictions(jurisdictions: list[str]) -> str:
    """Compare contract law principles across specified jurisdictions.
    Returns a side-by-side comparison of key doctrines (formation,
    consideration vs consent, damages, defenses, etc.).

    Args:
        jurisdictions: List of jurisdiction codes to compare.
                       Valid values: "US", "India", "EU", "Global".

    Returns:
        JSON string with comparison table for each doctrine.
    """
    import json

    logger.info(f"Tool: compare_jurisdictions {jurisdictions}")

    # Query both jurisdictions' contract law entries
    results_by_jur = {}
    for jur in jurisdictions:
        results = query_standards_hybrid(
            query="contract formation consideration breach damages defenses",
            top_k=6,
            jurisdiction=jur,
            standard_category="contract_law",
        )
        results_by_jur[jur] = [
            {
                "standard": r["standard"],
                "article": r.get("article"),
                "title": r["title"],
                "content": r["content"][:400],
            }
            for r in results
        ]

    return json.dumps({
        "jurisdictions_compared": jurisdictions,
        "results": results_by_jur,
        "note": "Only jurisdictions with curated coverage in the database "
                "are included. Missing jurisdictions indicate a knowledge gap.",
    }, default=str)


@tool
def escalate_to_human(
    reason: str,
    clause_id: str | None = None,
    standard: str | None = None,
) -> str:
    """Flag a finding that requires human legal review. Use when:
    - Confidence in a finding is below threshold (0.6)
    - The contract involves unusual or novel legal questions
    - Retrieved standards are contradictory or ambiguous
    - The governing law jurisdiction lacks curated coverage in the database
    - You cannot reach a definitive conclusion after multiple retrieval attempts

    Args:
        reason: Detailed explanation of why human review is needed.
        clause_id: The specific clause ID triggering the escalation (optional).
        standard: The specific standard causing uncertainty (optional).

    Returns:
        JSON string with escalation ticket details for the audit trail.
    """
    import json
    from datetime import UTC, datetime
    from uuid import uuid4

    ticket_id = str(uuid4())[:8]
    severity = "high" if standard else "medium"

    escalation = {
        "ticket_id": ticket_id,
        "reason": reason,
        "clause_id": clause_id,
        "standard": standard,
        "severity": severity,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    logger.audit(
        f"Human escalation: {reason[:100]}",
        ticket_id=ticket_id,
        clause_id=clause_id,
        standard=standard,
    )

    return json.dumps({
        "status": "escalated",
        "ticket": escalation,
        "message": "This finding has been flagged for human review. "
                   "Do not produce a final finding for this clause — "
                   "mark it as escalated in your output.",
    })


@tool
def request_more_context(reason: str) -> str:
    """Request additional contract context from the orchestrator.
    Use when the clause text alone is insufficient for analysis and
    you need to understand party relationships, data flows, business
    context, or cross-references to other clauses.

    Args:
        reason: What specific context you need and why.

    Returns:
        JSON string confirming the request was logged.
    """
    import json

    logger.info(f"Tool: request_more_context reason='{reason[:100]}'")

    return json.dumps({
        "status": "context_requested",
        "reason": reason,
        "message": "Additional context has been requested from the "
                   "orchestrator. If available, it will appear in the "
                   "next observation. If not, proceed with available "
                   "information and note the limitation.",
    })


# All tools exposed to the LLM
RISK_AGENT_TOOLS = [
    retrieve_standards,
    compare_jurisdictions,
    escalate_to_human,
    request_more_context,
]
