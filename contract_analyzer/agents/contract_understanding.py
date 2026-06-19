"""Contract Understanding Agent.

Parses contract text into structured clauses using LLM-based extraction.
"""

import json
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.models.output import ClauseType, ParsedClause

logger = AuditLogger(__name__, "contract_understanding_agent")

SYSTEM_PROMPT = """You are a contract analysis expert. Your job is to parse contract text
and identify all clauses with their types, titles, and line numbers. You must also extract
contract-level metadata critical for regulatory applicability analysis.

Output MUST be a JSON object with:
- governing_law: string - the governing law / jurisdiction clause text
- party_a_name: string - name of the first party (disclosing party, service provider, etc.)
- party_a_location: string - jurisdiction/address of the first party
- party_b_name: string - name of the second party
- party_b_location: string - jurisdiction/address of the second party
- contract_type: string - one of [nda, saas, vendor_agreement, employment, healthcare,
  payment_processing, educational, financial_services, consulting, other]
- subject_matter: string - brief description of what the contract covers
- data_involved: array of strings - types of data mentioned (e.g., "personal_data",
  "financial_data", "health_data", "payment_card_data", "student_records", "none")
- clauses: array of clause objects, each with:
  - clause_type: one of [liability, indemnification, data_protection, termination,
    payment, confidentiality, ip_rights, service_level, force_majeure, governing_law,
    insurance, warranty, audit_rights, subcontracting, other]
  - clause_number: the clause/section number if present (or null)
  - title: short descriptive title
  - text: the full clause text
  - start_line: starting line number (1-indexed)
  - end_line: ending line number (1-indexed)
  - metadata: object with any additional relevant info

Classify each clause accurately. If a section covers multiple topics, break it
into separate clauses with appropriate types. Do not skip any material clause.

Return ONLY valid JSON, no additional text."""


class ContractUnderstandingProcessor:
    """Core logic for parsing and classifying contract clauses."""

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            temperature=config.llm_temperature,
        )

    async def process(self, contract_text: str) -> dict:
        """Parse contract text into structured clauses."""
        start = time.monotonic()

        lines = contract_text.split("\n")
        numbered_lines = "\n".join(
            f"{i+1:04d}|{line}" for i, line in enumerate(lines)
        )

        response = await self.llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"Parse the following contract. Each line is prefixed "
                f"with its line number. Use these to record start_line and end_line:\n\n"
                f"{numbered_lines}"
            ),
        ])

        try:
            raw = response.content.strip()  # type: ignore[union-attr]
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM output: {e}", raw=raw[:500])
            return {"clauses": [], "error": str(e), "raw_output": raw[:1000]}

        clauses = []
        for item in data.get("clauses", []):
            try:
                clause_type = ClauseType(item.get("clause_type", "other"))
            except ValueError:
                clause_type = ClauseType.OTHER

            clauses.append(
                ParsedClause(
                    clause_type=clause_type,
                    clause_number=item.get("clause_number"),
                    title=item.get("title", ""),
                    text=item.get("text", ""),
                    start_line=item.get("start_line", 0),
                    end_line=item.get("end_line", 0),
                    metadata=item.get("metadata", {}),
                )
            )

        duration_ms = (time.monotonic() - start) * 1000
        logger.agent_call(
            "contract_understanding",
            "process",
            duration_ms,
            True,
            clause_count=len(clauses),
        )

        return {
            "clauses": [c.model_dump() for c in clauses],
            "total_clauses": len(clauses),
            "processing_time_ms": duration_ms,
            "governing_law": data.get("governing_law", ""),
            "party_a_name": data.get("party_a_name", ""),
            "party_a_location": data.get("party_a_location", ""),
            "party_b_name": data.get("party_b_name", ""),
            "party_b_location": data.get("party_b_location", ""),
            "contract_type": data.get("contract_type", ""),
            "subject_matter": data.get("subject_matter", ""),
            "data_involved": data.get("data_involved", []),
        }

processor = ContractUnderstandingProcessor()
