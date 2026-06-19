"""FAISS vector index for compliance standards retrieval.

Builds and queries a FAISS index populated with embeddings of curated
standards summaries. Uses sentence-transformers for embedding generation.
"""

import os
import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.retrieval.standards_data import STANDARDS_ENTRIES, StandardEntry

logger = AuditLogger(__name__, "standards_index")


class StandardsIndex:
    """Manages the FAISS index of compliance standards entries."""

    def __init__(self) -> None:
        self.model: SentenceTransformer | None = None
        self.index: faiss.Index | None = None
        self.entries: list[StandardEntry] = []
        self.embeddings: np.ndarray | None = None

    @property
    def is_loaded(self) -> bool:
        return self.index is not None and self.model is not None

    def load_model(self, model_name: str | None = None) -> None:
        if self.model is None:
            model_name = model_name or config.embedding_model
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)

    def build_index(self) -> None:
        """Build FAISS index from standards entries."""
        self.load_model()
        self.entries = list(STANDARDS_ENTRIES)

        texts = [
            f"{e.standard} {e.article or ''} {e.topic} {e.title} {e.content}"
            for e in self.entries
        ]

        logger.info(f"Building embeddings for {len(texts)} standards entries")
        self.embeddings = self.model.encode(  # type: ignore[union-attr]
            texts, show_progress_bar=True, normalize_embeddings=True
        )

        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # inner product for cosine sim
        self.index.add(self.embeddings.astype(np.float32))

        logger.info(f"FAISS index built with {self.index.ntotal} vectors (dim={dim})")

    def save(self, path: str | None = None) -> None:
        path = path or config.faiss_index_path
        os.makedirs(os.path.dirname(path), exist_ok=True)

        faiss.write_index(self.index, f"{path}.faiss")  # type: ignore[arg-type]
        with open(f"{path}_entries.pkl", "wb") as f:
            pickle.dump(self.entries, f)
        if self.embeddings is not None:
            np.save(f"{path}_embeddings.npy", self.embeddings)

        logger.info(f"Index saved to {path}")

    def load(self, path: str | None = None) -> None:
        """Load FAISS index from disk.

        Index files are keyed by embedding model name to avoid collisions
        when switching between general-purpose and legal-domain models.
        If a custom path is provided, use it as-is (no model slug appended).
        """
        if path is not None:
            # Custom path: use as-is
            pass
        else:
            path = config.faiss_index_path
            model_slug = config.embedding_model.replace("/", "_").replace("-", "_")
            path = f"{path}_{model_slug}"
        self.load_model()

        idx_path = f"{path}.faiss"
        entries_path = f"{path}_entries.pkl"
        emb_path = f"{path}_embeddings.npy"

        if not Path(idx_path).exists():
            # Fall back to default path for backward compatibility
            orig_path = config.faiss_index_path
            idx_path = f"{orig_path}.faiss"
            entries_path = f"{orig_path}_entries.pkl"
            emb_path = f"{orig_path}_embeddings.npy"
            if not Path(idx_path).exists():
                raise FileNotFoundError(
                    f"FAISS index not found at {idx_path}. Run setup_standards_db.py first."
                )

        self.index = faiss.read_index(idx_path)
        with open(entries_path, "rb") as f:
            self.entries = pickle.load(f)
        if Path(emb_path).exists():
            self.embeddings = np.load(emb_path)

        logger.info(f"Loaded index: {self.index.ntotal} vectors")

    def query(
        self, text: str, top_k: int = 5, min_score: float = 0.0,
        jurisdiction: str | None = None,
        standard_category: str | None = None,
    ) -> list[dict]:
        """Query standards index for relevant entries with optional metadata filtering.

        Args:
            text: Query text (e.g., a contract clause or risk description).
            top_k: Number of results to return.
            min_score: Minimum similarity score threshold.
            jurisdiction: Optional jurisdiction filter (post-retrieval).
            standard_category: Optional category filter (post-retrieval).

        Returns:
            List of dicts with keys: standard, article, topic, title,
            content, score, tags, jurisdiction, standard_category,
            authority_level.
        """
        if not self.is_loaded:
            raise RuntimeError("Index not loaded. Call load() or build_index() first.")

        query_vec = self.model.encode(  # type: ignore[union-attr]
            [text], normalize_embeddings=True
        ).astype(np.float32)

        # Retrieve more candidates if we plan to filter
        fetch_k = top_k * 3 if (jurisdiction or standard_category) else top_k
        scores, indices = self.index.search(query_vec, fetch_k)  # type: ignore[union-attr]

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.entries):
                continue
            if score < min_score:
                continue
            entry = self.entries[idx]

            # Post-retrieval metadata filter
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
                "score": float(score),
                "tags": entry.tags,
                "jurisdiction": entry.jurisdiction,
                "standard_category": entry.standard_category,
                "authority_level": entry.authority_level,
            })

            if len(results) >= top_k:
                break

        return results


_standards_index: StandardsIndex | None = None


def get_standards_index() -> StandardsIndex:
    """Get or create the global standards index singleton."""
    global _standards_index
    if _standards_index is not None and _standards_index.is_loaded:
        return _standards_index

    # Build/load first, only assign to global after fully ready.
    # This prevents concurrent callers from seeing a partially-loaded index.
    index = StandardsIndex()
    idx_path = config.faiss_index_path
    if Path(f"{idx_path}.faiss").exists():
        index.load()
    else:
        logger.warning("FAISS index not found, building from scratch")
        index.build_index()
        index.save()
    _standards_index = index
    return _standards_index
