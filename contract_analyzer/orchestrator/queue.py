"""Async job queue for contract analysis submissions.

Provides in-memory job tracking with optional Redis backend. Jobs are
submitted via the orchestrator's submit() method and processed
asynchronously. Status and results can be polled by job ID.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from contract_analyzer.logging_setup import AuditLogger

logger = AuditLogger(__name__, "job_queue")


@dataclass
class Job:
    """Tracks a single analysis job through its lifecycle."""

    job_id: str
    contract_name: str
    status: str = "pending"  # pending, running, completed, failed, needs_review
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    status_callback_url: str | None = None


class JobStore:
    """Thread-safe in-memory job store with optional Redis backend."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = asyncio.Lock()

    async def create(self, job_id: str, contract_name: str,
                     status_callback_url: str | None = None) -> Job:
        job = Job(
            job_id=job_id,
            contract_name=contract_name,
            status_callback_url=status_callback_url,
        )
        async with self._lock:
            self._jobs[job_id] = job
        logger.info("Job created", job_id=job_id, name=contract_name)
        return job

    async def get(self, job_id: str) -> Job | None:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_status(self, job_id: str, status: str,
                            error: str | None = None) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.status = status
                if status == "running" and job.started_at is None:
                    job.started_at = datetime.now(UTC).isoformat()
                if status in ("completed", "failed", "needs_review"):
                    job.completed_at = datetime.now(UTC).isoformat()
                if error:
                    job.error = error

    async def set_result(self, job_id: str, result: dict[str, Any]) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.result = result
                job.status = "completed"
                job.completed_at = datetime.now(UTC).isoformat()

    async def set_error(self, job_id: str, error: str) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.error = error
                job.status = "failed"
                job.completed_at = datetime.now(UTC).isoformat()

    async def list_jobs(self, limit: int = 50, offset: int = 0,
                        status: str | None = None) -> list[dict]:
        async with self._lock:
            jobs = list(self._jobs.values())
            # Sort by created_at descending
            jobs.sort(key=lambda j: j.created_at, reverse=True)
            if status:
                jobs = [j for j in jobs if j.status == status]
            return [
                {
                    "job_id": j.job_id,
                    "contract_name": j.contract_name,
                    "status": j.status,
                    "created_at": j.created_at,
                    "started_at": j.started_at,
                    "completed_at": j.completed_at,
                    "error": j.error,
                }
                for j in jobs[offset:offset + limit]
            ]

    async def delete(self, job_id: str) -> bool:
        async with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]
                return True
            return False


# Global job store instance
job_store = JobStore()
