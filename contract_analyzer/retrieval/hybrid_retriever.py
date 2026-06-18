"""Hybrid retrieval combining BM25 sparse search with FAISS dense vector search.

Uses Reciprocal Rank Fusion (RRF) to merge result lists from both indexes,
with pre-retrieval metadata filtering on jurisdiction, standard category,
and authority level.
"""

from typing import Any

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.retrieval.bm25_index import get_bm25_index
from contract_analyzer.retrieval.metadata_filter import RetrievalFilters
from contract_analyzer.retrieval.standards_index import get_standards_index as get_faiss_index

logger = AuditLogger(__name__, "hybrid_retriever")


def _reciprocal_rank_fusion(
    dense_results: list[dict[str, Any]],
    sparse_results: list[dict[str, Any]],
    k: int = 60,
    dense_weight: float = 0.7,
    sparse_weight: float = 0.3,
) -> list[dict[str, Any]]:
    """Fuse two ranked result lists using Reciprocal Rank Fusion.

    Each document gets score = sum(weight / (k + rank_position)) from each
    ranked list it appears in. Results with higher fused scores are ranked
    higher. The "standard|article" key is used as the document identifier.
    """
    rrf_scores: dict[str, float] = {}
    doc_map: dict[str, dict[str, Any]] = {}

    # Score dense results
    for rank, doc in enumerate(dense_results, start=1):
        key = f"{doc['standard']}|{doc.get('article') or 'none'}"
        rrf_scores[key] = dense_weight / (k + rank)
        doc_map[key] = doc

    # Score sparse results
    for rank, doc in enumerate(sparse_results, start=1):
        key = f"{doc['standard']}|{doc.get('article') or 'none'}"
        current = rrf_scores.get(key, 0.0)
        rrf_scores[key] = current + sparse_weight / (k + rank)
        if key not in doc_map:
            doc_map[key] = doc

    # Sort by fused score descending
    sorted_keys = sorted(rrf_scores, key=rrf_scores.get, reverse=True)  # type: ignore[arg-type]

    results = []
    for key in sorted_keys:
        doc = doc_map[key]
        doc["fused_score"] = rrf_scores[key]
        doc["dense_score"] = doc.get("score", 0.0)
        results.append(doc)

    return results


class HybridRetriever:
    """Combines BM25 + FAISS retrieval with metadata filtering and RRF fusion."""

    def __init__(
        self,
        dense_weight: float | None = None,
        sparse_weight: float | None = None,
    ) -> None:
        self._faiss = get_faiss_index()
        self._bm25 = get_bm25_index()
        self.dense_weight = dense_weight if dense_weight is not None else config.vector_weight
        self.sparse_weight = sparse_weight if sparse_weight is not None else config.bm25_weight

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.0,
        jurisdiction: str | None = None,
        standard_category: str | None = None,
        authority_level: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve standards entries using hybrid BM25 + vector search.

        Args:
            query: Search query text.
            top_k: Number of results to return after fusion.
            min_score: Minimum fused score threshold.
            jurisdiction: Optional jurisdiction filter.
            standard_category: Optional category filter.
            authority_level: Optional authority level filter.

        Returns:
            Fused and filtered results list.
        """
        filters = RetrievalFilters(
            jurisdiction=jurisdiction,
            standard_category=standard_category,
            authority_level=authority_level,
        )
        logger.info(
            f"Hybrid retrieval: '{query[:80]}...' with {filters.describe()}"
        )

        # Retrieve more candidates from each index to allow fusion to work well
        candidate_k = max(top_k * 3, 30)

        # Dense retrieval (FAISS supports metadata filtering on entry fields)
        dense_results = self._faiss.query(query, top_k=candidate_k, min_score=0.0)

        # Sparse retrieval (BM25)
        sparse_results = self._bm25.query(
            query,
            top_k=candidate_k,
            jurisdiction=jurisdiction,
            standard_category=standard_category,
        )

        # Fuse with RRF
        fused = _reciprocal_rank_fusion(
            dense_results,
            sparse_results,
            dense_weight=self.dense_weight,
            sparse_weight=self.sparse_weight,
        )

        # Post-fusion: apply metadata filtering and score threshold
        results = []
        for doc in fused:
            if doc["fused_score"] < min_score:
                continue
            # Re-check metadata filters against the fused document
            doc_with_meta = {
                **doc,
                "jurisdiction": doc.get("jurisdiction", "Global"),
                "standard_category": doc.get("standard_category", "general"),
                "authority_level": doc.get("authority_level", "framework"),
            }
            if filters.matches(doc_with_meta):
                doc["score"] = doc["fused_score"]  # normalize score field
                results.append(doc)

        return results[:top_k]


_hybrid_retriever: HybridRetriever | None = None


def get_hybrid_retriever() -> HybridRetriever:
    """Get or create the global hybrid retriever singleton."""
    global _hybrid_retriever
    if _hybrid_retriever is not None:
        return _hybrid_retriever

    # Build first, only assign to global after fully initialized.
    # This prevents concurrent callers from seeing a partially-loaded retriever.
    retriever = HybridRetriever()
    _hybrid_retriever = retriever
    return _hybrid_retriever


def query_standards_hybrid(
    query: str,
    top_k: int = 10,
    min_score: float = 0.0,
    jurisdiction: str | None = None,
    standard_category: str | None = None,
    authority_level: str | None = None,
) -> list[dict[str, Any]]:
    """Convenience function for hybrid standards retrieval."""
    return get_hybrid_retriever().retrieve(
        query=query,
        top_k=top_k,
        min_score=min_score,
        jurisdiction=jurisdiction,
        standard_category=standard_category,
        authority_level=authority_level,
    )
