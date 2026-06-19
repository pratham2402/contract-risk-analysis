"""PostgreSQL persistence layer for contracts, analyses, and audit trails."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from contract_analyzer.config import config
from contract_analyzer.logging_setup import AuditLogger

logger = AuditLogger(__name__, "database")


class Base(DeclarativeBase):
    pass


class ContractRecord(Base):
    """Persisted contract and its analysis results."""

    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(500), default="")
    contract_text: Mapped[str] = mapped_column(Text, default="")
    analysis_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    total_duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    clause_count: Mapped[int] = mapped_column(Integer, default=0)
    finding_count: Mapped[int] = mapped_column(Integer, default=0)
    recommendation_count: Mapped[int] = mapped_column(Integer, default=0)


# Synchronous engine for simplicity (async available via config)
_engine = None
SessionLocal = None
_db_available = False

try:
    _engine = create_engine(
        config.database_url.replace("+asyncpg", ""),
        echo=False,
        pool_size=5,
        max_overflow=10,
        connect_args={"connect_timeout": 3},
    )
    _engine.connect().close()
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    _db_available = True
except Exception:
    logger.warning("PostgreSQL not available, running without persistence")


def init_db() -> None:
    """Create all tables if they don't exist."""
    if not _db_available:
        return
    Base.metadata.create_all(bind=_engine)
    logger.info("Database tables initialized")


def get_session() -> Session | None:
    """Get a new database session, or None if DB is unavailable."""
    if not _db_available or SessionLocal is None:
        return None
    return SessionLocal()


def save_contract(
    name: str,
    contract_text: str,
    analysis_result: dict[str, Any] | None = None,
    status: str = "pending",
    error: str | None = None,
    duration_ms: float = 0.0,
) -> str:
    """Persist a contract and its analysis to PostgreSQL."""
    if not _db_available:
        return "no-db"
    with get_session() as session:
        record = ContractRecord(
            name=name,
            contract_text=contract_text,
            analysis_json=analysis_result or {},
            status=status,
            error=error,
            total_duration_ms=duration_ms,
            clause_count=(
                len(analysis_result.get("clauses", [])) if analysis_result else 0
            ),
            finding_count=(
                len(analysis_result.get("findings", [])) if analysis_result else 0
            ),
            recommendation_count=(
                len(analysis_result.get("recommendations", []))
                if analysis_result else 0
            ),
        )
        session.add(record)
        session.commit()
        logger.audit("Contract saved", contract_id=record.id, name=name)
        return record.id


def get_contract(contract_id: str) -> dict[str, Any] | None:
    """Retrieve a contract record by ID."""
    if not _db_available:
        return None
    with get_session() as session:
        record = session.get(ContractRecord, contract_id)
        if record is None:
            return None
        return {
            "id": record.id,
            "name": record.name,
            "contract_text": record.contract_text,
            "analysis": record.analysis_json,
            "status": record.status,
            "error": record.error,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
            "total_duration_ms": record.total_duration_ms,
            "clause_count": record.clause_count,
            "finding_count": record.finding_count,
            "recommendation_count": record.recommendation_count,
        }


def list_contracts(
    limit: int = 50, offset: int = 0, status: str | None = None
) -> list[dict[str, Any]]:
    """List contracts with optional status filter."""
    if not _db_available:
        return []
    with get_session() as session:
        query = session.query(ContractRecord).order_by(
            ContractRecord.created_at.desc()
        )
        if status:
            query = query.where(ContractRecord.status == status)
        records = query.offset(offset).limit(limit).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "total_duration_ms": r.total_duration_ms,
                "clause_count": r.clause_count,
                "finding_count": r.finding_count,
                "recommendation_count": r.recommendation_count,
                "summary": r.analysis_json.get("summary", {}),
            }
            for r in records
        ]


def update_contract_status(
    contract_id: str,
    status: str,
    error: str | None = None,
    analysis_result: dict[str, Any] | None = None,
) -> bool:
    """Update a contract's status and optionally its analysis."""
    if not _db_available:
        return False
    with get_session() as session:
        record = session.get(ContractRecord, contract_id)
        if record is None:
            return False
        record.status = status
        if error:
            record.error = error
        if analysis_result:
            record.analysis_json = analysis_result
        session.commit()
        return True
