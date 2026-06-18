#!/usr/bin/env python3
"""Start all Contract Compliance Analyzer services.

Launches up to 4 services:
  - Risk & Compliance Agent — generalist (A2A, port 8005)
  - Risk & Compliance Agent — privacy specialist (A2A, port 8006)
  - Risk & Compliance Agent — financial specialist (A2A, port 8007)
  - Main API Server (FastAPI, port 8000)

Only the Risk & Compliance agents are separate A2A microservices — they're
the only components that genuinely need the protocol (ReAct reasoning loop
with dynamic tool calling). Contract parsing, verification, and decision
generation are single-pass LLM calls that run directly in the API process.

Usage:
    python scripts/run_agents.py                  # all 4 services
    python scripts/run_agents.py --api-only       # only the main API
    python scripts/run_agents.py --agents-only    # only the 3 risk agents
    python scripts/run_agents.py --profile core  # generalist risk + API
"""

import argparse
import multiprocessing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger, setup_logging

setup_logging()
logger = AuditLogger("run_agents", "launcher")


def run_risk_agent():
    """Start the Risk & Compliance Agent (generalist) A2A server."""
    from contract_analyzer.agents.a2a_servers import create_risk_agent_app
    port = int(config.risk_agent_url.rsplit(":", 1)[-1])
    logger.info("Starting Risk & Compliance Agent (generalist)", port=port)
    uvicorn.run(create_risk_agent_app(port), host="0.0.0.0", port=port, log_level="warning")


def run_risk_privacy_agent():
    """Start the Risk & Compliance Agent (privacy specialist) A2A server."""
    from contract_analyzer.agents.a2a_servers import create_risk_privacy_agent_app
    port = int(config.risk_privacy_agent_url.rsplit(":", 1)[-1])
    logger.info("Starting Risk & Compliance Agent (privacy specialist)", port=port)
    uvicorn.run(create_risk_privacy_agent_app(port), host="0.0.0.0", port=port, log_level="warning")


def run_risk_financial_agent():
    """Start the Risk & Compliance Agent (financial specialist) A2A server."""
    from contract_analyzer.agents.a2a_servers import create_risk_financial_agent_app
    port = int(config.risk_financial_agent_url.rsplit(":", 1)[-1])
    logger.info("Starting Risk & Compliance Agent (financial specialist)", port=port)
    uvicorn.run(create_risk_financial_agent_app(port), host="0.0.0.0", port=port, log_level="warning")


def run_api():
    """Start the main FastAPI server."""
    logger.info("Starting Contract Compliance Analyzer API Server", port=config.api_port)
    uvicorn.run(
        "contract_analyzer.api.main:app",
        host=config.api_host,
        port=config.api_port,
        log_level="info",
    )


def start_agent_processes(*funcs, daemon: bool = True) -> list[multiprocessing.Process]:
    procs = []
    for func in funcs:
        p = multiprocessing.Process(target=func, daemon=daemon)
        p.start()
        procs.append(p)
    return procs


def wait_for_processes(procs: list[multiprocessing.Process]) -> None:
    try:
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        logger.info("Shutting down agent servers")
        for p in procs:
            p.terminate()
        for p in procs:
            p.join(timeout=5)


def main():
    parser = argparse.ArgumentParser(description="Contract Compliance Analyzer Agent Launcher")
    parser.add_argument("--api-only", action="store_true", help="Run only the main API server")
    parser.add_argument("--agents-only", action="store_true", help="Run only the A2A risk agent servers")
    parser.add_argument(
        "--profile", choices=["core", "full", "privacy", "financial"], default="full",
        help="Agent profile: core (generalist risk), full (all 3 risk agents), "
             "privacy/financial (single specialist)"
    )
    args = parser.parse_args()

    logger.info("Contract Compliance Analyzer Agent Launcher starting")

    index_path = Path(config.faiss_index_path + ".faiss")
    if not index_path.exists():
        logger.warning("FAISS index not found. Run scripts/setup_standards_db.py first.")
        sys.exit(1)

    if args.api_only:
        run_api()
        return

    profile = args.profile

    profile_funcs = {
        "core": [run_risk_agent],
        "privacy": [run_risk_privacy_agent],
        "financial": [run_risk_financial_agent],
        "full": [run_risk_agent, run_risk_privacy_agent, run_risk_financial_agent],
    }
    agent_funcs = profile_funcs.get(profile, profile_funcs["full"])

    if args.agents_only:
        procs = start_agent_processes(*agent_funcs)
        logger.info(f"Started {len(procs)} A2A risk agent server(s)")
        wait_for_processes(procs)
        return

    procs = start_agent_processes(*agent_funcs)
    logger.info(f"Started {len(procs)} A2A risk agent server(s), starting API in main process")
    run_api()


if __name__ == "__main__":
    main()
