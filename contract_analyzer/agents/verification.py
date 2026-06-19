"""Verification Agent.

Validates every cited standard in Risk Agent findings against the retrieved
evidence set. Produces a VerificationReport flagging hallucinated citations,
unsupported references, disconnected reasoning, and risk-level mismatches.

This is NOT an agentic component — it's a single structured LLM call.
"""

import json
import re
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.models.output import VerificationFlag, VerificationReport

logger = AuditLogger(__name__, "verification_agent")

# ── Article range normalization ──────────────────────────────────────────────
# Curated standards data uses range notation (e.g., "Art. 33-34") but the
# risk agent may cite a specific article within that range ("Art. 33").
# Expanding ranges before sending to the verifier prevents false
# "unsupported_citation" flags from exact-string mismatches.

_MAX_RANGE_EXPANSION = 20  # don't expand ranges larger than this


def _expand_article_ranges(article: str) -> str:
    """Expand article range notation into an explicit comma-separated list.

    >>> _expand_article_ranges("Art. 33-34")
    'Art. 33, Art. 34'
    >>> _expand_article_ranges("S. 3-5, 10A")
    'S. 3, S. 4, S. 5, S. 10A'
    >>> _expand_article_ranges("Req. 1-2")
    'Req. 1, Req. 2'
    >>> _expand_article_ranges("Art. 5")
    'Art. 5'
    """
    if not article:
        return article

    parts = [p.strip() for p in article.split(",")]
    expanded: list[str] = []

    for part in parts:
        # Skip complex legal cites like "§§ 2-711-2-717" (multi-level dashes)
        if part.count("-") > 1:
            expanded.append(part)
            continue

        # Pattern: "PREFIX<N>-<M>" where N and M are digits and prefix ends
        # with a non-digit character (or is empty).  Captures:
        #   "Art. 33-34"   → prefix="Art. ",  start=33, end=34
        #   "Annex A.8.28-29" → prefix="Annex A.8.", start=28, end=29
        #   "1798.100-1798.125" → prefix="1798.", start=100, end=125
        m = re.match(r"^(.+?)(\d+)-(\d+)$", part)
        if m:
            prefix = m.group(1)
            start, end = int(m.group(2)), int(m.group(3))
            # Only expand if the prefix is short (not a complex cite) and
            # the range is reasonable.
            if end > start and len(prefix) < 40 and (end - start) <= _MAX_RANGE_EXPANSION:
                for i in range(start, end + 1):
                    expanded.append(f"{prefix}{i}")
                continue

        # Pattern: "LETTER<N>-LETTER<M>" — same letter prefix, numeric range.
        #   "CC3-CC4" → prefix="CC", start=3, end=4
        #   "P1-P8"    → prefix="P",  start=1, end=8
        m = re.match(r"^([A-Za-z]+)(\d+)-([A-Za-z]+)(\d+)$", part)
        if m:
            pfx_start, num_start = m.group(1), int(m.group(2))
            pfx_end, num_end = m.group(3), int(m.group(4))
            if pfx_start == pfx_end and num_end > num_start and (num_end - num_start) <= _MAX_RANGE_EXPANSION:
                for i in range(num_start, num_end + 1):
                    expanded.append(f"{pfx_start}{i}")
                continue

        # No expansion — keep the original part
        expanded.append(part)

    return ", ".join(expanded)

VERIFICATION_SYSTEM_PROMPT = """You are a forensic compliance auditor. Your job is to validate
every citation a Risk & Compliance Agent produced against a set of retrieved evidence.

## WHAT YOU DO

For every finding, you check:
1. **Citation integrity**: Every standard/article cited in `referenced_standards`
   must appear in the retrieved evidence set. The evidence `article` field may
   have been expanded from range notation (e.g., "Art. 33-34" → "Art. 33, Art. 34")
   — a citation to *any* article within an expanded range is a VALID match.
2. **Reasoning-to-evidence connection**: The `reasoning_trace` must reference
   specific retrieved excerpts. If reasoning asserts something not in evidence, flag it.
3. **Risk-level calibration**: Does the risk_level match the severity described
   in the explanation and supporting evidence?
4. **Generic exclusion check**: Were standards excluded with generic reasons
   ("not applicable", "out of scope") without substantive justification?

## ARTICLE MATCHING RULES (most important)

- If the evidence article field contains a comma-separated list (e.g., "Art. 33, Art. 34"
  or "S. 3, S. 4, S. 5"), a citation to ANY single article in that list is VALID.
- If evidence has an `article_original` field showing the original range notation, that
  tells you the article field was expanded — the range covers ALL articles between
  the endpoints.
- Only flag `unsupported_citation` when the cited article number is clearly OUTSIDE
  the evidence coverage, or when the article field is a single value that doesn't match.
- A citation like "Art. 33" against evidence whose article field includes "Art. 33"
  (even as part of a list) is a MATCH — do NOT flag it.

## FLAG TYPES

- `hallucinated_citation`: A standard/article cited in findings does not appear
  at all in the retrieved evidence set (the standard name is absent entirely).
- `unsupported_citation`: The standard exists in evidence but the specific article
  number cited falls clearly outside the evidence coverage.
- `disconnected_reasoning`: The reasoning trace makes claims not supported by
  any retrieved excerpt.
- `risk_level_mismatch`: The risk_level assigned is inconsistent with the
  evidence-supported severity.
- `generic_exclusion`: A standard was excluded with a vague, non-substantive reason.

## SEVERITY

- `block`: The finding is fundamentally unreliable (hallucinated core citation —
  the standard itself doesn't exist in evidence).
- `warn`: The finding has issues but may still be directionally correct
  (includes imprecise article references, weak reasoning connections, borderline risk levels).
- `info`: Minor issue, likely not impactful.

## OUTPUT FORMAT

Return a JSON object:
{
  "verified": true/false,
  "flags": [
    {
      "finding_id": "...",
      "flag_type": "hallucinated_citation|unsupported_citation|disconnected_reasoning|risk_level_mismatch|generic_exclusion",
      "severity": "block|warn|info",
      "detail": "specific description of what was found"
    }
  ],
  "hallucination_count": 0,
  "adjusted_confidence": 0.0
}

## RULES

- Be precise: flag only what you can prove from the evidence.
- If a citation is partially correct (standard matches but article is wrong or
  imprecise), use `unsupported_citation` at `warn` severity — NOT `block`.
- `block` severity is reserved for `hallucinated_citation` where the standard
  itself is fabricated.
- Count every hallucinated or unsupported citation in `hallucination_count`.
- If no issues found, verified=true with empty flags.
- `adjusted_confidence` is the average confidence across all findings after
  penalizing for flags: -0.2 per block, -0.1 per warn, -0.05 per info.
  Floor at 0.0, cap at 1.0.
"""


class VerificationProcessor:
    """Validates Risk Agent findings against retrieved evidence."""

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            temperature=0.0,  # deterministic for audit
        )

    def _build_input(
        self,
        findings: list[dict],
        retrieved_evidence: list[dict],
    ) -> str:
        """Build the verification input payload.

        Article ranges in evidence are expanded so that the verifier can
        correctly match a citation like "Art. 33" against evidence whose
        curated article field reads "Art. 33-34".
        """
        # Normalize evidence articles to expand ranges
        norm_evidence: list[dict] = []
        for e in retrieved_evidence:
            raw_article = e.get("article")
            normalized = _expand_article_ranges(raw_article) if raw_article else raw_article
            entry: dict = {
                "standard": e.get("standard", ""),
                "article": normalized,
                "title": e.get("title", ""),
                "content": e.get("content", "")[:800],
            }
            # Include the original article text so the verifier knows a range
            # expansion happened — prevents confusion when the article field
            # suddenly contains a long comma-separated list.
            if normalized != raw_article:
                entry["article_original"] = raw_article
                entry["_note"] = (
                    "article field was expanded from the original range notation "
                    "for matching convenience"
                )
            norm_evidence.append(entry)

        return json.dumps({
            "task": "Validate the following compliance findings against the retrieved evidence.",
            "findings": [
                {
                    "id": f.get("id", ""),
                    "clause_id": f.get("clause_id"),
                    "issue_description": f.get("issue_description", ""),
                    "risk_level": f.get("risk_level", ""),
                    "category": f.get("category", ""),
                    "referenced_standards": f.get("referenced_standards", []),
                    "explanation": f.get("explanation", ""),
                    "reasoning_trace": f.get("reasoning_trace", ""),
                    "confidence": f.get("confidence", 1.0),
                }
                for f in findings
            ],
            "retrieved_evidence": norm_evidence,
        }, indent=2)

    async def process(
        self,
        findings_json: str,
        evidence_json: str = "",
    ) -> dict:
        """Validate findings against evidence.

        Args:
            findings_json: JSON string of findings list.
            evidence_json: JSON string of retrieved evidence list.

        Returns:
            Dict with verification_report ready for VerificationReport model.
        """
        start = time.monotonic()

        findings = (
            json.loads(findings_json) if isinstance(findings_json, str)
            else findings_json
        )
        if isinstance(findings, dict):
            findings = findings.get("findings", [])
        if not isinstance(findings, list):
            findings = []

        evidence = (
            json.loads(evidence_json) if isinstance(evidence_json, str)
            else evidence_json
        )
        if isinstance(evidence, dict):
            evidence = evidence.get("evidence", evidence.get("results", []))
        if not isinstance(evidence, list):
            evidence = []

        if not findings:
            duration_ms = (time.monotonic() - start) * 1000
            report = VerificationReport(
                verified=True,
                total_findings=0,
                total_citations=0,
                adjusted_confidence=0.0,
            )
            return {
                "verification_report": report.model_dump(),
                "processing_time_ms": duration_ms,
            }

        messages = [
            SystemMessage(content=VERIFICATION_SYSTEM_PROMPT),
            HumanMessage(content=self._build_input(findings, evidence)),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # Parse JSON from response
        result = self._parse_response(content)

        total_citations = sum(
            len(f.get("referenced_standards", [])) for f in findings
        )
        flags = []
        for flag_data in result.get("flags", []):
            flags.append(VerificationFlag(
                finding_id=flag_data.get("finding_id", ""),
                flag_type=flag_data.get("flag_type", "unsupported_citation"),
                severity=flag_data.get("severity", "warn"),
                detail=flag_data.get("detail", ""),
            ))

        hallucination_count = sum(
            1 for f in flags
            if f.flag_type in ("hallucinated_citation", "unsupported_citation")
        )

        # Compute adjusted confidence
        penalty = 0.0
        for f in flags:
            if f.severity == "block":
                penalty += 0.2
            elif f.severity == "warn":
                penalty += 0.1
            else:
                penalty += 0.05

        avg_confidence = (
            sum(f.get("confidence", 1.0) for f in findings) / len(findings)
            if findings else 1.0
        )
        adjusted = max(0.0, min(1.0, avg_confidence - penalty / max(len(findings), 1)))

        report = VerificationReport(
            verified=result.get("verified", len(flags) == 0),
            total_findings=len(findings),
            total_citations=total_citations,
            flags=flags,
            hallucination_count=hallucination_count,
            adjusted_confidence=adjusted,
        )

        duration_ms = (time.monotonic() - start) * 1000
        logger.agent_call(
            "verification",
            "verify",
            duration_ms,
            report.verified,
            finding_count=len(findings),
            flag_count=len(flags),
            hallucination_count=hallucination_count,
        )

        return {
            "verification_report": report.model_dump(),
            "processing_time_ms": duration_ms,
        }

    def _parse_response(self, content: str) -> dict:
        """Extract JSON from LLM response."""
        if isinstance(content, dict):
            return content

        content_str = str(content)
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0]
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0]

        try:
            return json.loads(content_str.strip())
        except json.JSONDecodeError:
            logger.warning("Verification: could not parse JSON from LLM output")
            return {"verified": False, "flags": [], "hallucination_count": 0}

verification_processor = VerificationProcessor()
