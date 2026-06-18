# Glass-Box Frontend Redesign — Contract Compliance Analyzer

**Date:** 2026-06-18
**Status:** Spec — awaiting user review
**Scope:** Next.js frontend overhaul to expose the multi-agent RAG pipeline

## Summary

Redesign the Contract Compliance Analyzer frontend from a "black box" AI shell into a transparent "glass-box" console. The new UI exposes the LangGraph orchestrator pipeline, ReAct agent reasoning loop, FAISS/BM25 retrieval, citation verification with hallucination detection, human-in-the-loop escalation tickets, and real-time async analysis progress via Server-Sent Events.

**Tech stack:** Next.js 16 (App Router), Tailwind CSS v4, shadcn/ui, Framer Motion, zustand

---

## 1. Architecture

### 1.1 Navigation Model

**Master-Detail with Context Panel** (3-column console layout):

```
+────────+──────────────────────────────────+─────────────+
│ Sidebar│         Main Panel               │  Inspector  │
│ (240px)│    (flex-1, fills remaining)     │  (380px)    │
│        │                                  │             │
│ History│   [Overview | Findings | Actions │ Contextual: │
│  list  │    | Audit]                      │  - Finding  │
│        │                                  │    detail   │
│  +New  │   Tab content renders here       │  - Verif.   │
│        │                                  │    flags    │
│        │                                  │  - Tickets  │
│        │                                  │  - Summary  │
+────────+──────────────────────────────────+─────────────+
```

- Inspector content is **derived** from current selection (clause, finding, or tickets)
- Sidebar replaces the existing sheet drawer for past analyses
- Live Trace appears as a **slide-over** (520px) during active analysis

### 1.2 Component Tree

```
app/
├── page.tsx                            (thin shell, view routing)
├── console/
│   ├── ConsoleLayout.tsx               (3-column with collapsible sidebar)
│   ├── ConsoleSidebar.tsx              (past analyses list + new analysis button)
│   ├── MainPanel.tsx                   (tab routing container)
│   ├── InspectorPanel.tsx              (right context panel)
│   │
│   ├── tabs/
│   │   ├── OverviewTab.tsx             (enhanced w/ clause-type gutters)
│   │   ├── FindingsTab.tsx             (verification badges added)
│   │   ├── ActionsTab.tsx              (escalation integration)
│   │   └── AuditTab.tsx                (audit trail + standards)
│   │
│   ├── trace/
│   │   ├── LiveTraceOverlay.tsx        (slide-over during analysis)
│   │   ├── LangGraphDAG.tsx            (pipeline stage visualization)
│   │   ├── StageNode.tsx               (single pipeline node)
│   │   ├── ReActLoopViewer.tsx         (tool call iteration feed)
│   │   ├── RetrievalInspector.tsx      (FAISS/BM25 chunk display)
│   │   └── SpecialistBadge.tsx         (Privacy | Financial | Generalist)
│   │
│   ├── verification/
│   │   ├── VerificationPanel.tsx       (inspector content)
│   │   ├── VerificationFlagCard.tsx    (single flag)
│   │   ├── CitationIntegrityBadge.tsx  (verified / hallucinated / unsupported)
│   │   └── ConfidenceIndicator.tsx     (color-coded 0-1 bar)
│   │
│   ├── escalation/
│   │   ├── EscalationPanel.tsx         (inspector content)
│   │   ├── TicketCard.tsx              (severity, reason, linked clause)
│   │   └── ResolutionActions.tsx       (Approve | Escalate | Block buttons)
│   │
│   ├── contract/
│   │   ├── ContractViewer.tsx          (clause-type color margins)
│   │   ├── ClauseGutter.tsx            (margin indicators per ClauseType)
│   │   ├── CrossJurisdictionDiff.tsx   (governing law vs. KB comparison)
│   │   └── InlineFindingsPanel.tsx     (verification-aware)
│   │
│   └── export/
│       ├── ExportButton.tsx            (PDF | CSV dropdown)
│       └── ExportDialog.tsx            (configure export sections)
│
├── submit/
│   ├── SubmissionView.tsx              (replaces LandingPage)
│   ├── FileDropZone.tsx                (existing, unchanged)
│   └── SampleContracts.tsx             (existing, unchanged)
│
└── progress/
    ├── AnalysisProgressTracker.tsx     (full-screen async progress)
    ├── StageTimeline.tsx               (SSE-driven pipeline stepper)
    └── StageDetailCard.tsx             (per-stage details)

stores/
├── index.ts                            (combined zustand store)
├── submission.slice.ts                 (submission + async job tracking)
├── analysis.slice.ts                   (results, tabs, filters, inspector state)
└── livetrace.slice.ts                  (SSE connection, stage progress, trace entries)
```

### 1.3 Removed Components
- `LandingPage.tsx` — replaced by `SubmissionView`
- `AnalysisLoadingOverlay.tsx` — replaced by `AnalysisProgressTracker`
- `ConsolePage.tsx` — decomposed into `console/*`

---

## 2. State Management (zustand)

### 2.1 `submission.slice.ts`

| Field | Type | Purpose |
|-------|------|---------|
| `contractName` | `string` | Contract identifier |
| `contractText` | `string` | Raw contract text |
| `selectedFile` | `File \| null` | Uploaded file |
| `submissionMode` | `"sync" \| "async"` | Analysis mode |
| `jobId` | `string \| null` | Async job ID |
| `jobStatus` | `"idle" \| "submitting" \| "running" \| "completed" \| "failed" \| "needs_review"` | Current job state |
| `jobError` | `string \| null` | Job error message |

Actions: `setInput`, `submitAsync`, `submitSync`, `cancelJob`, `reset`

### 2.2 `analysis.slice.ts`

| Field | Type | Purpose |
|-------|------|---------|
| `analysis` | `AnalysisResponse \| null` | Full analysis result |
| `contractText` | `string` | Contract text |
| `pastAnalyses` | `ContractListItem[]` | History list |
| `mainTab` | `"overview" \| "findings" \| "actions" \| "audit-standards"` | Active tab |
| `selectedClauseId` | `string \| null` | Selected clause |
| `selectedFindingId` | `string \| null` | Selected finding |
| `findingsFilter` | `FindingsFilter` | Active filters |
| `recommendationsView` | `"decision" \| "owner"` | Actions grouping |
| `isLoadingDetail` | `boolean` | Loading past analysis |
| `error` | `string \| null` | Error message |

Actions: `loadAnalysis`, `selectClause`, `selectFinding`, `setMainTab`, `setFindingsFilter`, `clearFindingsFilter`, `setRecommendationsView`, `loadPastAnalysis`, `refreshPastList`, `dismissError`

Derived: `resolvedTickets`, `flaggedFindings`, `inspectorContent`

### 2.3 `livetrace.slice.ts`

| Field | Type | Purpose |
|-------|------|---------|
| `isConnected` | `boolean` | SSE connection alive |
| `eventSource` | `EventSource \| null` | Active connection |
| `currentStage` | `string \| null` | Active pipeline stage |
| `stages` | `Map<string, StageStatus>` | Stage → status mapping |
| `traceEntries` | `AgentTraceEntry[]` | Accumulated trace events |
| `retrievedChunks` | `RetrievedChunk[]` | FAISS/BM25 chunks |
| `reaactIterations` | `number` | Total ReAct iterations |
| `currentIteration` | `number` | Current iteration |

Actions: `connect`, `disconnect`, `pushEvent`, `clear`

---

## 3. New TypeScript Types

Added to `src/lib/types.ts`:

```typescript
export interface VerificationFlag {
  finding_id: string;
  flag_type: "hallucinated_citation" | "unsupported_citation"
    | "disconnected_reasoning" | "risk_level_mismatch" | "generic_exclusion";
  severity: "block" | "warn" | "info";
  detail: string;
}

export interface VerificationReport {
  verified: boolean;
  total_findings: number;
  total_citations: number;
  flags: VerificationFlag[];
  hallucination_count: number;
  adjusted_confidence: number;
}

export interface EscalationTicket {
  ticket_id: string;
  reason: string;
  clause_id: string | null;
  standard: string | null;
  severity: string;
  timestamp: string;
  resolved?: boolean;
  resolution?: { decision: string; timestamp: string };
}

export interface ToolCallEntry {
  tool: string;
  input: string;
  timestamp: string;
}

export interface RetrievedChunk {
  source: "faiss" | "bm25";
  standard: string;
  article: string | null;
  snippet: string;
  relevance_score: number;
}

export interface AgentTraceEntry {
  timestamp: string;
  stage: string;
  action: string;
  specialist?: string;
  reaact_iteration?: number;
  tool_calls?: ToolCallEntry[];
  retrieved_chunks?: RetrievedChunk[];
}

export interface SSEStageEvent {
  type: "stage";
  stage: string;
  status: "started" | "in_progress" | "completed" | "failed";
  timestamp: string;
  message: string;
}

export interface SSETraceEvent {
  type: "trace";
  trace: AgentTraceEntry;
}

export interface SSEErrorEvent {
  type: "error";
  stage: string;
  message: string;
}

export type SSEEvent = SSEStageEvent | SSETraceEvent | SSEErrorEvent;
```

**`AnalysisResponse`** gains: `verification_report: VerificationReport | null`, `escalation_tickets: EscalationTicket[]`, `agent_trace: AgentTraceEntry[]`, `retrieved_evidence: RetrievedChunk[]`

---

## 4. API Layer Changes

### 4.1 New Frontend API Functions

```typescript
// Async submission
submitAsync(name: string, text: string, file?: File): Promise<{ job_id: string; status: string; contract_name: string }>

// Job polling (fallback)
getJobStatus(jobId: string): Promise<JobStatusResponse>

// SSE connection
connectJobStream(jobId: string): EventSource

// Ticket resolution
resolveTicket(analysisId: string, ticketId: string, decision: "approve" | "escalate" | "block"): Promise<void>
```

### 4.2 Data Flow During Analysis

```
User clicks "Run Analysis"
  → submitAsync(name, text, file?)         POST /api/v1/analyze/async
  → connectJobStream(jobId)                GET /api/v1/jobs/{jobId}/stream (SSE)
      ├─ event: stage=parsing, status=started
      ├─ event: trace { stage: "contract_parsing", action: "parsing_complete", clause_count: 14 }
      ├─ event: stage=classifying, status=started
      ├─ event: trace { specialist: "privacy" }
      ├─ event: stage=risk_evaluation, status=started
      ├─ event: trace { tool_calls: [...], retrieved_chunks: [...] }  (repeats per iteration)
      ├─ event: stage=verifying, status=started
      ├─ event: stage=decision_generation, status=started
      └─ event: stage=complete
  → loadAnalysis(result)                   Store result, transition to console
```

### 4.3 Inspector Derivation Logic

```
if selectedFindingId → VerificationDetail (CitationIntegrityBadge + ConfidenceIndicator + VerificationFlagCard)
else if selectedClauseId → InlineFindingsPanel (findings for that clause, verification-aware)
else if unresolved tickets exist → EscalationPanel (TicketCard list with ResolutionActions)
else → SummaryCard (total findings, verification stats, ticket count)
```

---

## 5. Visual Design

### 5.1 Aesthetic Direction

"Legal-grade glass-box" — clean, high-density workstation for compliance engineers. Dark-first, warm-cool palette distinguishing data provenance at a glance.

### 5.2 Semantic Color Tokens

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| Agent intelligence | `#7c3aed` (violet) | Same | Traces, ReAct, specialist badges |
| FAISS retrieval | `#2563eb` (blue) | Same | FAISS-sourced chunks |
| BM25 retrieval | `#d97706` (amber) | Same | BM25-sourced chunks |
| Verified clean | `#059669` (emerald) | Same | Verified findings, clean citations |
| Hallucinated | `#dc2626` (red) | Same | Hallucinated citation flags |
| Unsupported | `#d97706` (amber) | Same | Unsupported citation flags |
| Escalation | `#e11d48` (rose) | Same | Tickets, human review |
| Surface primary | `#ffffff` | `#0a0a0f` | Main backgrounds |
| Surface secondary | `#f4f5f7` | `#111118` | Cards, panels |
| Surface elevated | `#ffffff` | `#1a1a24` | Modals, overlays |
| Text primary | `#0f172a` | `#e2e8f0` | Body text |
| Text muted | `#64748b` | `#94a3b8` | Secondary text |

### 5.3 Clause Type Gutter Colors

| Clause Type | Color |
|-------------|-------|
| `data_protection` | violet |
| `liability` | red |
| `indemnification` | orange |
| `ip_rights` | blue |
| `payment` | green |
| `termination` | rose |
| `confidentiality` | cyan |
| `service_level` | teal |
| `governing_law` | amber |
| `insurance` | lime |
| `audit_rights` | sky |
| `warranty` | yellow |
| `force_majeure` | slate |
| `subcontracting` | pink |
| `other` | gray |

### 5.4 Confidence Indicator

- Horizontal bar, 0-100% width, animated fill on mount
- 0-60%: red · 60-80%: amber · 80-95%: emerald · 95-100%: emerald + checkmark
- Verification-adjusted confidence shown as thinner bar below when different

### 5.5 Animation Principles

- Micro-interactions: 200-300ms
- View transitions: 400-600ms
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` for entrances
- List stagger: 30-50ms per item, max 500ms total
- All animations respect `prefers-reduced-motion`
- Only state transitions animate; static content renders instantly

### 5.6 Progress Tracker Animation

- Pending: gray dot
- Active: pulsing violet dot with ripple
- Complete: emerald checkmark (spring animation)
- Failed: red X (shake animation)
- Stage transitions advance the vertical stepper with Framer Motion `AnimatePresence`

### 5.7 Export Styling

- PDF: `@media print` — grayscale, no animations, full-width, serif body font
- CSV: client-side direct download, no UI beyond export dialog

---

## 6. Error Handling

### 6.1 Error States by Surface

| Surface | Error | Handling |
|---------|-------|----------|
| Submission | File >10MB | Client-side validation, toast + inline message |
| Submission | Unsupported type | Dropzone accept filter + extension check |
| Submission | Empty text (<10 chars) | Button disabled, inline hint |
| Submission | API unreachable | ErrorBanner with retry button |
| Async job | Pipeline failure | SSE error event → stage marked failed, retry or view partial results |
| Async job | Timeout (60s no events) | "Analysis stalled" message with Cancel + Retry |
| SSE stream | Connection drop | Auto-reconnect 1s→2s→4s→max 10s; fallback to polling after 3 failures |
| SSE stream | EventSource not supported | Feature-detect, fallback to polling every 2s |
| Past analyses | List fetch fails | Silent empty list with message |
| Past analysis | Detail fetch 404/500 | ErrorBanner with back button |
| Ticket resolution | POST fails | Toast error, optimistic rollback |
| Export | PDF generation fails | Toast + console error; CSV fallback |
| Verification | No report (old analysis) | "Verification data not available" |

### 6.2 Edge Cases

| Case | Behavior |
|------|----------|
| Zero findings | Green "No compliance issues detected" empty state |
| All findings verified clean | Emerald checkmark, no flags |
| All findings hallucinated | Human review gate, all as escalation tickets |
| Mid-analysis escalation | Tickets appear in SSE trace feed immediately |
| User navigates away during analysis | Job continues server-side; reconnect on return |
| Second submission while running | Confirmation dialog before queuing |
| Very long contract (1000+ clauses) | Virtualized contract viewer (TanStack Virtual) |
| Mobile viewport | Single-column, sidebar→bottom sheet, inspector→full-screen |

### 6.3 Loading States

All async views have skeletons: ContractViewer (12 lines shimmer), FindingsTab (4-6 finding cards), ActionsTab (3-column grid), AuditTrail (timeline), VerificationPanel (2-3 flag placeholders), EscalationPanel (severity badge + text), LiveTraceOverlay (pulsing entries).

---

## 7. Escalation Ticket Resolution Flow

1. Analysis completes with `escalation_tickets[]` → `jobStatus = "needs_review"`
2. Inspector panel shows `EscalationPanel` with unresolved tickets
3. Each `TicketCard` shows severity, reason, linked clause, standard
4. `ResolutionActions` offers 3 buttons:
   - **Approve** (green) — accept the finding, mark ticket resolved
   - **Escalate** (amber) — escalate to legal team (external action)
   - **Block** (red outline) — block the contract, mark ticket resolved
5. Resolution calls `POST /api/v1/analyses/{id}/tickets/{tid}/resolve`
6. Optimistic update: ticket marked resolved immediately, rolled back on error
7. When all tickets resolved, `jobStatus` transitions to `completed`

---

## 8. Implementation Phases

| Phase | Scope | Key Deliverable |
|-------|-------|-----------------|
| 1. Foundation | Types, store, API functions | Data shapes defined, store ready |
| 2. Console Shell | 3-column layout, sidebar, inspector | New layout with existing content |
| 3. Async + Progress | SubmissionView, SSE, progress tracker | Live pipeline progress replaces spinner |
| 4. Live Agent Trace | Trace overlay, DAG, ReAct viewer, retrieval | Glass-box trace visible during analysis |
| 5. Verification | VerificationPanel, flags, confidence | Every finding shows verification status |
| 6. Escalation | EscalationPanel, ticket resolution | User can resolve tickets inline |
| 7. Contract Viewer | Clause gutter, cross-jurisdiction diff | Clause-type coloring, jurisdiction compare |
| 8. Export | PDF/CSV export dialog | Downloadable analysis reports |
| 9. Polish | Mobile, a11y, virtualization, reduced motion | Production-ready across devices |

---

## 9. Backend Changes Required

### 9.1 New Endpoint: SSE Job Stream

```
GET /api/v1/jobs/{job_id}/stream
→ Content-Type: text/event-stream
→ Events: stage, trace, error
```

Implementation: `JobEventBus` class with per-job `asyncio.Queue`. Each LangGraph node publishes events. SSE endpoint drains the queue.

### 9.2 Enhanced Audit Trail in LangGraph Nodes

| Node | New Fields |
|------|------------|
| `_node_evaluate_risk` | `reaact_iterations`, `tool_calls[]`, `retrieved_chunks[]`, `duration_ms` |
| `_node_verify_findings` | `verification_report` (already exists, ensure serialized) |
| All nodes | `specialist` (when applicable), `duration_ms` |

### 9.3 New Endpoint: Resolve Escalation Ticket

```
POST /api/v1/analyses/{analysis_id}/tickets/{ticket_id}/resolve
Body: { "decision": "approve" | "escalate" | "block" }
→ 200: { "ticket_id": "...", "status": "resolved", "decision": "..." }
```

### 9.4 Verify Sync Response Includes New Models

`verification_report` and `escalation_tickets` are already in `ContractSubmitResponse`. Verify correct serialization in async job result dict.

### 9.5 Job Event Bus

```python
class JobEventBus:
    _queues: dict[str, asyncio.Queue] = {}
    
    @classmethod
    def get_queue(cls, job_id: str) -> asyncio.Queue: ...
    @classmethod
    async def publish(cls, job_id: str, event: dict) -> None: ...
    @classmethod
    def remove(cls, job_id: str) -> None: ...
```

Each LangGraph node calls `JobEventBus.publish(job_id, event)` before and after execution.

---

## 10. Dependencies to Add

- `zustand` — state management
- `@tanstack/react-virtual` — contract viewer virtualization (Phase 9)
- `@react-pdf/renderer` or browser `@media print` — PDF export (Phase 8)

No new dependencies for SSE — `EventSource` is a browser built-in.

---

## 11. Files to Create

```
contract-analyzer-frontend/src/
├── stores/index.ts
├── stores/submission.slice.ts
├── stores/analysis.slice.ts
├── stores/livetrace.slice.ts
├── app/console/ConsoleLayout.tsx
├── app/console/ConsoleSidebar.tsx
├── app/console/MainPanel.tsx
├── app/console/InspectorPanel.tsx
├── app/console/tabs/OverviewTab.tsx
├── app/console/tabs/FindingsTab.tsx
├── app/console/tabs/ActionsTab.tsx
├── app/console/tabs/AuditTab.tsx
├── app/console/trace/LiveTraceOverlay.tsx
├── app/console/trace/LangGraphDAG.tsx
├── app/console/trace/StageNode.tsx
├── app/console/trace/ReActLoopViewer.tsx
├── app/console/trace/RetrievalInspector.tsx
├── app/console/trace/SpecialistBadge.tsx
├── app/console/verification/VerificationPanel.tsx
├── app/console/verification/VerificationFlagCard.tsx
├── app/console/verification/CitationIntegrityBadge.tsx
├── app/console/verification/ConfidenceIndicator.tsx
├── app/console/escalation/EscalationPanel.tsx
├── app/console/escalation/TicketCard.tsx
├── app/console/escalation/ResolutionActions.tsx
├── app/console/contract/ContractViewer.tsx
├── app/console/contract/ClauseGutter.tsx
├── app/console/contract/CrossJurisdictionDiff.tsx
├── app/console/contract/InlineFindingsPanel.tsx
├── app/console/export/ExportButton.tsx
├── app/console/export/ExportDialog.tsx
├── app/submit/SubmissionView.tsx
├── app/submit/FileDropZone.tsx
├── app/submit/SampleContracts.tsx
├── app/progress/AnalysisProgressTracker.tsx
├── app/progress/StageTimeline.tsx
└── app/progress/StageDetailCard.tsx
```

## 12. Files to Modify

```
contract-analyzer-frontend/src/
├── lib/types.ts                         (add new types)
├── lib/api.ts                           (add async/SSE/ticket functions)
├── lib/utils.ts                         (add clause gutter colors)
├── app/layout.tsx                       (metadata update)
├── app/page.tsx                         (route to new components)
├── components/ErrorBanner.tsx           (wire retry)
├── components/JurisdictionBar.tsx       (add CrossJurisdictionDiff link)
└── next.config.ts                       (add SSE rewrite if needed)
```

## 13. Files to Remove

```
contract-analyzer-frontend/src/
├── app/components/LandingPage.tsx       (replaced by SubmissionView)
├── app/components/AnalysisLoadingOverlay.tsx  (replaced by progress tracker)
├── app/components/ConsolePage.tsx       (decomposed into console/*)
├── hooks/useAnalysis.ts                (replaced by zustand stores)
└── lib/samples.ts                      (moved to app/submit/SampleContracts.tsx)
```
