"""Tests for hybrid retrieval Reciprocal Rank Fusion and filter logic.

These test the fusion algorithm and filter application in isolation.
Index-building tests are skipped when no FAISS/BM25 data exists.
"""

import math

import pytest

from contract_analyzer.retrieval.hybrid_retriever import _reciprocal_rank_fusion
from contract_analyzer.retrieval.metadata_filter import RetrievalFilters


def _make_doc(standard, article="1", score=0.9, jurisdiction="US",
              category="data_protection", authority="regulation"):
    return {
        "standard": standard,
        "article": article,
        "title": f"{standard} Title",
        "content": f"Content for {standard}",
        "score": score,
        "jurisdiction": jurisdiction,
        "standard_category": category,
        "authority_level": authority,
    }


class TestReciprocalRankFusion:
    def test_empty_inputs(self):
        result = _reciprocal_rank_fusion([], [])
        assert result == []

    def test_dense_only(self):
        dense = [_make_doc("GDPR"), _make_doc("CCPA")]
        result = _reciprocal_rank_fusion(dense, [])
        assert len(result) == 2

    def test_sparse_only(self):
        sparse = [_make_doc("GDPR"), _make_doc("HIPAA")]
        result = _reciprocal_rank_fusion([], sparse)
        assert len(result) == 2

    def test_overlap_boosts_score(self):
        """Documents appearing in both lists should get boosted."""
        gdpr = _make_doc("GDPR")
        dense = [gdpr, _make_doc("CCPA")]
        sparse = [gdpr, _make_doc("HIPAA")]

        result = _reciprocal_rank_fusion(dense, sparse)
        # GDPR should be first (boosted by appearing in both lists)
        assert result[0]["standard"] == "GDPR"
        # Should have fused_score from both lists
        assert result[0]["fused_score"] > 0

    def test_fusion_is_deterministic(self):
        dense = [_make_doc("GDPR"), _make_doc("CCPA")]
        sparse = [_make_doc("HIPAA"), _make_doc("PCI DSS", score=0.7)]

        r1 = _reciprocal_rank_fusion(dense, sparse)
        r2 = _reciprocal_rank_fusion(dense, sparse)
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a["standard"] == b["standard"]
            assert a["fused_score"] == b["fused_score"]

    def test_weights_affect_ranking(self):
        doc_a = _make_doc("A", score=0.95)
        doc_b = _make_doc("B", score=0.5)

        # Rank doc_a high in dense, low in sparse; doc_b opposite
        dense = [doc_a, doc_b]
        sparse = [doc_b, doc_a]

        # Dense-heavy: A should rank higher
        result_dense_heavy = _reciprocal_rank_fusion(
            dense, sparse, dense_weight=0.9, sparse_weight=0.1
        )
        # Sparse-heavy: B should rank higher
        result_sparse_heavy = _reciprocal_rank_fusion(
            dense, sparse, dense_weight=0.1, sparse_weight=0.9
        )

        # Top results should differ based on weight dominance
        assert result_dense_heavy[0]["standard"] == "A"
        assert result_sparse_heavy[0]["standard"] == "B"

    def test_k_parameter_effect(self):
        """Higher k reduces rank position differences."""
        # Use different documents in each list so overlap doesn't mask the effect
        dense = [_make_doc("A"), _make_doc("B"), _make_doc("C")]
        sparse = [_make_doc("C"), _make_doc("B"), _make_doc("A")]
        result_low_k = _reciprocal_rank_fusion(dense, sparse, k=1)
        result_high_k = _reciprocal_rank_fusion(dense, sparse, k=1000)

        # With very high k, rank differences between close items should be negligible.
        # Check that the top two have closer scores at high k than at low k.
        score_diff_low = abs(
            result_low_k[0]["fused_score"] - result_low_k[1]["fused_score"]
        )
        score_diff_high = abs(
            result_high_k[0]["fused_score"] - result_high_k[1]["fused_score"]
        )
        # At high k, the fusion is more uniform
        assert score_diff_high <= score_diff_low

    def test_unique_keys_based_on_standard_article(self):
        """Documents are identified by standard|article."""
        doc1 = _make_doc("GDPR", article="Art. 5")
        doc2 = _make_doc("GDPR", article="Art. 32")
        dense = [doc1, doc2]
        sparse = [doc2, doc1]
        result = _reciprocal_rank_fusion(dense, sparse)
        # Both should be present — different articles
        assert len(result) == 2


class TestHybridRetrieverConstruction:
    """Test that the HybridRetriever class exists and is importable.

    Full integration tests with live indexes are skipped when no index data exists.
    """
    def test_import(self):
        from contract_analyzer.retrieval.hybrid_retriever import (
            HybridRetriever,
            get_hybrid_retriever,
            query_standards_hybrid,
        )
        # Basic sanity: all imports resolve
        assert HybridRetriever is not None
        assert callable(get_hybrid_retriever)
        assert callable(query_standards_hybrid)


class TestFiltersWithHybrid:
    """Verify RetrievalFilters used by hybrid retriever work correctly."""
    def test_filter_applied_to_doc(self):
        filters = RetrievalFilters(
            jurisdiction="US",
            standard_category="data_protection",
            authority_level="regulation",
        )
        doc = _make_doc("GDPR", jurisdiction="US", category="data_protection", authority="regulation")
        assert filters.matches(doc)

    def test_filter_rejects_wrong_category(self):
        filters = RetrievalFilters(standard_category="security")
        doc = _make_doc("GDPR", category="data_protection")
        assert not filters.matches(doc)

    def test_global_passes_jurisdiction_filter(self):
        filters = RetrievalFilters(jurisdiction="India")
        doc = _make_doc("ISO 27001", jurisdiction="Global")
        assert filters.matches(doc)
