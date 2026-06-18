"""BM25 sparse retrieval index for hybrid search.

Provides keyword-based retrieval using rank_bm25 for exact term matching
to complement FAISS dense vector search. The BM25 index is built from the
same curated standards entries and supports jurisdiction/category metadata
filtering.
"""

import pickle
import re
from pathlib import Path
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.retrieval.standards_data import STANDARDS_ENTRIES, StandardEntry

logger = AuditLogger(__name__, "bm25_index")


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer with lowercase normalization."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]


class BM25Index:
    """BM25 Okapi index over standards entries with metadata filtering."""

    def __init__(self) -> None:
        self.entries: list[StandardEntry] = []
        self.bm25: BM25Okapi | None = None
        self._doc_texts: list[str] = []
        self._tokenized: list[list[str]] = []

    @property
    def is_loaded(self) -> bool:
        return self.bm25 is not None

    def build(self, entries: list[StandardEntry] | None = None) -> None:
        """Build BM25 index from standards entries."""
        self.entries = entries or list(STANDARDS_ENTRIES)

        self._doc_texts = [
            f"{e.standard} {e.article or ''} {e.topic} {e.title} {e.content}"
            for e in self.entries
        ]
        self._tokenized = [_tokenize(t) for t in self._doc_texts]
        self.bm25 = BM25Okapi(self._tokenized)

        logger.info(f"BM25 index built with {len(self.entries)} documents")

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        jurisdiction: str | None = None,
        standard_category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query the BM25 index with optional metadata filters.

        Args:
            query_text: Search query.
            top_k: Maximum results to return.
            jurisdiction: Optional jurisdiction filter (e.g., "US", "EU", "India").
            standard_category: Optional category filter.

        Returns:
            List of result dicts with standard, article, title, content, score, tags.
        """
        if not self.is_loaded:
            raise RuntimeError("BM25 index not loaded. Call build() first.")

        tokens = _tokenize(query_text)
        scores = self.bm25.get_scores(tokens)

        # Score all then filter by metadata, keeping top_k * 4 candidates
        candidate_count = top_k * 4
        top_indices = np.argsort(scores)[::-1][:candidate_count]

        results: list[dict[str, Any]] = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            entry = self.entries[idx]

            # Metadata filter
            if jurisdiction and entry.jurisdiction != "Global" and entry.jurisdiction != jurisdiction:
                continue
            if standard_category and entry.standard_category != standard_category:
                continue

            results.append({
                "standard": entry.standard,
                "article": entry.article,
                "topic": entry.topic,
                "title": entry.title,
                "content": entry.content,
                "score": float(scores[idx]),
                "tags": entry.tags,
                "jurisdiction": entry.jurisdiction,
                "standard_category": entry.standard_category,
                "authority_level": entry.authority_level,
            })

        return results[:top_k]

    def save(self, path: str | None = None) -> None:
        path = path or f"{config.faiss_index_path}_bm25.pkl"
        with open(path, "wb") as f:
            pickle.dump({
                "entries": self.entries,
                "doc_texts": self._doc_texts,
                "tokenized": self._tokenized,
            }, f)
        logger.info(f"BM25 index saved to {path}")

    def load(self, path: str | None = None) -> None:
        path = path or f"{config.faiss_index_path}_bm25.pkl"
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"BM25 index not found at {path}. Build it first.")

        with open(path, "rb") as f:
            data = pickle.load(f)
        self.entries = data["entries"]
        self._doc_texts = data["doc_texts"]
        self._tokenized = data["tokenized"]
        self.bm25 = BM25Okapi(self._tokenized)
        logger.info(f"BM25 index loaded: {len(self.entries)} documents")


_bm25_index: BM25Index | None = None


def get_bm25_index() -> BM25Index:
    global _bm25_index
    if _bm25_index is not None and _bm25_index.is_loaded:
        return _bm25_index

    index = BM25Index()
    pkl_path = f"{config.faiss_index_path}_bm25.pkl"
    if Path(pkl_path).exists():
        index.load(pkl_path)
    else:
        index.build()
        index.save(pkl_path)
    _bm25_index = index
    return _bm25_index
