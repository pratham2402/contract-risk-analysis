# Contract Compliance Analyzer

Multi-agent contract risk and obligation intelligence system. Analyzes contracts using 4 agents (orchestrator, contract understanding, risk and compliance, decision and recommendation) communicating via Google A2A protocol. Evaluates against 17 standards (GDPR, HIPAA, PCI DSS, SOC 2, NIST CSF, etc.) using FAISS hybrid vector search.

## Commands

```bash
# Virtual environment at venv/ (not .venv)
source venv/bin/activate
pip install -r requirements.txt

# Setup the FAISS standards database (required first time)
./venv/bin/python scripts/setup_standards_db.py

# Run all services (API + 3 risk agents as separate A2A microservices)
./venv/bin/python scripts/run_agents.py

# Run only the main API server (port 8000)
./venv/bin/python scripts/run_agents.py --api-only

# Run only the risk agents (ports 8005, 8006, 8007)
./venv/bin/python scripts/run_agents.py --agents-only

# Run with specific agent profile
./venv/bin/python scripts/run_agents.py --profile core      # generalist risk only
./venv/bin/python scripts/run_agents.py --profile full       # all 3 risk agents

# Demo
./venv/bin/python scripts/demo.py
./venv/bin/python scripts/demo.py --contract data/sample_contracts/risky_saas.txt
./venv/bin/python scripts/demo.py --server                  # also start agent servers first

# Frontend
cd contract-analyzer-frontend
npm install
npm run dev       # Next.js dev server
npm run build     # production build
npm run lint      # ESLint via Next.js

# Health check
curl -s http://127.0.0.1:8000/api/v1/health

# Quick test analyze
curl -s -X POST http://127.0.0.1:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"name":"test","text":"This is a test contract."}'

# Tests
./venv/bin/python -m pytest tests/ -v
```

## Environment

Copy `.env.example` to `.env` and set:
- `LLM_PROVIDER` (default: `openai`)
- `LLM_MODEL` (default: `gpt-4o`)
- `OPENAI_API_KEY` (required)
- `DATABASE_URL` (postgresql+asyncpg, optional -- system runs without it)

## Architecture

```
FastAPI API (port 8000)
  └─ LangGraph Orchestrator (StateGraph)
       ├─ A2A ─ Contract Understanding Agent
       ├─ A2A ─ Risk and Compliance Agent (port 8005)
       │         ├─ Privacy Specialist (port 8006)
       │         └─ Financial Specialist (port 8007)
       └─ A2A ─ Decision and Recommendation Agent
                      │
              FAISS Vector DB (17 standards)
```

- **4 agents** communicate via Google A2A protocol (a2a-sdk)
- **Orchestrator** controls flow via LangGraph StateGraph, manages state, coordinates all agents
- **Risk and Compliance Agent** is the only one that runs as separate A2A microservices (3 processes for generalist, privacy, financial) -- it needs the ReAct reasoning loop with dynamic tool calling
- **Contract Understanding** and **Decision agents** run in-process as single-pass LLM calls
- **FAISS hybrid retrieval**: vector search (70 percent) + BM25 (30 percent) over 17 standards
- **Verification**: in-process, cross-references findings against evidence, flags at confidence threshold 0.6
- **Frontend**: Next.js 16 + React 19 + shadcn/ui + Tailwind CSS 4

## Source layout

| Module | Purpose |
|---|---|
| `contract_analyzer/api/main.py` | FastAPI app (port 8000) |
| `contract_analyzer/api/routes.py` | REST endpoints |
| `contract_analyzer/orchestrator/` | LangGraph StateGraph workflow |
| `contract_analyzer/agents/a2a_servers.py` | A2A agent server definitions |
| `contract_analyzer/config.py` | `Config` dataclass from env vars |
| `contract_analyzer/retrieval/` | FAISS hybrid retriever |
| `contract_analyzer/models/` | Pydantic schemas |
| `contract_analyzer/document_parser/` | PDF and DOCX parsing |
| `contract_analyzer/persistence/database.py` | SQLAlchemy async PostgreSQL |
| `scripts/run_agents.py` | Multi-process agent launcher |
| `scripts/demo.py` | End-to-end pipeline demo |
| `scripts/setup_standards_db.py` | FAISS index builder |
| `contract-analyzer-frontend/` | Next.js frontend |
| `tests/` | pytest suite |

## Key patterns

- **venv at `venv/`** (not `.venv` like other projects)
- **A2A protocol**: inter-agent communication via a2a-sdk, each agent is an A2A server
- **Multi-process**: risk agents run as separate Python processes via multiprocessing
- **Hybrid retrieval**: dense (sentence-transformers all-MiniLM-L6-v2) + sparse (BM25) with configurable weights
- **17 standards**: GDPR, DPDPA, CCPA, HIPAA, PCI DSS, ISO 27001, SOC 2, NIST CSF, SOX, FedRAMP, FERPA, GLBA, ICA, IT Act, Restatement, UCC Art. 2, DGCL
- **Risk agent confidence threshold**: 0.6 (configurable)
- **Frontend**: Next.js App Router, shadcn/ui components, Tailwind v4
