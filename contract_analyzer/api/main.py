"""FastAPI application for Contract Regulatory Compliance Scanner.

Scans contracts against 17 regulatory standards (GDPR, HIPAA, PCI DSS,
SOC 2, NIST CSF, etc.) using FAISS hybrid vector search with evidence-backed
findings and hallucination detection.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contract_analyzer.api.routes import router
from contract_analyzer.logging_setup import AuditLogger, setup_logging
from contract_analyzer.persistence.database import init_db

setup_logging()
logger = AuditLogger(__name__, "api")

app = FastAPI(
    title="Contract Regulatory Compliance Scanner",
    description="Scan contracts against 17 regulatory standards with FAISS hybrid retrieval, ReAct agent analysis, and hallucination detection.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    logger.info("Starting Contract Compliance Analyzer API server")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database not available, running without persistence: {e}")


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "service": "Contract Regulatory Compliance Scanner", "version": "2.0.0"}
