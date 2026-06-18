"""API routes for contract submission, analysis retrieval, and listing.

Supports both synchronous (blocking) and asynchronous (job-based) submission.
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from contract_analyzer.config import config
from contract_analyzer.document_parser import ExtractionError, extract_text
from contract_analyzer.logging_setup import AuditLogger
from contract_analyzer.orchestrator.queue import job_store
from contract_analyzer.orchestrator.worker import worker
from contract_analyzer.orchestrator.workflow import orchestrator
from contract_analyzer.persistence.database import (
    get_contract,
    list_contracts,
    save_contract,
    update_contract_status,
)

router = APIRouter()
logger = AuditLogger(__name__, "api_routes")


class ContractSubmitRequest(BaseModel):
    name: str = Field(default="", description="Contract name or identifier")
    text: str = Field(..., min_length=10, description="Full contract text")
    async_mode: bool = Field(default=False, description="Submit as background job")


class ContractSubmitResponse(BaseModel):
    analysis_id: str
    status: str
    clause_count: int
    finding_count: int
    recommendation_count: int
    total_duration_ms: float
    summary: dict[str, Any]
    clauses: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    jurisdiction_analysis: dict[str, Any] = Field(default_factory=dict)
    standards_applicability: list[dict[str, Any]] = Field(default_factory=list)
    audit_trail: list[dict[str, Any]] = Field(default_factory=list)
    verification_report: dict[str, Any] | None = None
    escalation_tickets: list[dict[str, Any]] = Field(default_factory=list)
    human_review_required: bool = False


class JobSubmitResponse(BaseModel):
    job_id: str
    status: str
    contract_name: str


class JobStatusResponse(BaseModel):
    job_id: str
    contract_name: str
    status: str
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    result: dict[str, Any] | None = None


class ContractListItem(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    total_duration_ms: float
    clause_count: int
    finding_count: int
    recommendation_count: int
    summary: dict[str, Any] | None = None


async def _run_analysis(contract_text: str, contract_name: str) -> ContractSubmitResponse:
    """Core analysis logic — shared by JSON and file upload paths."""
    analysis = await orchestrator.analyze(
        contract_text=contract_text,
        contract_name=contract_name,
    )

    analysis_dict = analysis.model_dump()
    try:
        save_contract(
            name=contract_name,
            contract_text=contract_text,
            analysis_result=analysis_dict,
            status="completed",
            duration_ms=analysis.total_duration_ms,
        )
    except Exception as e:
        logger.warning(f"Failed to persist analysis: {e}")

    low_confidence = [f for f in analysis.findings if f.confidence < 0.6]
    if low_confidence:
        logger.warning(
            "Analysis contains low-confidence findings",
            count=len(low_confidence),
        )

    return ContractSubmitResponse(
        analysis_id=analysis.analysis_id,
        status="completed",
        clause_count=len(analysis.clauses),
        finding_count=len(analysis.findings),
        recommendation_count=len(analysis.recommendations),
        total_duration_ms=analysis.total_duration_ms,
        summary=analysis.summary,
        clauses=[c.model_dump() for c in analysis.clauses],
        findings=[f.model_dump() for f in analysis.findings],
        recommendations=[r.model_dump() for r in analysis.recommendations],
        jurisdiction_analysis=analysis.jurisdiction_analysis,
        standards_applicability=analysis.standards_applicability,
        audit_trail=analysis.audit_trail,
        verification_report=(
            analysis.verification_report.model_dump()
            if analysis.verification_report else None
        ),
        escalation_tickets=[
            t.model_dump() for t in analysis.escalation_tickets
        ],
        human_review_required=bool(analysis.escalation_tickets),
    )


@router.post("/analyze", response_model=ContractSubmitResponse)
async def analyze_contract(request: Request):
    """Submit a contract for synchronous analysis.

    Accepts two formats:
      - JSON body: {"name": "...", "text": "...", "async_mode": false}
      - Multipart form: file=<upload> + name=<optional>

    The orchestrator will:
    1. Send the contract to the Contract Understanding Agent (A2A)
    2. Classify content and route to specialist Risk Agent
    3. Evaluate risk with ReAct-based agentic retrieval
    4. Verify findings against retrieved evidence
    5. Send findings to the Decision & Recommendation Agent (A2A)
    6. Return the complete analysis

    For async processing, use POST /analyze/async
    """
    content_type = request.headers.get("content-type", "")

    # --- Multipart file upload ---
    if "multipart/form-data" in content_type:
        form = await request.form()
        upload: UploadFile | None = form.get("file")
        name: str = form.get("name", "") or ""
        text: str = form.get("text", "") or ""

        if upload is not None and upload.filename:
            logger.info("Analysis requested via file upload", filename=upload.filename)
            try:
                file_bytes = await upload.read()
                contract_text = extract_text(
                    file_bytes,
                    upload.filename,
                    max_size_mb=config.max_upload_size_mb,
                )
            except ExtractionError as e:
                raise HTTPException(status_code=400, detail=str(e))
            contract_name = name or upload.filename
        elif text:
            logger.info("Analysis requested via multipart text", name=name)
            contract_text = text
            contract_name = name
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide a file upload or text content.",
            )
    else:
        # --- JSON body ---
        body = await request.json()
        try:
            req = ContractSubmitRequest.model_validate(body)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

        # If async mode requested, redirect to async endpoint
        if req.async_mode:
            return await _submit_async(req.text, req.name)

        logger.info("Analysis requested", name=req.name)
        contract_text = req.text
        contract_name = req.name

    try:
        return await _run_analysis(contract_text, contract_name)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.post("/analyze/async", response_model=JobSubmitResponse)
async def submit_async_analysis(request: Request):
    """Submit a contract for asynchronous (background) analysis.

    Returns a job_id immediately. Poll /jobs/{job_id} for status and results.

    Accepts:
      - JSON body: {"name": "...", "text": "..."}
      - Multipart form: file=<upload> + name=<optional>
    """
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        upload: UploadFile | None = form.get("file")
        name: str = form.get("name", "") or ""
        text: str = form.get("text", "") or ""

        if upload is not None and upload.filename:
            try:
                file_bytes = await upload.read()
                contract_text = extract_text(
                    file_bytes,
                    upload.filename,
                    max_size_mb=config.max_upload_size_mb,
                )
            except ExtractionError as e:
                raise HTTPException(status_code=400, detail=str(e))
            contract_name = name or upload.filename
        elif text:
            contract_text = text
            contract_name = name
        else:
            raise HTTPException(status_code=400, detail="Provide a file or text content.")
    else:
        body = await request.json()
        try:
            req = ContractSubmitRequest.model_validate(body)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
        contract_text = req.text
        contract_name = req.name

    return await _submit_async(contract_text, contract_name)


async def _submit_async(contract_text: str, contract_name: str) -> JobSubmitResponse:
    """Create an async job and return immediately."""
    import uuid

    job_id = str(uuid.uuid4())
    await job_store.create(
        job_id=job_id,
        contract_name=contract_name,
    )

    # Store contract text in job for worker pickup
    job = await job_store.get(job_id)
    if job:
        job.result = {"contract_text": contract_text}

    # Start worker if not already running
    await worker.start()

    # Process in background
    import asyncio
    asyncio.create_task(_process_async_job(job_id))

    logger.info("Async analysis job submitted", job_id=job_id, name=contract_name)

    return JobSubmitResponse(
        job_id=job_id,
        status="pending",
        contract_name=contract_name,
    )


async def _process_async_job(job_id: str) -> None:
    """Process an async job in the background."""
    job = await job_store.get(job_id)
    if not job:
        return

    await job_store.update_status(job_id, "running")

    try:
        contract_text = (job.result or {}).get("contract_text", "")
        contract_name = job.contract_name

        analysis = await orchestrator.analyze(
            contract_text=contract_text,
            contract_name=contract_name,
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
            "human_review_required": bool(analysis.escalation_tickets),
        }

        await job_store.set_result(job_id, result)

    except Exception as e:
        logger.error(f"Async job failed: {e}", job_id=job_id)
        await job_store.set_error(job_id, str(e))


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status and result of an async analysis job."""
    job = await job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        contract_name=job.contract_name,
        status=job.status,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error,
        result=job.result,
    )


@router.get("/jobs")
async def list_jobs(limit: int = 50, offset: int = 0, status: str | None = None):
    """List all async analysis jobs."""
    return await job_store.list_jobs(limit=limit, offset=offset, status=status)


@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve a previously completed analysis by ID."""
    record = get_contract(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return record


@router.get("/analyses")
async def list_analyses(limit: int = 50, offset: int = 0, status: str | None = None):
    """List all contract analyses."""
    return list_contracts(limit=limit, offset=offset, status=status)
