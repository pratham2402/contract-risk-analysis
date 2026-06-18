# Contract Compliance Analyzer

**Multi-Agent Contract Risk and Obligation Intelligence System**

A production-grade enterprise system that analyzes contracts and produces risk assessment, compliance evaluation, obligation extraction, financial exposure insights, and actionable recommendations.

Contract Compliance Analyzer is a decision-support system, not a chatbot.

---

## Architecture

```
                        +---------------------------+
                        |     FastAPI API Server     |
                        |        (port 8000)         |
                        +-------------+-------------+
                                      |
                        +-------------v-------------+
                        |   LangGraph Orchestrator  |
                        |   (StateGraph Workflow)    |
                        +--+--------+--------+-----+
                           |        |        |
                    A2A    |   A2A  |   A2A  |
              +------------+  +-----+  +----+----------+
              |               |            |             |
    +---------v------+  +-----v------+  +--v------------+
    | Contract       |  | Risk &     |  | Decision &    |
    | Understanding  |  | Compliance |  | Recommendation|
    | Agent          |  | Agent      |  | Agent         |
    | (port 8001)    |  | (port 8005)|  | (port 8003)   |
    +----------------+  +-----+------+  +---------------+
                              |
                    +---------v---------+
                    |   FAISS Vector DB  |
                    |  (17 Standards:    |
                    |   GDPR, DPDPA,     |
                    |   CCPA, HIPAA,     |
                    |   PCI DSS, ISO     |
                    |   27001, SOC 2,    |
                    |   NIST CSF, SOX,   |
                    |   FedRAMP, FERPA,  |
                    |   GLBA, ICA, IT    |
                    |   Act, Restatement,|
                    |   UCC Art. 2, DGCL)|
                    +-------------------+
```

### The Four Agents

| Agent | Role | Technology |
|-------|------|------------|
| **Orchestrator** | Controls execution flow, builds DAG, manages state, coordinates all agents | LangGraph StateGraph |
| **Contract Understanding** | Parses contract text, segments into clauses, classifies clause types, outputs structured data | LLM + A2A |
| **Risk & Compliance** | Evaluates contract against 17 standards (US + Indian contract law, global regulatory frameworks), detects risks/violations, uses vector DB retrieval, produces evidence-backed findings | LLM + FAISS + A2A |
| **Decision & Recommendation** | Converts findings into actions: recommended fixes, negotiation suggestions, owner, priority, final decision | LLM + A2A |

### Agent Communication

All inter-agent communication uses the **Google A2A (Agent-to-Agent) Protocol** via the official `a2a-sdk`. Each agent:

- Exposes an A2A-compatible interface with an Agent Card at `/.well-known/agent.json`
- Communicates via JSON-RPC over HTTP (Starlette/Uvicorn)
- Has well-defined skills and capabilities declared in its Agent Card
- Is independently deployable and versioned

No direct function calls between agents. The Orchestrator uses `a2a.client.Client` to send messages to each agent.

### Orchestration Flow

```
1. Orchestrator receives contract text
2. Sends to Contract Understanding Agent (A2A)
3. Receives structured clauses -> sends to Risk & Compliance Agent (A2A)
4. Risk agent queries FAISS vector DB for relevant standards context
5. Receives findings -> sends to Decision & Recommendation Agent (A2A)
6. Final output assembled with full audit trail
```

---

## Why Multi-Agent Design

A single LLM call cannot reliably:

1. **Maintain separation of concerns** -- parsing, risk assessment, and decision-making require different prompts and different levels of rigor
2. **Ground in external standards** -- the risk agent needs dedicated access to a vector database with curated standards summaries, which would pollute a single-agent context
3. **Provide audit trails** -- each agent logs its own calls, duration, and outputs independently
4. **Scale independently** -- the contract parsing agent may need different resources than the risk evaluation agent
5. **Fail gracefully** -- if the decision agent fails, partial results (parsed clauses + findings) are still available

This is not a chatbot use case. It is a pipeline where each stage has distinct inputs, outputs, quality requirements, and failure modes. Multi-agent architecture with A2A protocol provides:

- **Accountability**: each agent's decisions are independently auditable
- **Extensibility**: new standards or agent types can be added without modifying existing agents
- **Resilience**: errors in one stage do not cascade to others
- **Standards grounding**: the risk agent's vector DB retrieval is decoupled from the LLM reasoning

---

## Business Value

- **Reduce contract review time** from days to seconds
- **Eliminate missed obligations** by cross-referencing every clause against applicable standards with jurisdiction-aware gating
- **Standardize risk assessment** across all contracts with consistent, evidence-backed scoring
- **Provide negotiation leverage** with specific, standards-cited recommendations
- **Create audit-ready decision trails** for compliance reviews and regulatory inquiries

---

## Retrieval-Based Standards Grounding

Every risk finding is grounded in real standards, not LLM hallucination:

1. 100 curated summaries of 17 regulatory, industry, and contract law standards are stored in FAISS
2. During analysis, relevant clause text is embedded and matched against the index
3. Top-k matching standards excerpts are injected into the LLM context
4. The LLM must explicitly cite which standard article supports each finding
5. Low-confidence findings (<60%) are flagged for human review

### Standards Coverage

The vector database now contains 100 curated entries across 17 standards:

**Data Protection & Privacy:**
- **GDPR**: Arts. 5, 6, 12-23, 25, 28, 32, 33-34, 35, 37-39, 44-49
- **DPDPA 2023** (India): S.3-4, 6-8, 10-13, 16, 33 - consent, data fiduciary duties, cross-border transfers, penalties
- **CCPA/CPRA** (California): 1798.100-1798.125, Regs. Art. 9-11 - consumer rights, cybersecurity audits, risk assessments, ADMT

**Industry-Specific:**
- **HIPAA**: 45 CFR 164.306-504 - Privacy Rule, Security Rule, Breach Notification, BAA requirements
- **PCI DSS v4.0.1**: Req. 1-12 - network security, account data protection, access control, vulnerability management, TPSP oversight
- **FERPA**: 20 USC 1232g, 34 CFR 99 - student education records, school official exception, directory information
- **GLBA**: Regulation P, 16 CFR Part 314 - financial privacy, Safeguards Rule, breach notification

**Security Frameworks:**
- **ISO 27001**: Clauses 4-9, Annex A.5-A.18 - ISMS, access control, cryptography, supplier management, incident response, secure development
- **SOC 2**: CC3-CC4, CC6-CC9, A1, PI1, C1, P1-P8 - security, availability, processing integrity, confidentiality, privacy
- **NIST CSF 2.0**: GV, ID, PR, DE, RS, RC - govern, identify, protect, detect, respond, recover (106 subcategories)
- **FedRAMP**: NIST SP 800-53 Rev. 5 - AC, AU, CM, IA, SC, CP, IR, SR families across Low/Moderate/High baselines
- **SOX**: S.302, 404, 802, 906 - CEO/CFO certification, ICFR, ITGCs, record retention

**General Contract Law (US Jurisdiction):**
- **US_RESTATEMENT - Restatement (Second) of Contracts**: §§ 17, 24, 36, 50, 61 (formation); §§ 71, 73, 79, 81 (consideration); §§ 344, 346, 347, 349-352, 356 (breach, damages, penalties); §§ 12-16, 20, 151-177, 208 (defenses); §§ 87, 90 (promissory estoppel); §§ 234-243, 345-377 (performance, conditions, remedies)
- **US_UCC - Uniform Commercial Code Article 2**: §§ 2-102, 2-105, 2-204, 2-206 (scope, formation); §§ 2-205, 2-207, 2-209 (firm offers, battle of forms, modification); §§ 2-312-2-316 (warranties and disclaimers); §§ 2-508, 2-601, 2-602, 2-608-2-612 (performance, perfect tender, cure); §§ 2-711-2-717 (buyer remedies); §§ 2-702-2-710 (seller remedies)
- **US_DGCL - Delaware General Corporation Law**: §§ 101-102, 122 (incorporation, corporate powers); § 141 (board authority, fiduciary duties); § 145 (indemnification, D&O insurance); § 102(b)(7), § 144 (director exculpation, safe harbors); §§ 122(13), 122(18) (corporate contracting, veil piercing)

**General Contract Law (Indian Jurisdiction):**
- **Indian Contract Act, 1872**: S.2, 10-11, 14-22, 23-30, 37, 39, 55, 73-74, 124-128, 182-226
- **IT Act, 2000**: S.3-5, 10A, 43A, 65-66F, 72-72A, 79

### Applicability Gating

Standards are NOT applied blindly. The Risk & Compliance Agent uses a 3-layer trigger analysis:

1. **Subject-matter test**: Does the contract involve the regulated activity?
2. **Jurisdictional nexus**: Is there a territorial hook?
3. **Materiality threshold**: Is the regulated thing actually present?

A standard applies ONLY if all three layers pass. General contract law always applies as the baseline, with the applicable body determined by governing law jurisdiction (US_RESTATEMENT + US_UCC + US_DGCL for US-governed contracts; IND_CONTRACT + IT_ACT for Indian-law-governed contracts).

---

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, for persistence)
- OpenAI API key (for LLM)

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

This builds the FAISS index from 100 curated compliance standards summaries across 17 standards. Output: `data/standards_index.faiss`.

### Start Services

```bash
# Start all 4 services (3 agents + API)
python scripts/run_agents.py

# Or start individually:
python scripts/run_agents.py --agents-only   # just the 3 A2A agents
python scripts/run_agents.py --api-only      # just the main API + UI
```

### Run Demo

```bash
# Demo with sample NDA contract
python scripts/demo.py

# Demo with SaaS agreement
python scripts/demo.py --contract data/sample_contracts/risky_saas.txt

# Custom contract
python scripts/demo.py --contract path/to/contract.txt --name "My Contract"
```

### Web Console

After starting the API, open `http://localhost:8000/console`

---

## API

### POST /api/v1/analyze

Submit a contract for analysis.

```json
{
  "name": "NDA-2025-01",
  "text": "NON-DISCLOSURE AGREEMENT\n\n1. DEFINITION OF CONFIDENTIAL INFORMATION..."
}
```

Response includes clauses, findings, recommendations, audit trail, and summary statistics.

### GET /api/v1/analyses/{id}

Retrieve a previous analysis by ID.

### GET /api/v1/analyses

List all analyses (with pagination).

---

## Project Structure

```
Compliance/
  contract_analyzer/
    agents/                     # A2A agent implementations
      a2a_servers.py            # A2A server wrappers (AgentCards, Executors, Starlette apps)
      contract_understanding.py # Contract parsing agent
      risk_compliance.py        # Risk & compliance evaluation agent
      decision_recommendation.py # Decision & recommendation agent
    api/
      main.py                   # FastAPI application
      routes.py                 # API endpoints
    frontend/console/
      index.html                # Enterprise operations console
    models/
      output.py                 # Pydantic models (Clause, Finding, Recommendation, etc.)
      state.py                  # LangGraph state definition
    orchestrator/
      workflow.py               # LangGraph StateGraph workflow
    persistence/
      database.py               # PostgreSQL persistence (SQLAlchemy)
    retrieval/
      standards_data.py         # Curated standards summaries (80+ entries, 14 standards)
      standards_index.py        # FAISS index management and querying
    config.py                   # Environment-based configuration
    logging_setup.py            # Structured JSON audit logging
  scripts/
    setup_standards_db.py       # Build FAISS index
    run_agents.py               # Launch all services
    demo.py                     # End-to-end demo
  data/
    sample_contracts/           # Sample contracts for testing
  requirements.txt
  .env.example
```

---

## Edge Cases Handled

| Case | Handling |
|------|----------|
| Missing clauses | Flagged as findings with recommendation to add |
| Incomplete contracts | Partial analysis produced; warnings in audit trail |
| Conflicting analysis results | Multiple findings for same clause allowed; conflict noted |
| Low-confidence outputs | Confidence < 0.6 flagged for human review |
| Agent failure | Error state in workflow; partial results preserved |
| No standards matches | "No relevant standards found" context; LLM instructed to note this |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph (StateGraph) |
| Agent Communication | Google A2A SDK (a2a-sdk) |
| LLM | OpenAI GPT-4o (configurable) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS (Facebook AI Similarity Search) |
| API Server | FastAPI + Uvicorn |
| Agent Servers | Starlette + Uvicorn (A2A) |
| Persistence | PostgreSQL + SQLAlchemy |
| Frontend | HTML5 + CSS + Vanilla JavaScript |
| Logging | Structured JSON (stdout) |

---

## License

Proprietary. All rights reserved.
