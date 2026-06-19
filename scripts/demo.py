#!/usr/bin/env python3
"""End-to-end demo of Contract Regulatory Compliance Scanner.

Demonstrates the full pipeline:
  1. Contract parsing — extract clauses, parties, governing law
  2. Risk evaluation — ReAct agent retrieves and applies regulatory standards
  3. Verification — cross-reference findings against retrieved evidence
  4. Decision generation — prioritized recommendations with owner assignments

Usage:
    python scripts/demo.py                    # run with sample NDA
    python scripts/demo.py --contract data/sample_contracts/risky_saas.txt
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger, setup_logging
from contract_analyzer.orchestrator.workflow import orchestrator
from contract_analyzer.models.output import RiskLevel, Decision

setup_logging()
logger = AuditLogger("demo", "demo_runner")

SAMPLE_NDA = str(Path(__file__).parent.parent / "data" / "sample_contracts" / "standard_nda.txt")
SAMPLE_SAAS = str(Path(__file__).parent.parent / "data" / "sample_contracts" / "risky_saas.txt")


def print_header(text: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_finding(f, idx: int) -> None:
    risk_colors = {
        "critical": "\033[91m",
        "high": "\033[93m",
        "medium": "\033[33m",
        "low": "\033[92m",
        "info": "\033[90m",
    }
    reset = "\033[0m"
    color = risk_colors.get(f.risk_level.value, "")

    print(f"\n  [{idx}] {color}{f.risk_level.value.upper()}{reset} - {f.issue_description}")
    print(f"      Category: {f.category}")
    if f.referenced_standards:
        refs = ", ".join(
            f"{r.standard} {r.article or ''}".strip() for r in f.referenced_standards
        )
        print(f"      Standards: {refs}")
    print(f"      Explanation: {f.explanation[:200]}...")
    print(f"      Confidence: {f.confidence:.0%}")
    if f.reasoning_trace:
        print(f"      Reasoning: {f.reasoning_trace[:150]}...")


def print_recommendation(r, idx: int) -> None:
    decision_colors = {
        "approve": "\033[92m",
        "escalate": "\033[93m",
        "block": "\033[91m",
    }
    reset = "\033[0m"

    print(f"\n  [{idx}] {decision_colors.get(r.decision.value, '')}{r.decision.value.upper()}{reset} | "
          f"Priority: {r.priority}/5 | Owner: {r.owner.value}")
    print(f"      Action: {r.recommended_action[:200]}...")
    if r.negotiation_suggestion:
        print(f"      Negotiation: {r.negotiation_suggestion[:150]}...")


async def run_demo(contract_path: str, contract_name: str = "") -> None:
    contract_text = Path(contract_path).read_text()
    if not contract_name:
        contract_name = Path(contract_path).name

    print_header(f"Contract Compliance Analyzer Analysis: {contract_name}")
    print(f"\n  Contract length: {len(contract_text)} chars, ~{len(contract_text.splitlines())} lines")
    print(f"  API Key configured: {'Yes' if config.llm_api_key else 'No'}")

    if not config.llm_api_key:
        print("\n  WARNING: OPENAI_API_KEY not set. LLM calls will fail.")
        print("  Set it in .env or export OPENAI_API_KEY=your-key")
        return

    print("\n  Starting analysis pipeline...")

    try:
        analysis = await orchestrator.analyze(contract_text, contract_name)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Clauses
    print_header(f"Extracted Clauses: {len(analysis.clauses)}")
    for i, clause in enumerate(analysis.clauses, 1):
        print(f"  [{i}] [{clause.clause_type.value}] {clause.title}")
        print(f"      Text: {clause.text[:100]}...")

    # Findings
    print_header(f"Risk Findings: {len(analysis.findings)}")
    for i, f in enumerate(analysis.findings, 1):
        print_finding(f, i)

    # Recommendations
    print_header(f"Recommendations: {len(analysis.recommendations)}")
    for i, r in enumerate(analysis.recommendations, 1):
        print_recommendation(r, i)

    # Summary
    print_header("Analysis Summary")
    s = analysis.summary
    print(f"  Total Clauses:     {s.get('total_clauses', 'N/A')}")
    print(f"  Total Findings:    {s.get('total_findings', 'N/A')}")
    print(f"  Recommendations:   {s.get('total_recommendations', 'N/A')}")
    print(f"  Duration:          {analysis.total_duration_ms:.0f}ms")
    print(f"  Risk Distribution:")
    for level, count in s.get("risk_counts", {}).items():
        if count > 0:
            print(f"    {level}: {count}")
    print(f"  Decision Distribution:")
    for dec, count in s.get("decision_counts", {}).items():
        if count > 0:
            print(f"    {dec}: {count}")

    # Audit trail
    print_header("Audit Trail")
    for entry in analysis.audit_trail:
        ts = entry.get("timestamp", "")[:19]
        stage = entry.get("stage", "")
        action = entry.get("action", "")
        extra = {k: v for k, v in entry.items() if k not in ("timestamp", "stage", "action")}
        extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
        print(f"  [{ts}] {stage:25s} | {action:40s} | {extra_str}")

    print_header("Demo Complete")
    print(f"\n  Results saved in-memory. Use the API to persist and review.")
    print(f"  Start the UI: python scripts/run_agents.py --api-only")
    print(f"  Then open http://localhost:{config.api_port}/console\n")


def main():
    parser = argparse.ArgumentParser(description="Contract Compliance Analyzer End-to-End Demo")
    parser.add_argument(
        "--contract", "-c",
        default=SAMPLE_NDA,
        help=f"Path to contract text file (default: {SAMPLE_NDA})",
    )
    parser.add_argument("--name", "-n", default="", help="Contract name")
    args = parser.parse_args()

    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"Contract file not found: {args.contract}")
        print(f"Available samples:")
        for p in [SAMPLE_NDA, SAMPLE_SAAS]:
            print(f"  {p}")
        sys.exit(1)

    asyncio.run(run_demo(str(contract_path), args.name))


if __name__ == "__main__":
    main()
