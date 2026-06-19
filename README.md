# Contract Regulatory Compliance Scanner

**Scan contracts against 17 regulatory standards with evidence-backed findings.**

A production-grade compliance scanning system that analyzes contract clauses against GDPR, HIPAA, PCI DSS, SOC 2, NIST CSF, SOX, and 11 other standards using FAISS hybrid vector search. The LLM retrieves relevant standards dynamically and produces cited, evidence-backed findings — not hallucinated advice.

This is a **regulatory compliance scanner**, not a general contract risk analyzer or chatbot. Every finding is grounded in a specific standard article retrieved from the curated standards database.

---

## Architecture

```
FastAPI API (port 8000)
  └─ LangGraph StateGraph Pipeline (7 nodes, 6 stages)
       ├─ parse_contract ── LLM extracts clauses + classifies content
       ├─ evaluate_risk  ── ReAct agent (4 tools, dynamic FAISS+BM25 retrieval)
       ├─ verify_findings ── LLM cross-references citations vs retrieved evidence
       ├─ generate_decisions ── LLM produces prioritized recommendations
       ├─ human_review ── triggered when verification flags exceed threshold
       ├─ finalize ── assemble output
       └─ handle_error ── graceful failure with partial results
                    │
            FAISS + BM25 Hybrid DB (100 curated entries, 17 standards)
```

### What Each Stage Does

| Stage | Type | Description |
|-------|------|-------------|
| **Parse Contract** | Single LLM call | Extracts clauses, parties, governing law, contract type, data involved. Classifies content to route to privacy/financial/generalist specialist. |
| **Evaluate Risk** | **ReAct Agent** (4 tools) | The only genuinely agentic component. LLM runs a Thought→Action→Observation loop: decides what standards to retrieve, when evidence is sufficient, and whether to escalate. Tools: `retrieve_standards`, `compare_jurisdictions`, `escalate_to_human`, `request_more_context`. |
| **Verify Findings** | Single LLM call | Cross-references every cited standard article against retrieved evidence. Flags hallucinated citations, unsupported references, disconnected reasoning, and risk-level mismatches. |
| **Generate Decisions** | Single LLM call | Converts findings into actionable recommendations with owner (legal/finance/security/compliance/executive), priority (1-5), and decision (approve/escalate/block). |

Everything runs **in-process** — no microservices, no inter-process communication. Single `python scripts/run_agents.py` starts everything.

---

## Pipeline Stages (User-Visible)

1. **Parsing Contract** — Extracting clauses, parties, and governing law
2. **Classifying Content** — Keyword-based routing to specialist (privacy/financial/generalist)
3. **Evaluating Risk** — ReAct agent loop with FAISS + BM25 retrieval across 17 standards
4. **Verifying Citations** — Cross-referencing citations against retrieved evidence
5. **Generating Decisions** — Prioritized recommendations with owner assignments
6. **Finalizing** — Assembling complete analysis output

---

## Standards Coverage

100 curated entries across 17 standards, each with article-level granularity:

**Data Protection & Privacy:**
- **GDPR**: Arts. 5, 6, 12-23, 25, 28, 32, 33-34, 35, 37-39, 44-49
- **DPDPA 2023** (India): S.3-4, 6-8, 10-13, 16, 33
- **CCPA/CPRA** (California): 1798.100-1798.125

**Industry-Specific:**
- **HIPAA**: 45 CFR 164.306-504 — Privacy Rule, Security Rule, Breach Notification
- **PCI DSS v4.0.1**: Req. 1-12 — network security, cardholder data, access control
- **FERPA**: 20 USC 1232g, 34 CFR 99 — student education records
- **GLBA**: Regulation P, 16 CFR Part 314 — financial privacy, Safeguards Rule
- **SOX**: S.302, 404, 802, 906 — ICFR, ITGCs, record retention

**Security Frameworks:**
- **ISO 27001**: Clauses 4-9, Annex A.5-A.18
- **SOC 2**: CC3-CC4, CC6-CC9, A1, PI1, C1, P1-P8
- **NIST CSF 2.0**: GV, ID, PR, DE, RS, RC (106 subcategories)
- **FedRAMP**: NIST SP 800-53 Rev. 5 — AC, AU, CM, IA, SC, CP, IR, SR families

**General Contract Law:**
- **US_RESTATEMENT** (Second) of Contracts: formation, consideration, breach, damages, defenses, remedies
- **US_UCC** Article 2: sales, formation, warranties, performance, remedies
- **US_DGCL**: incorporation, board authority, indemnification, fiduciary duties
- **Indian Contract Act, 1872**: S.2, 10-11, 14-22, 23-30, 37, 39, 55, 73-74, 124-128, 182-226
- **IT Act, 2000** (India): S.3-5, 10A, 43A, 65-66F, 72-72A, 79

### Applicability Gating

Standards are NOT applied blindly. The ReAct agent uses a 3-layer trigger test:

1. **Subject-matter test**: Does the contract involve the regulated activity?
2. **Jurisdictional nexus**: Is there a territorial hook?
3. **Materiality threshold**: Is the regulated thing actually present?

A standard applies ONLY if all three layers pass.

---

## Retrieval-Based Grounding

Every risk finding is grounded in retrieved evidence:

1. 100 curated standards entries stored in FAISS (dense) + BM25 (sparse) indexes
2. During analysis, the ReAct agent dynamically queries for relevant standards
3. Top-k results are fused using Reciprocal Rank Fusion (70% vector, 30% BM25)
4. The LLM must explicitly cite which standard article supports each finding
5. Retrieved evidence is extracted from tool calls and passed to verification
6. Verification cross-references every citation against evidence — flagging unsupported claims
7. Low-confidence findings (<60%) escalate to human review

---

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, for persistence)
- LLM API key (DeepSeek, OpenAI, or compatible)

### Installation

```bash
git clone <repo-url>
cd Compliance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### Initialize Standards Database

```bash
python scripts/setup_standards_db.py
```

### Start Server

```bash
python scripts/run_agents.py
```

Single process — all components run in-process on port 8000.

### Run Demo

```bash
python scripts/demo.py
python scripts/demo.py --contract data/sample_contracts/risky_saas.txt
```

---

## API

### POST /api/v1/analyze
Synchronous contract analysis. Returns complete results.

### POST /api/v1/analyze/async
Submit contract for background processing. Returns `job_id` immediately. Poll `GET /jobs/{job_id}` for results.

### GET /api/v1/jobs/{job_id}/stream
SSE endpoint for real-time progress streaming. Pushes stage events as the pipeline progresses.

### GET /api/v1/jobs/{job_id}
Get job status and results.

### GET /api/v1/analyses
List completed analyses.

---

## Project Structure

```
contract_analyzer/
  agents/                     # Pipeline components (all in-process)
    contract_understanding.py # Clause extraction (single LLM call)
    risk_compliance.py        # ReAct agent with tool calling
    react_graph.py            # ReAct StateGraph builder + output parsing
    tools.py                  # 4 tools: retrieve_standards, compare_jurisdictions, etc.
    verification.py           # Evidence cross-reference verification
    decision_recommendation.py # Findings → recommendations converter
  api/
    main.py                   # FastAPI application
    routes.py                 # API endpoints + async job processing
  models/
    output.py                 # Pydantic models (Finding, Recommendation, etc.)
    state.py                  # LangGraph state definition
  orchestrator/
    workflow.py               # LangGraph StateGraph pipeline
    queue.py                  # In-memory job store with SSE event queues
  retrieval/
    standards_data.py         # 100 curated standards entries
    standards_index.py        # FAISS index management
    hybrid_retriever.py       # FAISS + BM25 with RRF fusion
    bm25_index.py             # BM25 sparse retrieval
    metadata_filter.py        # Jurisdiction/category/authority filtering
  persistence/
    database.py               # PostgreSQL persistence (optional)
  document_parser/
    extractor.py              # PDF and DOCX text extraction
  config.py                   # Environment-based configuration
  logging_setup.py            # Structured JSON audit logging
scripts/
  setup_standards_db.py       # Build FAISS index
  run_agents.py               # Single-process server launcher
  demo.py                     # End-to-end pipeline demo
data/
  sample_contracts/           # Sample NDA and SaaS contracts
tests/                        # pytest suite (161 tests)
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph (StateGraph) |
| LLM | Configurable (DeepSeek Chat / GPT-4o / compatible) |
| Agent Pattern | ReAct loop with tool calling |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Search | FAISS |
| Keyword Search | BM25 |
| Fusion | Reciprocal Rank Fusion (RRF) |
| API Server | FastAPI + Uvicorn |
| Streaming | Server-Sent Events (SSE) via asyncio.Queue |
| Persistence | PostgreSQL + SQLAlchemy (optional) |
| Logging | Structured JSON (stdout) |

---

## Edge Cases

| Case | Handling |
|------|----------|
| Missing clauses | Flagged as findings with recommendation to add |
| Incomplete contracts | Partial analysis produced; warnings in audit trail |
| No standards matches | Agent notes limitation; produces findings from contract law baseline |
| Low-confidence outputs | Escalated to human review |
| Agent failure | Error node preserves partial results |
| Hallucination detection | Verification cross-references every citation against evidence |
