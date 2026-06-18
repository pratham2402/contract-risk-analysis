"""FastAPI application for Contract Compliance Analyzer.

Serves the REST API and the enterprise operations console.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contract_analyzer.api.routes import router
from contract_analyzer.logging_setup import AuditLogger, setup_logging
from contract_analyzer.persistence.database import init_db

setup_logging()
logger = AuditLogger(__name__, "api")

app = FastAPI(
    title="Contract Compliance Analyzer",
    description="Multi-Agent Contract Risk and Obligation Intelligence System",
    version="1.0.0",
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
    return {"status": "healthy", "service": "Contract Compliance Analyzer", "version": "1.0.0"}
