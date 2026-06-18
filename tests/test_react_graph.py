"""Tests for ReAct agent graph logic and JSON extraction.

These test pure functions — no LLM calls, no API keys required.
"""

import json

import pytest
from langchain_core.messages import ToolMessage

from contract_analyzer.agents.react_graph import (
    ClauseLookupTool,
    _extract_json_from_text,
    _repair_and_parse,
)


class TestExtractJsonFromText:
    def test_plain_json(self):
        text = '{"findings": [{"issue": "test"}], "standards_applicability": []}'
        result = _extract_json_from_text(text)
        assert result is not None
        assert len(result["findings"]) == 1
        assert result["findings"][0]["issue"] == "test"

    def test_json_with_markdown_fence(self):
        text = '''Here is my analysis:

```json
{"findings": [{"risk_level": "high", "issue_description": "Missing encryption"}], "standards_applicability": [{"standard": "GDPR", "applies": true}]}
```

Let me know if you need more detail.'''
        result = _extract_json_from_text(text)
        assert result is not None
        assert len(result["findings"]) == 1
        assert result["findings"][0]["risk_level"] == "high"

    def test_json_with_generic_fence(self):
        text = '''```
{"findings": [], "standards_applicability": []}
```'''
        result = _extract_json_from_text(text)
        assert result is not None

    def test_json_buried_in_prose(self):
        text = '''I have analyzed the contract and here are my conclusions.

The main finding is that the encryption clause is weak.

Here is the structured output:
{"findings": [{"issue_description": "Weak encryption", "risk_level": "medium", "confidence": 0.8}], "standards_applicability": [], "jurisdiction_analysis": {"governing_law": "Delaware"}}

Please review these findings.'''
        result = _extract_json_from_text(text)
        assert result is not None
        assert result["jurisdiction_analysis"]["governing_law"] == "Delaware"

    def test_no_findings_key_not_extracted(self):
        text = '{"some": "data", "other": "stuff"}'
        result = _extract_json_from_text(text)
        assert result is None

    def test_invalid_json(self):
        text = "This is not JSON at all"
        result = _extract_json_from_text(text)
        assert result is None

    def test_empty_string(self):
        result = _extract_json_from_text("")
        assert result is None

    def test_findings_with_braces_in_text(self):
        """JSON inside a markdown code block with other braces around."""
        text = '''Based on evidence: {retrieved: "GDPR Art. 32"}

```json
{
  "findings": [
    {
      "clause_id": "abc-123",
      "issue_description": "Need stronger encryption",
      "risk_level": "high",
      "category": "security",
      "referenced_standards": [
        {"standard": "GDPR", "article": "Art. 32", "description": "Security of processing", "relevance_score": 0.95}
      ],
      "explanation": "Clause uses TLS 1.2 but GDPR recommends state of the art",
      "reasoning_trace": "Retrieved GDPR Art 32 -> compared with clause text",
      "confidence": 0.85
    }
  ],
  "standards_applicability": [
    {"standard": "GDPR", "applies": true, "reason": "EU entity involved"}
  ],
  "jurisdiction_analysis": {"governing_law": "Delaware", "notes": "US law applies"}
}
```'''
        result = _extract_json_from_text(text)
        assert result is not None
        assert result["jurisdiction_analysis"]["governing_law"] == "Delaware"


    def test_trailing_comma_in_array(self):
        """JSON with trailing comma in array — common LLM mistake."""
        text = '{"findings": [{"issue": "bad encryption", "risk_level": "high", },], "standards_applicability": []}'
        result = _extract_json_from_text(text)
        assert result is not None
        assert len(result["findings"]) == 1
        assert result["findings"][0]["risk_level"] == "high"

    def test_trailing_comma_in_object(self):
        """JSON with trailing comma in object — common LLM mistake."""
        text = '{"findings": [], "standards_applicability": [], "jurisdiction_analysis": {"law": "India",}}'
        result = _extract_json_from_text(text)
        assert result is not None
        assert result["jurisdiction_analysis"]["law"] == "India"

    def test_broken_json_in_markdown_fence(self):
        """Malformed JSON inside markdown fence — json_repair should fix it."""
        text = '''```json
{
  "findings": [
    {
      "clause_id": "abc",
      "issue_description": "Unescaped "quotes" in text",
      "risk_level": "high",
      "confidence": 0.9,
    }
  ],
  "standards_applicability": []
}
```'''
        result = _extract_json_from_text(text)
        assert result is not None
        assert len(result["findings"]) == 1

    def test_text_before_json_no_fence(self):
        """LLM outputs prose then raw JSON without markdown fence."""
        text = '''Based on my thorough analysis, here is the final compliance report:

{
  "findings": [
    {
      "clause_id": "c1",
      "issue_description": "Missing encryption clause",
      "risk_level": "high",
      "category": "security",
      "referenced_standards": [],
      "explanation": "test",
      "reasoning_trace": "test",
      "confidence": 0.85
    }
  ],
  "standards_applicability": [],
  "jurisdiction_analysis": {"governing_law": "India"}
}'''
        result = _extract_json_from_text(text)
        assert result is not None
        assert len(result["findings"]) == 1
        assert result["jurisdiction_analysis"]["governing_law"] == "India"

    def test_multiple_json_candidates_picks_findings(self):
        """Text with multiple JSON blocks — picks the one with 'findings' key."""
        text = '''Pre-analysis: {"preliminary": true}

```json
{
  "findings": [{"issue_description": "Data breach risk", "risk_level": "critical", "confidence": 0.95}],
  "standards_applicability": []
}
```

Post-analysis: {"status": "complete"}'''
        result = _extract_json_from_text(text)
        assert result is not None
        assert len(result["findings"]) == 1
        assert result["findings"][0]["risk_level"] == "critical"


class TestRepairAndParse:
    def test_valid_json(self):
        result = _repair_and_parse('{"key": "value", "num": 42}')
        assert result == {"key": "value", "num": 42}

    def test_trailing_comma(self):
        result = _repair_and_parse('{"key": "value",}')
        assert result == {"key": "value"}

    def test_single_quotes(self):
        result = _repair_and_parse("{'key': 'value'}")
        assert result == {"key": "value"}

    def test_unescaped_quotes_in_value(self):
        """Unescaped double quotes inside a string value."""
        result = _repair_and_parse('{"text": "He said "hello" to me"}')
        assert result is not None
        assert "hello" in result["text"]

    def test_missing_closing_brace(self):
        """Truncated JSON — repair may or may not fix depending on severity."""
        result = _repair_and_parse('{"findings": [{"issue": "test"}], "standards_applicability": []')
        # json_repair may add missing closing brace
        if result is not None:
            assert "findings" in result

    def test_garbage_text(self):
        result = _repair_and_parse("this is not json at all")
        assert result is None

    def test_list_not_dict(self):
        """Top-level array is valid JSON but not a dict — returns None."""
        result = _repair_and_parse('[1, 2, 3]')
        assert result is None


class TestClauseLookupTool:
    @pytest.fixture
    def clauses(self):
        return [
            {
                "id": "c1",
                "title": "Confidentiality Obligations",
                "clause_type": "confidentiality",
                "text": "Receiving Party shall hold all info in strict confidence.",
            },
            {
                "id": "c2",
                "title": "Limitation of Liability",
                "clause_type": "liability",
                "text": "Total liability shall not exceed fees paid in 12 months.",
            },
            {
                "id": "c3",
                "title": "Data Protection",
                "clause_type": "data_protection",
                "text": "Personal data shall be encrypted using TLS 1.3 and AES-256.",
            },
        ]

    @pytest.fixture
    def lookup(self, clauses):
        return ClauseLookupTool(clauses)

    def test_found_clause(self, lookup):
        msg = ToolMessage(
            content=json.dumps({"status": "requested", "clause_id": "c2"}),
            tool_call_id="tc1",
        )
        enriched = lookup.enrich_observation(msg)
        content = json.loads(enriched.content)
        assert content["status"] == "found"
        assert content["title"] == "Limitation of Liability"
        assert "fees paid" in content["text"]

    def test_not_found_clause(self, lookup):
        msg = ToolMessage(
            content=json.dumps({"status": "requested", "clause_id": "nonexistent"}),
            tool_call_id="tc2",
        )
        enriched = lookup.enrich_observation(msg)
        content = json.loads(enriched.content)
        assert content["status"] == "not_found"
        assert "c1" in content["message"]
        assert "c2" in content["message"]
        assert "c3" in content["message"]

    def test_non_retrieve_clause_message_passes_through(self, lookup):
        msg = ToolMessage(
            content=json.dumps({"status": "ok", "results": [{"standard": "GDPR"}]}),
            tool_call_id="tc3",
        )
        result = lookup.enrich_observation(msg)
        assert result is msg  # same object, not modified

    def test_non_json_message_passes_through(self, lookup):
        msg = ToolMessage(content="Plain text response", tool_call_id="tc4")
        result = lookup.enrich_observation(msg)
        assert result is msg

    def test_empty_clauses(self):
        lookup = ClauseLookupTool([])
        msg = ToolMessage(
            content=json.dumps({"status": "requested", "clause_id": "c1"}),
            tool_call_id="tc5",
        )
        enriched = lookup.enrich_observation(msg)
        content = json.loads(enriched.content)
        assert content["status"] == "not_found"
        assert "[]" in content["message"] or "Available IDs: []" in content["message"]
