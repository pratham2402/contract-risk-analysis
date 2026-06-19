#!/usr/bin/env python3
"""Start the Contract Compliance Analyzer API server.

All agents (contract parsing, risk compliance with ReAct loop,
verification, decision generation) run in-process. No separate
microservices needed.

Usage:
    python scripts/run_agents.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger, setup_logging

setup_logging()
logger = AuditLogger("run_agents", "launcher")


def main():
    index_path = Path(config.faiss_index_path + ".faiss")
    if not index_path.exists():
        logger.warning("FAISS index not found. Run scripts/setup_standards_db.py first.")
        sys.exit(1)

    logger.info("Starting Contract Compliance Analyzer API Server", port=config.api_port)
    uvicorn.run(
        "contract_analyzer.api.main:app",
        host=config.api_host,
        port=config.api_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
