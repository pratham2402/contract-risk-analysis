"""Tests for Risk Agent tool definitions (no LLM required)."""

import json

import pytest

from contract_analyzer.agents.tools import (
    RISK_AGENT_TOOLS,
    compare_jurisdictions,
    escalate_to_human,
    request_more_context,
    retrieve_clause,
)


class TestToolDefinitions:
    def test_all_tools_in_list(self):
        tool_names = {t.name for t in RISK_AGENT_TOOLS}
        expected = {
            "retrieve_standards",
            "retrieve_clause",
            "compare_jurisdictions",
            "escalate_to_human",
            "request_more_context",
        }
        assert tool_names == expected

    def test_tool_has_description(self):
        for tool in RISK_AGENT_TOOLS:
            assert tool.description, f"Tool {tool.name} has no description"

    def test_tool_is_langchain_tool(self):
        from langchain_core.tools import BaseTool
        for tool in RISK_AGENT_TOOLS:
            assert isinstance(tool, BaseTool), f"{tool.name} is not a BaseTool"


class TestRetrieveClause:
    def test_returns_requested_status(self):
        result = retrieve_clause.invoke({"clause_id": "c1"})
        data = json.loads(result)
        assert data["status"] == "requested"
        assert data["clause_id"] == "c1"


class TestEscalateToHuman:
    def test_basic_escalation(self):
        result = escalate_to_human.invoke({
            "reason": "Ambiguous liability clause — conflicting standards",
        })
        data = json.loads(result)
        assert data["status"] == "escalated"
        assert data["ticket"]["reason"] == "Ambiguous liability clause — conflicting standards"
        assert data["ticket"]["severity"] == "medium"
        assert "ticket_id" in data["ticket"]
        assert "timestamp" in data["ticket"]

    def test_escalation_with_clause(self):
        result = escalate_to_human.invoke({
            "reason": "Unusual indemnification structure",
            "clause_id": "c5",
            "standard": "US_RESTATEMENT",
        })
        data = json.loads(result)
        assert data["ticket"]["severity"] == "high"
        assert data["ticket"]["clause_id"] == "c5"
        assert data["ticket"]["standard"] == "US_RESTATEMENT"

    def test_escalation_message(self):
        result = escalate_to_human.invoke({"reason": "Novel legal question"})
        data = json.loads(result)
        assert "human review" in data["message"].lower()
        assert "escalated" in data["message"].lower()


class TestRequestMoreContext:
    def test_returns_context_requested(self):
        result = request_more_context.invoke({
            "reason": "Need to understand data flows between parties",
        })
        data = json.loads(result)
        assert data["status"] == "context_requested"
        assert "data flows" in data["reason"]


class TestCompareJurisdictions:
    def test_returns_comparison_structure(self):
        """Note: This may fail if FAISS index doesn't exist or has stale pickle data.
        We skip gracefully in that case."""
        try:
            result = compare_jurisdictions.invoke({
                "jurisdictions": ["US", "India"],
            })
            data = json.loads(result)
            assert "jurisdictions_compared" in data
            assert "results" in data
        except (FileNotFoundError, ModuleNotFoundError):
            pytest.skip("Standards index not available (needs rebuild with current module name)")
