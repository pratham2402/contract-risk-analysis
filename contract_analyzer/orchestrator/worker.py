"""Background worker for async contract analysis jobs.

Polls the job store for pending jobs and processes them through the
orchestrator, updating job status and results as it goes.
"""

import asyncio
from typing import Any

from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.orchestrator.queue import Job, job_store
from contract_analyzer.orchestrator.workflow import orchestrator

logger = AuditLogger(__name__, "worker")


class AnalysisWorker:
    """Background worker that processes analysis jobs from the queue."""

    def __init__(self, poll_interval: float = 1.0) -> None:
        self.poll_interval = poll_interval
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the worker loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Analysis worker started")

    async def stop(self) -> None:
        """Stop the worker loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Analysis worker stopped")

    async def _loop(self) -> None:
        """Main worker loop — poll for pending jobs."""
        while self._running:
            try:
                # Find pending jobs
                pending = await job_store.list_jobs(status="pending", limit=10)
                for job_data in pending:
                    job = await job_store.get(job_data["job_id"])
                    if job and job.status == "pending":
                        asyncio.create_task(self._process_job(job))
            except Exception as e:
                logger.error(f"Worker loop error: {e}")

            await asyncio.sleep(self.poll_interval)

    async def _process_job(self, job: Job) -> None:
        """Process a single analysis job."""
        logger.info("Processing job", job_id=job.job_id)

        await job_store.update_status(job.job_id, "running")

        try:
            analysis = await orchestrator.analyze(
                contract_text=job.result.get("contract_text", "") if job.result else "",
                contract_name=job.contract_name,
            )

            result = {
                "analysis_id": analysis.analysis_id,
                "status": "completed",
                "contract_name": analysis.contract_name,
                "clause_count": len(analysis.clauses),
                "finding_count": len(analysis.findings),
                "recommendation_count": len(analysis.recommendations),
                "total_duration_ms": analysis.total_duration_ms,
                "summary": analysis.summary,
                "clauses": [c.model_dump() for c in analysis.clauses],
                "findings": [f.model_dump() for f in analysis.findings],
                "recommendations": [r.model_dump() for r in analysis.recommendations],
                "jurisdiction_analysis": analysis.jurisdiction_analysis,
                "standards_applicability": analysis.standards_applicability,
                "audit_trail": analysis.audit_trail,
                "verification_report": (
                    analysis.verification_report.model_dump()
                    if analysis.verification_report else None
                ),
                "escalation_tickets": [
                    t.model_dump() for t in analysis.escalation_tickets
                ],
            }

            await job_store.set_result(job.job_id, result)
            logger.info("Job completed successfully", job_id=job.job_id)

        except Exception as e:
            logger.error(f"Job failed: {e}", job_id=job.job_id)
            await job_store.set_error(job.job_id, str(e))

    async def submit_and_wait(
        self,
        contract_text: str,
        contract_name: str = "",
        timeout: float = 300.0,
    ) -> dict[str, Any]:
        """Submit a job and wait for completion (convenience method).

        Args:
            contract_text: Full contract text.
            contract_name: Human-readable identifier.
            timeout: Maximum wait time in seconds.

        Returns:
            Completed job result dict.
        """
        import uuid

        job_id = str(uuid.uuid4())
        await job_store.create(
            job_id=job_id,
            contract_name=contract_name,
        )

        # Store the contract text in job result for the worker to pick up
        job = await job_store.get(job_id)
        if job:
            job.result = {"contract_text": contract_text}

        await self._process_job(job)

        # Poll for completion
        start = asyncio.get_event_loop().time()
        while True:
            job = await job_store.get(job_id)
            if job and job.status in ("completed", "failed", "needs_review"):
                return job.result or {"status": job.status, "error": job.error}

            if asyncio.get_event_loop().time() - start > timeout:
                return {"status": "timeout", "error": f"Job timed out after {timeout}s"}

            await asyncio.sleep(0.5)


# Global worker instance
worker = AnalysisWorker()
