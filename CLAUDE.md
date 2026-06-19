# Contract Compliance Analyzer

LangGraph orchestration pipeline for contract risk and compliance analysis. Uses a ReAct agent with dynamic tool calling for risk evaluation across 17 regulatory standards (GDPR, HIPAA, PCI DSS, SOC 2, NIST CSF, etc.) via FAISS hybrid vector search. All components run in-process — no separate microservices.

## Token efficiency

- **Do NOT read `standards_data.py` in full** unless adding new standards — it's 1718 lines of curated regulatory entries. Use grep to find specific standards.
- **Do NOT read generated data files** — `.faiss`, `.npy`, `.pkl` files in `data/` are binary and unreadable.
- **Do NOT re-read files already read earlier in the session** — the harness tracks state.
- **Use the Explore agent** for broad searches across many files rather than reading each one.
- **Consult this CLAUDE.md first** for architecture, source layout, key patterns, and commands before searching the codebase.
- **Avoid reading `node_modules/` or `venv/`** — they're excluded via `.claudeignore`.
- **Prefer targeted grep over full file reads** when answering questions about specific symbols, patterns, or references.

## Commands

```bash
# Virtual environment at venv/ (not .venv)
source venv/bin/activate
pip install -r requirements.txt

# Setup the FAISS standards database (required first time)
./venv/bin/python scripts/setup_standards_db.py

# Run API server (single process, all agents run in-process)
./venv/bin/python scripts/run_agents.py

# Demo
./venv/bin/python scripts/demo.py
./venv/bin/python scripts/demo.py --contract data/sample_contracts/risky_saas.txt

# Health check
curl -s http://127.0.0.1:8000/api/v1/health

# Quick test async analysis
curl -s -X POST http://127.0.0.1:8000/api/v1/analyze/async \
  -H "Content-Type: application/json" \
  -d '{"name":"test","text":"This is a test contract."}'

# Tests
./venv/bin/python -m pytest tests/ -v
```

## Environment

Copy `.env.example` to `.env` and set:
- `LLM_MODEL` (default: `gpt-4o`; currently using `deepseek-chat` for cost)
- `OPENAI_API_KEY` (required)
- `OPENAI_BASE_URL` (optional — set to DeepSeek endpoint for non-OpenAI providers)
- `DATABASE_URL` (postgresql+asyncpg, optional — system runs without it)

## Architecture

```
FastAPI API (port 8000)
  └─ LangGraph StateGraph Pipeline
       ├─ parse_contract ── LLM extracts clauses + classifies content
       ├─ evaluate_risk  ── ReAct agent (5 tools, dynamic retrieval)
       ├─ verify_findings ── LLM cross-references evidence vs citations
       ├─ generate_decisions ── LLM produces prioritized recommendations
       └─ finalize ── assemble output
                    │
            FAISS + BM25 Hybrid DB (17 standards)
```

- **6-stage LangGraph pipeline** with conditional routing and verification gating
- **One genuine agent**: Risk evaluation uses a ReAct reasoning loop (Thought→Action→Observation) with 5 tools (retrieve_standards, retrieve_clause, compare_jurisdictions, escalate_to_human, request_more_context). The LLM decides when to retrieve, what to query, and when evidence is sufficient.
- **Other stages** are single-pass LLM calls with structured output
- **3 specialist profiles** for risk agent: generalist, privacy, financial (keyword-routed)
- **FAISS hybrid retrieval**: vector search (70%) + BM25 (30%) over 17 standards via Reciprocal Rank Fusion
- **Verification**: cross-references findings against retrieved evidence, flags hallucinated/unsupported citations at threshold 0.6
- **SSE streaming**: real-time stage progress pushed via per-job asyncio.Queue

## Source layout

| Module | Purpose |
|---|---|
| `contract_analyzer/api/main.py` | FastAPI app (port 8000) |
| `contract_analyzer/api/routes.py` | REST endpoints + async job processing |
| `contract_analyzer/orchestrator/workflow.py` | LangGraph StateGraph pipeline |
| `contract_analyzer/orchestrator/queue.py` | In-memory job store with SSE event queues |
| `contract_analyzer/agents/contract_understanding.py` | Clause extraction (single LLM call) |
| `contract_analyzer/agents/risk_compliance.py` | ReAct agent with tool calling |
| `contract_analyzer/agents/react_graph.py` | ReAct StateGraph builder + output parsing |
| `contract_analyzer/agents/tools.py` | 5 tools for the ReAct agent |
| `contract_analyzer/agents/verification.py` | Evidence-cross-reference verification |
| `contract_analyzer/agents/decision_recommendation.py` | Findings → recommendations converter |
| `contract_analyzer/config.py` | `Config` dataclass from env vars |
| `contract_analyzer/retrieval/` | FAISS + BM25 hybrid retriever |
| `contract_analyzer/models/` | Pydantic schemas (Finding, Recommendation, etc.) |
| `contract_analyzer/document_parser/` | PDF and DOCX parsing |
| `contract_analyzer/persistence/database.py` | SQLAlchemy async PostgreSQL |
| `scripts/run_agents.py` | Single-process API server launcher |
| `scripts/demo.py` | End-to-end pipeline demo |
| `scripts/setup_standards_db.py` | FAISS index builder |
| `tests/` | pytest suite |

## Key patterns

- **venv at `venv/`** (not `.venv` like other projects)
- **Everything runs in-process** — no microservices, no A2A protocol, no multi-process. Simpler deployment, lower memory.
- **Only the risk agent is agentic** — it runs a ReAct loop with tool calling. Other stages are single-pass LLM calls with structured output prompts.
- **Hybrid retrieval**: dense (sentence-transformers all-MiniLM-L6-v2) + sparse (BM25) with configurable weights
- **17 standards**: GDPR, DPDPA, CCPA, HIPAA, PCI DSS, ISO 27001, SOC 2, NIST CSF, SOX, FedRAMP, FERPA, GLBA, ICA, IT Act, Restatement, UCC Art. 2, DGCL
- **Risk agent confidence threshold**: 0.6 (configurable via `RISK_AGENT_CONFIDENCE_THRESHOLD`)
- **Max ReAct iterations**: 10 (configurable via `RISK_AGENT_MAX_ITERATIONS`)
- **Evidence collection**: Retrieved standards are extracted from ReAct tool messages and passed to verification to prevent hallucination false-positives
