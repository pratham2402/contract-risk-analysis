#!/usr/bin/env python3
"""Build FAISS and BM25 indexes of compliance standards.

Run this once before starting the system, and after any changes to
standards_data.py or the embedding model:
    python3 scripts/setup_standards_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger, setup_logging
from contract_analyzer.retrieval.standards_index import StandardsIndex
from contract_analyzer.retrieval.bm25_index import BM25Index

setup_logging()
logger = AuditLogger("setup_standards_db", "setup")


def main():
    logger.info(
        "Building FAISS + BM25 standards indexes",
        model=config.embedding_model,
        output_path=config.faiss_index_path,
        hybrid=config.use_hybrid_retrieval,
    )

    # 1. FAISS dense index
    logger.info("--- Building FAISS index ---")
    index = StandardsIndex()
    index.load_model()
    index.build_index()
    index.save()
    logger.info(
        "FAISS index built",
        vectors=index.index.ntotal if index.index else 0,
        path=config.faiss_index_path,
    )

    # 2. BM25 sparse index
    logger.info("--- Building BM25 index ---")
    bm25 = BM25Index()
    bm25.build()
    bm25.save()
    logger.info("BM25 index built", documents=len(bm25.entries))

    # 3. Quick test queries
    logger.info("--- Test queries ---")
    test_queries = [
        "data breach notification requirements",
        "contract formation offer acceptance Delaware",
        "corporate director fiduciary duties indemnification",
    ]
    for q in test_queries:
        results = index.query(q, top_k=3, min_score=0.3)
        logger.info(f"Query: {q[:60]}...")
        for r in results:
            logger.info(
                f"  [{r['score']:.3f}] {r['standard']} {r['article']} - {r['title']}"
            )


if __name__ == "__main__":
    main()
