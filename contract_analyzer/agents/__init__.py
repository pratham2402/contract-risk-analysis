"""Contract analysis pipeline components — all run in-process.

- contract_understanding: clause extraction (single LLM call)
- risk_compliance: ReAct agent with tool calling (5 tools, dynamic retrieval)
- verification: evidence cross-reference verification (single LLM call)
- decision_recommendation: findings → recommendations converter (single LLM call)
"""