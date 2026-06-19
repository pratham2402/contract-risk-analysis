"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (walk up from this file's location)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


@dataclass
class Config:
    """Contract Compliance Analyzer configuration."""

    # LLM
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o")
    llm_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Vector DB
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "data/standards_index")

    # Hybrid retrieval weights
    vector_weight: float = float(os.getenv("VECTOR_WEIGHT", "0.7"))
    bm25_weight: float = float(os.getenv("BM25_WEIGHT", "0.3"))

    # Agent behavior
    risk_agent_max_iterations: int = int(os.getenv("RISK_AGENT_MAX_ITERATIONS", "10"))

    # Verification
    verification_enabled: bool = os.getenv("VERIFICATION_ENABLED", "true").lower() == "true"
    verification_flag_threshold: int = int(os.getenv("VERIFICATION_FLAG_THRESHOLD", "2"))

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://contract_analyzer:contract_analyzer@localhost:5432/contract_analyzer",
    )

    # File upload
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # API server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Feature flags
    use_hybrid_retrieval: bool = True


config = Config()
