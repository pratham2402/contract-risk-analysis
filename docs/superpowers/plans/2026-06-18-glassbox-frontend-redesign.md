# Glass-Box Frontend Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul the Contract Compliance Analyzer Next.js frontend from a black-box AI shell into a transparent glass-box console exposing multi-agent reasoning, FAISS/BM25 retrieval, citation verification with hallucination detection, escalation ticket workflow, and SSE-driven real-time progress.

**Architecture:** 3-column master-detail layout (Sidebar | Main Panel | Inspector) with zustand state management across 3 slices (submission, analysis, livetrace). Server-Sent Events drive the live analysis progress tracker and agent trace overlay. Inspector panel derives content from current selection (clause, finding, or tickets).

**Tech Stack:** Next.js 16 (App Router), Tailwind CSS v4, shadcn/ui, Framer Motion, zustand, TypeScript

**Spec:** `docs/superpowers/specs/2026-06-18-glassbox-frontend-redesign.md`

## Global Constraints

- Next.js 16 App Router with `"use client"` for interactive components
- Tailwind CSS v4 for all styling; shadcn/ui for base components
- Framer Motion for all state-transition animations; respect `prefers-reduced-motion`
- zustand for state management (3 slices: submission, analysis, livetrace)
- All new files use TypeScript with strict types from `@/lib/types`
- Frequent commits between tasks — every task ends with a commit
- Color tokens from spec section 5.2 and 5.3 must be used consistently

---

## Phase 1: Foundation — Types, Store, API Layer

### Task 1.1: Install zustand dependency

- [ ] **Step 1: Install zustand**

```bash
cd contract-analyzer-frontend && npm install zustand
```

- [ ] **Step 2: Verify install**

Check `package.json` for `"zustand"` entry.

- [ ] **Step 3: Commit**

```bash
git add contract-analyzer-frontend/package.json contract-analyzer-frontend/package-lock.json
git commit -m "deps: add zustand for state management"
```

### Task 1.2: Add new TypeScript types

**Files:**
- Modify: `contract-analyzer-frontend/src/lib/types.ts`

- [ ] **Step 1: Append new types to types.ts**

Add the following after the existing `AnalysisResponse` interface:

```typescript
// ── Verification types ───────────────────────────────────────

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

// ── Escalation types ─────────────────────────────────────────

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

// ── Agent trace types ────────────────────────────────────────

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

// ── SSE event types ──────────────────────────────────────────

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

- [ ] **Step 2: Update AnalysisResponse to include new fields**

Add these fields to the `AnalysisResponse` interface (after `audit_trail`):

```typescript
export interface AnalysisResponse {
  // ... existing fields ...
  verification_report: VerificationReport | null;
  escalation_tickets: EscalationTicket[];
  agent_trace: AgentTraceEntry[];
  retrieved_evidence: RetrievedChunk[];
}
```

- [ ] **Step 3: Type-check**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
```

Expected: no new type errors from `types.ts`.

- [ ] **Step 4: Commit**

```bash
git add contract-analyzer-frontend/src/lib/types.ts
git commit -m "feat: add verification, escalation, trace, and SSE types"
```

### Task 1.3: Add utility functions for new visual elements

**Files:**
- Modify: `contract-analyzer-frontend/src/lib/utils.ts`

- [ ] **Step 1: Add clause gutter color map**

After the existing color maps in `utils.ts`, add:

```typescript
export const CLAUSE_TYPE_COLORS: Record<string, string> = {
  data_protection: "bg-violet-500",
  liability: "bg-red-500",
  indemnification: "bg-orange-500",
  ip_rights: "bg-blue-500",
  payment: "bg-green-500",
  termination: "bg-rose-500",
  confidentiality: "bg-cyan-500",
  service_level: "bg-teal-500",
  governing_law: "bg-amber-500",
  insurance: "bg-lime-500",
  audit_rights: "bg-sky-500",
  warranty: "bg-yellow-500",
  force_majeure: "bg-slate-500",
  subcontracting: "bg-pink-500",
  other: "bg-gray-500",
};

export const CLAUSE_TYPE_BORDER_COLORS: Record<string, string> = {
  data_protection: "border-l-violet-500",
  liability: "border-l-red-500",
  indemnification: "border-l-orange-500",
  ip_rights: "border-l-blue-500",
  payment: "border-l-green-500",
  termination: "border-l-rose-500",
  confidentiality: "border-l-cyan-500",
  service_level: "border-l-teal-500",
  governing_law: "border-l-amber-500",
  insurance: "border-l-lime-500",
  audit_rights: "border-l-sky-500",
  warranty: "border-l-yellow-500",
  force_majeure: "border-l-slate-500",
  subcontracting: "border-l-pink-500",
  other: "border-l-gray-500",
};
```

- [ ] **Step 2: Add confidence indicator helper**

```typescript
export function confidenceColor(value: number): string {
  if (value >= 0.95) return "bg-emerald-500";
  if (value >= 0.80) return "bg-emerald-400";
  if (value >= 0.60) return "bg-amber-500";
  return "bg-red-500";
}

export function confidenceLabel(value: number): string {
  if (value >= 0.95) return "Verified High";
  if (value >= 0.80) return "High";
  if (value >= 0.60) return "Moderate";
  return "Low";
}
```

- [ ] **Step 3: Add flag severity and verification status colors**

```typescript
export const FLAG_SEVERITY_COLORS: Record<string, string> = {
  block: "border-l-red-500 bg-red-50 dark:bg-red-950/20",
  warn: "border-l-amber-500 bg-amber-50 dark:bg-amber-950/20",
  info: "border-l-slate-500 bg-slate-50 dark:bg-slate-950/20",
};

export const VERIFICATION_STATUS_COLORS: Record<string, string> = {
  unverified: "text-slate-500",
  verified_clean: "text-emerald-500",
  verified_with_flags: "text-amber-500",
  escalated: "text-rose-500",
};

export const VERIFICATION_STATUS_LABELS: Record<string, string> = {
  unverified: "Unverified",
  verified_clean: "Verified",
  verified_with_flags: "Flagged",
  escalated: "Escalated",
};
```

- [ ] **Step 4: Add source color helpers for FAISS/BM25**

```typescript
export const RETRIEVAL_SOURCE_COLORS = {
  faiss: { bg: "bg-blue-500/10", border: "border-blue-500", text: "text-blue-600 dark:text-blue-400", badge: "bg-blue-500" },
  bm25: { bg: "bg-amber-500/10", border: "border-amber-500", text: "text-amber-600 dark:text-amber-400", badge: "bg-amber-500" },
} as const;
```

- [ ] **Step 5: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/lib/utils.ts
git commit -m "feat: add clause gutter colors, confidence bar, and verification color helpers"
```

### Task 1.4: Create zustand store — submission slice

**Files:**
- Create: `contract-analyzer-frontend/src/stores/submission.slice.ts`

- [ ] **Step 1: Write submission slice**

```typescript
import type { StateCreator } from "zustand";

export type SubmissionMode = "sync" | "async";
export type JobStatus = "idle" | "submitting" | "running" | "completed" | "failed" | "needs_review";

export interface SubmissionSlice {
  contractName: string;
  contractText: string;
  selectedFile: File | null;
  submissionMode: SubmissionMode;
  jobId: string | null;
  jobStatus: JobStatus;
  jobError: string | null;

  setInput: (name: string, text: string, file?: File) => void;
  setSubmitting: (jobId: string) => void;
  setJobRunning: () => void;
  setJobCompleted: () => void;
  setJobNeedsReview: () => void;
  setJobFailed: (error: string) => void;
  cancelJob: () => void;
  reset: () => void;
}

const initialSubmission = {
  contractName: "",
  contractText: "",
  selectedFile: null,
  submissionMode: "async" as SubmissionMode,
  jobId: null as string | null,
  jobStatus: "idle" as JobStatus,
  jobError: null as string | null,
};

export const createSubmissionSlice: StateCreator<SubmissionSlice> = (set) => ({
  ...initialSubmission,

  setInput: (name, text, file) =>
    set({ contractName: name, contractText: text, selectedFile: file ?? null }),

  setSubmitting: (jobId) =>
    set({ jobId, jobStatus: "submitting", jobError: null }),

  setJobRunning: () =>
    set({ jobStatus: "running" }),

  setJobCompleted: () =>
    set({ jobStatus: "completed" }),

  setJobNeedsReview: () =>
    set({ jobStatus: "needs_review" }),

  setJobFailed: (error) =>
    set({ jobStatus: "failed", jobError: error }),

  cancelJob: () =>
    set({ jobStatus: "idle", jobId: null }),

  reset: () => set(initialSubmission),
});
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/stores/submission.slice.ts
git commit -m "feat: create submission zustand slice"
```

### Task 1.5: Create zustand store — analysis slice

**Files:**
- Create: `contract-analyzer-frontend/src/stores/analysis.slice.ts`

- [ ] **Step 1: Write analysis slice**

```typescript
import type { StateCreator } from "zustand";
import type {
  AnalysisResponse,
  ContractListItem,
  EscalationTicket,
  Finding,
  RiskLevel,
} from "@/lib/types";

export type MainTab = "overview" | "findings" | "actions" | "audit-standards";
export type RecommendationsView = "decision" | "owner";

export interface FindingsFilter {
  riskLevels: RiskLevel[];
  category: string;
  standard: string;
  search: string;
}

export type InspectorView = "summary" | "clause" | "finding" | "escalation";

export interface AnalysisSlice {
  analysis: AnalysisResponse | null;
  contractText: string;
  pastAnalyses: ContractListItem[];
  mainTab: MainTab;
  selectedClauseId: string | null;
  selectedFindingId: string | null;
  findingsFilter: FindingsFilter;
  recommendationsView: RecommendationsView;
  isLoadingDetail: boolean;
  error: string | null;

  loadAnalysis: (analysis: AnalysisResponse, text: string) => void;
  selectClause: (id: string | null) => void;
  selectFinding: (id: string | null) => void;
  setMainTab: (tab: MainTab) => void;
  setFindingsFilter: (partial: Partial<FindingsFilter>) => void;
  clearFindingsFilter: () => void;
  setRecommendationsView: (view: RecommendationsView) => void;
  setPastAnalyses: (list: ContractListItem[]) => void;
  dismissError: () => void;
}

const defaultFilter: FindingsFilter = {
  riskLevels: [],
  category: "",
  standard: "",
  search: "",
};

export const createAnalysisSlice: StateCreator<AnalysisSlice> = (set) => ({
  analysis: null,
  contractText: "",
  pastAnalyses: [],
  mainTab: "overview",
  selectedClauseId: null,
  selectedFindingId: null,
  findingsFilter: defaultFilter,
  recommendationsView: "decision",
  isLoadingDetail: false,
  error: null,

  loadAnalysis: (analysis, text) =>
    set({
      analysis,
      contractText: text || analysis.contract_text || "",
      mainTab: "overview",
      selectedClauseId: null,
      selectedFindingId: null,
      findingsFilter: defaultFilter,
      isLoadingDetail: false,
      error: null,
    }),

  selectClause: (id) =>
    set({ selectedClauseId: id, selectedFindingId: null }),

  selectFinding: (id) =>
    set({ selectedFindingId: id, selectedClauseId: null }),

  setMainTab: (tab) => set({ mainTab: tab }),

  setFindingsFilter: (partial) =>
    set((s) => ({ findingsFilter: { ...s.findingsFilter, ...partial } })),

  clearFindingsFilter: () => set({ findingsFilter: defaultFilter }),

  setRecommendationsView: (view) => set({ recommendationsView: view }),

  setPastAnalyses: (list) => set({ pastAnalyses: list }),

  dismissError: () => set({ error: null }),
});
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/stores/analysis.slice.ts
git commit -m "feat: create analysis zustand slice"
```

### Task 1.6: Create zustand store — livetrace slice

**Files:**
- Create: `contract-analyzer-frontend/src/stores/livetrace.slice.ts`

- [ ] **Step 1: Write livetrace slice**

```typescript
import type { StateCreator } from "zustand";
import type { AgentTraceEntry, RetrievedChunk, SSEEvent } from "@/lib/types";

export interface StageStatus {
  status: "pending" | "active" | "completed" | "failed";
  startedAt: string | null;
  completedAt: string | null;
}

export interface LiveTraceSlice {
  isConnected: boolean;
  currentStage: string | null;
  stages: Record<string, StageStatus>;
  traceEntries: AgentTraceEntry[];
  retrievedChunks: RetrievedChunk[];
  reaactIterations: number;
  currentIteration: number;

  connect: (jobId: string) => void;
  disconnect: () => void;
  pushEvent: (event: SSEEvent) => void;
  clear: () => void;
}

const STAGE_ORDER = [
  "parsing",
  "classifying",
  "risk_evaluation",
  "verifying",
  "decision_generation",
  "complete",
];

function buildInitialStages(): Record<string, StageStatus> {
  const stages: Record<string, StageStatus> = {};
  for (const name of STAGE_ORDER) {
    stages[name] = { status: "pending", startedAt: null, completedAt: null };
  }
  return stages;
}

export const createLiveTraceSlice: StateCreator<LiveTraceSlice> = (set, get) => {
  let eventSource: EventSource | null = null;

  return {
    isConnected: false,
    currentStage: null,
    stages: buildInitialStages(),
    traceEntries: [],
    retrievedChunks: [],
    reaactIterations: 0,
    currentIteration: 0,

    connect: (jobId) => {
      // Close existing connection
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }

      const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/jobs/${jobId}/stream`;

      eventSource = new EventSource(url);

      eventSource.onopen = () => {
        set({ isConnected: true });
      };

      eventSource.onmessage = (e) => {
        try {
          const event: SSEEvent = JSON.parse(e.data);
          get().pushEvent(event);
        } catch {
          // ignore malformed events
        }
      };

      eventSource.onerror = () => {
        set({ isConnected: false });
        // Auto-reconnect handled by EventSource built-in behavior
      };
    },

    disconnect: () => {
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
      set({ isConnected: false });
    },

    pushEvent: (event) => {
      if (event.type === "stage") {
        set((s) => ({
          currentStage: event.stage,
          stages: {
            ...s.stages,
            [event.stage]: {
              status:
                event.status === "started"
                  ? "active"
                  : event.status === "completed"
                    ? "completed"
                    : event.status === "failed"
                      ? "failed"
                      : "active",
              startedAt:
                event.status === "started"
                  ? event.timestamp
                  : s.stages[event.stage]?.startedAt ?? null,
              completedAt:
                event.status === "completed" || event.status === "failed"
                  ? event.timestamp
                  : null,
            },
          },
        }));
      } else if (event.type === "trace") {
        set((s) => {
          const entry = event.trace;
          const newChunks = entry.retrieved_chunks
            ? [...s.retrievedChunks, ...entry.retrieved_chunks]
            : s.retrievedChunks;
          return {
            traceEntries: [...s.traceEntries, entry],
            retrievedChunks: newChunks,
            reaactIterations:
              entry.reaact_iteration != null
                ? Math.max(s.reaactIterations, entry.reaact_iteration)
                : s.reaactIterations,
            currentIteration: entry.reaact_iteration ?? s.currentIteration,
          };
        });
      }
      // error events are handled at the component level via a dedicated handler
    },

    clear: () =>
      set({
        isConnected: false,
        currentStage: null,
        stages: buildInitialStages(),
        traceEntries: [],
        retrievedChunks: [],
        reaactIterations: 0,
        currentIteration: 0,
      }),
  };
};
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/stores/livetrace.slice.ts
git commit -m "feat: create livetrace zustand slice with SSE handling"
```

### Task 1.7: Create combined zustand store

**Files:**
- Create: `contract-analyzer-frontend/src/stores/index.ts`

- [ ] **Step 1: Write combined store**

```typescript
"use client";

import { create } from "zustand";
import {
  createSubmissionSlice,
  type SubmissionSlice,
} from "./submission.slice";
import {
  createAnalysisSlice,
  type AnalysisSlice,
} from "./analysis.slice";
import {
  createLiveTraceSlice,
  type LiveTraceSlice,
} from "./livetrace.slice";

export type AppStore = SubmissionSlice & AnalysisSlice & LiveTraceSlice;

export const useStore = create<AppStore>()((...args) => ({
  ...createSubmissionSlice(...args),
  ...createAnalysisSlice(...args),
  ...createLiveTraceSlice(...args),
}));
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/stores/index.ts
git commit -m "feat: create combined zustand store"
```

### Task 1.8: Add async API functions

**Files:**
- Modify: `contract-analyzer-frontend/src/lib/api.ts`

- [ ] **Step 1: Add new API functions to api.ts**

Append after the existing `getAnalysis` function:

```typescript
// ── Async submission ─────────────────────────────────────────

export interface JobSubmitResponse {
  job_id: string;
  status: string;
  contract_name: string;
}

export interface JobStatusResponse {
  job_id: string;
  contract_name: string;
  status: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
  result: AnalysisResponse | null;
}

export async function submitAsync(
  name: string,
  text: string,
  file?: File
): Promise<JobSubmitResponse> {
  if (file) {
    const form = new FormData();
    form.append("file", file);
    if (name) form.append("name", name);
    const res = await fetch(`${BASE}/analyze/async`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail ?? "Upload failed");
    }
    return res.json();
  }

  const res = await fetch(`${BASE}/analyze/async`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name || "Unnamed Contract", text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Submission failed" }));
    throw new Error(err.detail ?? "Submission failed");
  }
  return res.json();
}

export async function getJobStatus(
  jobId: string
): Promise<JobStatusResponse> {
  const res = await fetch(`${BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export function connectJobStream(jobId: string): EventSource {
  const url = `${BASE}/jobs/${jobId}/stream`;
  return new EventSource(url);
}

export async function resolveTicket(
  analysisId: string,
  ticketId: string,
  decision: "approve" | "escalate" | "block"
): Promise<void> {
  const res = await fetch(
    `${BASE}/analyses/${analysisId}/tickets/${ticketId}/resolve`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Resolution failed" }));
    throw new Error(err.detail ?? "Resolution failed");
  }
}
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/lib/api.ts
git commit -m "feat: add async submission, job polling, SSE, and ticket resolution API functions"
```

---

## Phase 2: Console Shell — 3-Column Layout

### Task 2.1: Create ConsoleLayout

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/ConsoleLayout.tsx`

- [ ] **Step 1: Write ConsoleLayout component**

```typescript
"use client";

import { type ReactNode, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConsoleSidebar } from "./ConsoleSidebar";
import { InspectorPanel } from "./InspectorPanel";

export function ConsoleLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-white dark:bg-[#0a0a0f]">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 240, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="h-full shrink-0 overflow-hidden border-r border-slate-200 dark:border-slate-800"
          >
            <ConsoleSidebar />
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <div className="flex h-10 items-center gap-2 border-b border-slate-200 px-3 dark:border-slate-800">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setSidebarOpen((v) => !v)}
          >
            {sidebarOpen ? (
              <PanelLeftClose className="h-4 w-4" />
            ) : (
              <PanelLeftOpen className="h-4 w-4" />
            )}
          </Button>
          <span className="text-xs font-semibold tracking-widest text-slate-500">
            COMPLIANCE ANALYZER
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </main>

      {/* Inspector */}
      <aside className="h-full w-[380px] shrink-0 overflow-y-auto border-l border-slate-200 dark:border-slate-800">
        <InspectorPanel />
      </aside>
    </div>
  );
}
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/app/console/ConsoleLayout.tsx
git commit -m "feat: create 3-column ConsoleLayout with collapsible sidebar"
```

### Task 2.2: Create ConsoleSidebar

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/ConsoleSidebar.tsx`

- [ ] **Step 1: Write ConsoleSidebar component**

```typescript
"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Plus,
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { listAnalyses } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { ContractListItem } from "@/lib/types";

const statusIcon: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
  pending: <Clock className="h-4 w-4 text-amber-500" />,
  running: <Clock className="h-4 w-4 text-blue-500 animate-pulse" />,
  failed: <XCircle className="h-4 w-4 text-red-500" />,
  needs_review: <AlertCircle className="h-4 w-4 text-rose-500" />,
};

export function ConsoleSidebar() {
  const pastAnalyses = useStore((s) => s.pastAnalyses);
  const setPastAnalyses = useStore((s) => s.setPastAnalyses);
  const loadAnalysis = useStore((s) => s.loadAnalysis);
  const reset = useStore((s) => s.reset);

  useEffect(() => {
    listAnalyses()
      .then(setPastAnalyses)
      .catch(() => {});
  }, [setPastAnalyses]);

  const handleNew = () => {
    reset();
  };

  const handleSelect = async (item: ContractListItem) => {
    try {
      const { getAnalysis } = await import("@/lib/api");
      const detail = await getAnalysis(item.id);
      const analysis = detail.analysis ?? (detail as unknown as Parameters<typeof loadAnalysis>[0]);
      loadAnalysis(analysis, detail.contract_text ?? "");
    } catch {
      // silently fail — items may be stale
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-50 dark:bg-[#111118]">
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2.5 dark:border-slate-800">
        <span className="text-xs font-semibold tracking-wider text-slate-500">
          PAST ANALYSES
        </span>
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleNew}>
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="space-y-0.5 p-2">
          {pastAnalyses.length === 0 && (
            <p className="px-3 py-8 text-center text-xs text-slate-400">
              No analyses yet
            </p>
          )}
          {pastAnalyses.map((item, i) => (
            <motion.button
              key={item.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03, duration: 0.2 }}
              onClick={() => handleSelect(item)}
              className="flex w-full items-start gap-2 rounded-md px-3 py-2 text-left transition-colors hover:bg-slate-200/60 dark:hover:bg-slate-800/60"
            >
              {statusIcon[item.status] ?? statusIcon.completed}
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-medium text-slate-700 dark:text-slate-300">
                  {item.name}
                </div>
                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <span>{formatDate(item.created_at)}</span>
                  {item.finding_count > 0 && (
                    <span>{item.finding_count} findings</span>
                  )}
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/app/console/ConsoleSidebar.tsx
git commit -m "feat: create ConsoleSidebar with past analyses list"
```

### Task 2.3: Create InspectorPanel with derivation logic

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/InspectorPanel.tsx`

- [ ] **Step 1: Write InspectorPanel component**

```typescript
"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, AlertTriangle, FileSearch } from "lucide-react";
import { useStore } from "@/stores";
import type { InspectorView } from "@/stores/analysis.slice";

export function InspectorPanel() {
  const analysis = useStore((s) => s.analysis);
  const selectedClauseId = useStore((s) => s.selectedClauseId);
  const selectedFindingId = useStore((s) => s.selectedFindingId);

  const inspectorView: InspectorView = useMemo(() => {
    if (selectedFindingId) return "finding";
    if (selectedClauseId) return "clause";
    if (
      analysis?.escalation_tickets?.some((t) => !t.resolved)
    )
      return "escalation";
    return "summary";
  }, [selectedFindingId, selectedClauseId, analysis]);

  if (!analysis) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-center">
        <p className="text-sm text-slate-400">
          No analysis loaded. Submit a contract to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      <motion.div
        key={inspectorView}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {inspectorView === "summary" && <SummaryCard />}
        {inspectorView === "clause" && (
          <div className="space-y-3">
            <InlineFindingsPanel clauseId={selectedClauseId!} />
          </div>
        )}
        {inspectorView === "finding" && (
          <div className="space-y-3">
            {/* VerificationDetail — built in Phase 5 */}
            <p className="text-sm text-slate-400">Finding detail — Phase 5</p>
          </div>
        )}
        {inspectorView === "escalation" && (
          <div className="space-y-3">
            {/* EscalationPanel — built in Phase 6 */}
            <p className="text-sm text-slate-400">Escalation tickets — Phase 6</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}

function SummaryCard() {
  const analysis = useStore((s) => s.analysis);
  if (!analysis) return null;

  const summary = analysis.summary;
  const vrf = analysis.verification_report;
  const tickets = analysis.escalation_tickets ?? [];
  const unresolvedTickets = tickets.filter((t) => !t.resolved).length;
  const totalFlags = vrf?.flags?.length ?? 0;
  const hallucinations = vrf?.hallucination_count ?? 0;

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-semibold tracking-widest text-slate-400">
        SUMMARY
      </h3>

      <div className="grid grid-cols-2 gap-3">
        <StatBox
          icon={<FileSearch className="h-4 w-4 text-violet-500" />}
          label="Clauses"
          value={summary.total_clauses}
        />
        <StatBox
          icon={<AlertTriangle className="h-4 w-4 text-rose-500" />}
          label="Findings"
          value={summary.total_findings}
        />
        <StatBox
          icon={<ShieldCheck className="h-4 w-4 text-emerald-500" />}
          label="Verified"
          value={summary.total_findings - totalFlags}
        />
        <StatBox
          icon={<AlertTriangle className="h-4 w-4 text-amber-500" />}
          label="Flags"
          value={totalFlags}
        />
      </div>

      {hallucinations > 0 && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 dark:border-red-900 dark:bg-red-950/20">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">
            {hallucinations} hallucinated citation{hallucinations > 1 ? "s" : ""} detected
          </p>
          <p className="mt-1 text-xs text-red-600 dark:text-red-500">
            These findings cite standards that do not contain the claimed text.
          </p>
        </div>
      )}

      {unresolvedTickets > 0 && (
        <div className="rounded-md border border-rose-200 bg-rose-50 p-3 dark:border-rose-900 dark:bg-rose-950/20">
          <p className="text-sm font-medium text-rose-700 dark:text-rose-400">
            {unresolvedTickets} unresolved escalation ticket{unresolvedTickets > 1 ? "s" : ""}
          </p>
          <p className="mt-1 text-xs text-rose-600 dark:text-rose-500">
            These require human review before the analysis can be finalized.
          </p>
        </div>
      )}

      {totalFlags === 0 && unresolvedTickets === 0 && (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3 dark:border-emerald-900 dark:bg-emerald-950/20">
          <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">
            All findings verified clean
          </p>
          <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-500">
            No hallucinated citations or unresolved escalations.
          </p>
        </div>
      )}
    </div>
  );
}

function StatBox({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-[#1a1a24]">
      <div className="mb-1 flex items-center gap-1.5">
        {icon}
        <span className="text-[11px] text-slate-400">{label}</span>
      </div>
      <div className="text-2xl font-semibold text-slate-800 dark:text-slate-200">
        {value}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/app/console/InspectorPanel.tsx
git commit -m "feat: create InspectorPanel with summary card and view derivation"
```

### Task 2.4: Create MainPanel with tab routing

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/MainPanel.tsx`

- [ ] **Step 1: Write MainPanel component**

```typescript
"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useStore } from "@/stores";
import type { MainTab } from "@/stores/analysis.slice";
import { OverviewTab } from "./tabs/OverviewTab";
import { FindingsTab } from "./tabs/FindingsTab";
import { ActionsTab } from "./tabs/ActionsTab";
import { AuditTab } from "./tabs/AuditTab";

export function MainPanel() {
  const mainTab = useStore((s) => s.mainTab);
  const setMainTab = useStore((s) => s.setMainTab);
  const analysis = useStore((s) => s.analysis);

  if (!analysis) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-slate-400">
          No analysis loaded. Submit a contract to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <Tabs
        value={mainTab}
        onValueChange={(v) => setMainTab(v as MainTab)}
        className="flex h-full flex-col"
      >
        <div className="shrink-0 border-b border-slate-200 px-4 dark:border-slate-800">
          <TabsList className="h-9">
            <TabsTrigger value="overview" className="text-xs">
              Overview
            </TabsTrigger>
            <TabsTrigger value="findings" className="text-xs">
              Findings
            </TabsTrigger>
            <TabsTrigger value="actions" className="text-xs">
              Actions
            </TabsTrigger>
            <TabsTrigger value="audit-standards" className="text-xs">
              Audit & Standards
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-hidden">
          {mainTab === "overview" && <OverviewTab />}
          {mainTab === "findings" && <FindingsTab />}
          {mainTab === "actions" && <ActionsTab />}
          {mainTab === "audit-standards" && <AuditTab />}
        </div>
      </Tabs>
    </div>
  );
}
```

- [ ] **Step 2: Type-check** (will fail until tabs are created — expected)

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
```

- [ ] **Step 3: Commit** (commit even though tabs are stubs — they'll be filled in next)

```bash
git add contract-analyzer-frontend/src/app/console/MainPanel.tsx
git commit -m "feat: create MainPanel with tab routing"
```

### Task 2.5: Migrate existing tabs into console/tabs/

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/tabs/OverviewTab.tsx`
- Create: `contract-analyzer-frontend/src/app/console/tabs/FindingsTab.tsx`
- Create: `contract-analyzer-frontend/src/app/console/tabs/ActionsTab.tsx`
- Create: `contract-analyzer-frontend/src/app/console/tabs/AuditTab.tsx`

- [ ] **Step 1: Extract OverviewTab**

Copy the existing Overview section from `ConsolePage.tsx` into `OverviewTab.tsx`. Replace `useAnalysis()` calls with `useStore()` selectors:

```typescript
"use client";

import { motion } from "framer-motion";
import { useStore } from "@/stores";
import { formatDuration } from "@/lib/utils";
import { RiskDistributionBar } from "@/components/RiskDistributionBar"; // existing component
import { ContractViewer } from "../contract/ContractViewer";
import { JurisdictionBar } from "@/components/JurisdictionBar";

export function OverviewTab() {
  const analysis = useStore((s) => s.analysis);
  const selectClause = useStore((s) => s.selectClause);
  const selectedClauseId = useStore((s) => s.selectedClauseId);

  if (!analysis) return null;
  const summary = analysis.summary;

  return (
    <div className="flex h-full flex-col overflow-y-auto p-4 space-y-4">
      <JurisdictionBar analysis={analysis} />

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard
          icon="AlertTriangle"
          label="Total Findings"
          value={summary.total_findings}
        />
        <StatCard
          icon="Shield"
          label="Critical / High"
          value={
            (summary.risk_counts.critical ?? 0) + (summary.risk_counts.high ?? 0)
          }
          accent="border-l-red-500"
        />
        <StatCard
          icon="Clock"
          label="Duration"
          value={formatDuration(analysis.total_duration_ms)}
        />
      </div>

      {/* Risk distribution bar */}
      <RiskDistributionBar riskCounts={summary.risk_counts} />

      {/* Contract viewer */}
      <div className="flex-1 min-h-0">
        <ContractViewer
          text={analysis.contract_text ?? ""}
          clauses={analysis.clauses}
          findings={analysis.findings}
          selectedClauseId={selectedClauseId}
          onSelectClause={selectClause}
        />
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  accent,
}: {
  icon: string;
  label: string;
  value: string | number;
  accent?: string;
}) {
  return (
    <div
      className={`rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-[#1a1a24] ${accent ?? ""}`}
    >
      <p className="text-[11px] text-slate-400">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-800 dark:text-slate-200">
        {value}
      </p>
    </div>
  );
}
```

- [ ] **Step 2: Extract FindingsTab, ActionsTab, AuditTab**

Extract each from the existing `ConsolePage.tsx` into their respective files under `tabs/`. Each should:
- Import from `@/stores` (`useStore`) instead of `useAnalysis()`
- Use `useStore` selectors: `useStore((s) => s.fieldName)`
- Keep all existing filter/search/group functionality

The conversion pattern for all three tabs:
- Replace `useAnalysis()` destructuring with individual `useStore((s) => s.xxx)` calls
- Replace action calls: `setFindingsFilter({...})` → `useStore((s) => s.setFindingsFilter)({...})` or import the setter
- For `FindingsTab`: add the filter toolbar, findings list, empty states
- For `ActionsTab`: keep the "By Decision" / "By Owner" toggle with recommendation cards
- For `AuditTab`: keep the two-column layout with audit trail timeline and standards panel

- [ ] **Step 3: Type-check**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
```

Expected: type errors from unresolved imports for new components (ContractViewer in new location, ClauseGutter). These will be fixed in Phase 7.

- [ ] **Step 4: Commit**

```bash
git add contract-analyzer-frontend/src/app/console/tabs/
git commit -m "feat: migrate existing tabs into console/tabs/ with zustand selectors"
```

### Task 2.6: Create SubmissionView (replacement for LandingPage)

**Files:**
- Create: `contract-analyzer-frontend/src/app/submit/SubmissionView.tsx`

- [ ] **Step 1: Write SubmissionView**

```typescript
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Loader2 } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useStore } from "@/stores";
import { submitAsync, submitContract } from "@/lib/api";
import { toast } from "sonner";

const SAMPLE_NDA = `...`; // existing sample text
const SAMPLE_SAAS = `...`; // existing sample text

type InputMode = "upload" | "paste";

export function SubmissionView() {
  const [mode, setMode] = useState<InputMode>("paste");
  const [name, setName] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setInput = useStore((s) => s.setInput);
  const setSubmitting = useStore((s) => s.setSubmitting);
  const setJobRunning = useStore((s) => s.setJobRunning);
  const loadAnalysis = useStore((s) => s.loadAnalysis);

  const canSubmit = (mode === "upload" && file) || (mode === "paste" && text.length >= 10);

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setIsSubmitting(true);
    setError(null);

    try {
      const submittedName = name || file?.name || "Unnamed Contract";
      setInput(submittedName, text, file ?? undefined);

      const job = await submitAsync(submittedName, text, file ?? undefined);
      setSubmitting(job.job_id);
      setJobRunning();
      // SSE connection and progress tracker handled by parent page
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Submission failed";
      setError(msg);
      toast.error(msg);
      setIsSubmitting(false);
    }
  };

  const loadSample = (sample: string, sampleName: string) => {
    setText(sample);
    setName(sampleName);
    setMode("paste");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-[#0a0a0f]">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-[#111118]"
      >
        {/* Header */}
        <div className="text-center space-y-1">
          <h1 className="text-xl font-semibold text-slate-800 dark:text-slate-200">
            Contract Compliance Analyzer
          </h1>
          <p className="text-sm text-slate-500">
            AI-powered contract risk analysis against 17 regulatory standards
          </p>
        </div>

        {/* Input mode toggle */}
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
          <button
            onClick={() => setMode("upload")}
            className={`flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              mode === "upload"
                ? "bg-white text-slate-800 shadow-sm dark:bg-slate-700 dark:text-slate-200"
                : "text-slate-500"
            }`}
          >
            <Upload className="h-4 w-4" />
            Upload Document
          </button>
          <button
            onClick={() => setMode("paste")}
            className={`flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              mode === "paste"
                ? "bg-white text-slate-800 shadow-sm dark:bg-slate-700 dark:text-slate-200"
                : "text-slate-500"
            }`}
          >
            <FileText className="h-4 w-4" />
            Paste Text
          </button>
        </div>

        {/* Name field */}
        <Input
          placeholder="Contract name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="text-sm"
        />

        {/* Input area */}
        {mode === "upload" ? (
          <FileDropZone
            file={file}
            onFileSelect={setFile}
            accept=".pdf,.docx,.txt"
            maxSizeMB={10}
          />
        ) : (
          <Textarea
            placeholder="Paste your contract text here (minimum 10 characters)..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="min-h-[280px] font-mono text-sm"
          />
        )}

        {/* Error */}
        {error && (
          <div className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/20 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Submit */}
        <Button
          onClick={handleSubmit}
          disabled={!canSubmit || isSubmitting}
          className="w-full"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            "Run Analysis"
          )}
        </Button>

        {/* Sample contracts */}
        <div className="flex items-center justify-center gap-4 text-sm">
          <span className="text-slate-400">Try a sample:</span>
          <button
            onClick={() => loadSample(SAMPLE_NDA, "Standard NDA")}
            className="text-violet-600 hover:underline dark:text-violet-400"
          >
            Standard NDA
          </button>
          <button
            onClick={() => loadSample(SAMPLE_SAAS, "SaaS Services Agreement")}
            className="text-violet-600 hover:underline dark:text-violet-400"
          >
            SaaS Agreement
          </button>
        </div>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: Create FileDropZone and SampleContracts stubs**

Create `FileDropZone.tsx` and `SampleContracts.tsx` in `app/submit/` — simple self-contained components that mirror the existing dropzone from `LandingPage.tsx`.

- [ ] **Step 3: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/app/submit/
git commit -m "feat: create SubmissionView with file upload and text paste modes"
```

### Task 2.7: Refactor page.tsx to route between submission and console

**Files:**
- Modify: `contract-analyzer-frontend/src/app/page.tsx`

- [ ] **Step 1: Rewrite page.tsx**

```typescript
"use client";

import { useStore } from "@/stores";
import { ConsoleLayout } from "./console/ConsoleLayout";
import { MainPanel } from "./console/MainPanel";
import { SubmissionView } from "./submit/SubmissionView";
import { AnalysisProgressTracker } from "./progress/AnalysisProgressTracker";
import { LiveTraceOverlay } from "./console/trace/LiveTraceOverlay";

export default function Page() {
  const analysis = useStore((s) => s.analysis);
  const jobStatus = useStore((s) => s.jobStatus);

  // Show progress tracker during async analysis
  if (
    jobStatus === "submitting" ||
    jobStatus === "running"
  ) {
    return (
      <>
        <AnalysisProgressTracker />
        <LiveTraceOverlay />
      </>
    );
  }

  // Show console when analysis is loaded
  if (analysis) {
    return (
      <ConsoleLayout>
        <MainPanel />
      </ConsoleLayout>
    );
  }

  // Default: submission view
  return <SubmissionView />;
}
```

- [ ] **Step 2: Type-check** (will fail on missing components — expected)

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
```

Expected: errors for `AnalysisProgressTracker`, `LiveTraceOverlay` — built in Phases 3 and 4.

- [ ] **Step 3: Commit**

```bash
git add contract-analyzer-frontend/src/app/page.tsx
git commit -m "feat: refactor page.tsx to route between submission, progress, and console views"
```

### Task 2.8: Remove deprecated components

**Files:**
- Remove: `contract-analyzer-frontend/src/components/LandingPage.tsx`
- Remove: `contract-analyzer-frontend/src/components/AnalysisLoadingOverlay.tsx`
- Remove: `contract-analyzer-frontend/src/components/ConsolePage.tsx`
- Remove: `contract-analyzer-frontend/src/hooks/useAnalysis.ts`
- Remove: `contract-analyzer-frontend/src/lib/samples.ts`

- [ ] **Step 1: Remove deprecated files**

```bash
cd contract-analyzer-frontend
rm src/components/LandingPage.tsx
rm src/components/AnalysisLoadingOverlay.tsx
rm src/components/ConsolePage.tsx
rm src/hooks/useAnalysis.ts
rm src/lib/samples.ts
```

- [ ] **Step 2: Fix any import errors**

Search for remaining imports of deleted files:

```bash
grep -r "LandingPage\|AnalysisLoadingOverlay\|ConsolePage\|useAnalysis\|from.*samples" src/ --include="*.ts" --include="*.tsx"
```

Remove or fix any remaining references.

- [ ] **Step 3: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add -A
git commit -m "refactor: remove deprecated components replaced by new architecture"
```

---

## Phase 3: Async Submission + Progress Tracker

### Task 3.1: Wire async submission flow in SubmissionView

**Files:**
- Modify: `contract-analyzer-frontend/src/app/submit/SubmissionView.tsx`

- [ ] **Step 1: Update handleSubmit to use async pipeline**

In `SubmissionView.tsx`, ensure `handleSubmit` calls `submitAsync` (POST to `/analyze/async`) instead of `submitContract`:

```typescript
const handleSubmit = async () => {
  if (!canSubmit) return;
  setIsSubmitting(true);
  setError(null);
  try {
    const submittedName = name || file?.name || "Unnamed Contract";
    const submittedText = mode === "paste" ? text : "(file upload)";
    setInput(submittedName, submittedText, file ?? undefined);
    const job = await submitAsync(submittedName, submittedText, file ?? undefined);
    setSubmitting(job.job_id);
    setJobRunning();
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Submission failed";
    setError(msg);
    toast.error(msg);
    setIsSubmitting(false);
  }
};
```

- [ ] **Step 2: Type-check and commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/app/submit/SubmissionView.tsx
git commit -m "feat: wire async submission flow in SubmissionView"
```

### Task 3.2: Create StageTimeline component

**Files:**
- Create: `contract-analyzer-frontend/src/app/progress/StageTimeline.tsx`

- [ ] **Step 1: Write StageTimeline**

```typescript
"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Circle } from "lucide-react";
import { useStore } from "@/stores";

const STAGES = [
  { key: "parsing", label: "Parsing Contract" },
  { key: "classifying", label: "Classifying Content" },
  { key: "risk_evaluation", label: "Evaluating Risk" },
  { key: "verifying", label: "Verifying Citations" },
  { key: "decision_generation", label: "Generating Decisions" },
  { key: "complete", label: "Finalizing" },
];

export function StageTimeline() {
  const stages = useStore((s) => s.stages);
  const currentStage = useStore((s) => s.currentStage);

  return (
    <div className="space-y-0">
      {STAGES.map((stage, i) => {
        const status = stages[stage.key];
        const isActive = currentStage === stage.key;
        const isLast = i === STAGES.length - 1;
        const isCompleted = status?.status === "completed";
        const isFailed = status?.status === "failed";

        return (
          <div key={stage.key} className="relative flex gap-3">
            {!isLast && (
              <div className="absolute left-[11px] top-6 bottom-0 w-px bg-slate-200 dark:bg-slate-800" />
            )}
            <div className="relative z-10 mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center">
              {isCompleted ? (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                >
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                </motion.div>
              ) : isFailed ? (
                <motion.div
                  initial={{ rotate: 0 }}
                  animate={{ rotate: 360 }}
                  transition={{ duration: 0.4 }}
                >
                  <XCircle className="h-5 w-5 text-red-500" />
                </motion.div>
              ) : isActive ? (
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                >
                  <div className="h-3 w-3 rounded-full bg-violet-500 ring-4 ring-violet-500/20" />
                </motion.div>
              ) : (
                <Circle className="h-3 w-3 text-slate-300 dark:text-slate-700" />
              )}
            </div>
            <div className="py-1">
              <p className={`text-sm font-medium ${
                isActive ? "text-violet-600 dark:text-violet-400"
                : isCompleted ? "text-slate-700 dark:text-slate-300"
                : isFailed ? "text-red-600 dark:text-red-400"
                : "text-slate-400"
              }`}>
                {stage.label}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add contract-analyzer-frontend/src/app/progress/StageTimeline.tsx
git commit -m "feat: create StageTimeline with animated pipeline progress"
```

### Task 3.3: Create StageDetailCard and AnalysisProgressTracker

**Files:**
- Create: `contract-analyzer-frontend/src/app/progress/StageDetailCard.tsx`
- Create: `contract-analyzer-frontend/src/app/progress/AnalysisProgressTracker.tsx`

- [ ] **Step 1: Write StageDetailCard**

```typescript
"use client";

import { useStore } from "@/stores";

const stageMessages: Record<string, string> = {
  parsing: "Extracting clauses, parties, governing law, and contract metadata via AI parsing...",
  classifying: "Scanning for privacy and financial compliance signals to route to specialist agent...",
  risk_evaluation: "Running ReAct agent loop — querying 17 regulatory standards via FAISS + BM25...",
  verifying: "Cross-referencing citations against retrieved evidence — detecting hallucinations...",
  decision_generation: "Generating prioritized recommendations with ownership assignments...",
  complete: "Analysis complete. Loading results...",
};

export function StageDetailCard() {
  const currentStage = useStore((s) => s.currentStage);
  const reaactIterations = useStore((s) => s.reaactIterations);
  const traceEntries = useStore((s) => s.traceEntries);
  const message = currentStage ? (stageMessages[currentStage] ?? "Processing...") : "Initializing...";

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-[#1a1a24]">
      <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p>
      {reaactIterations > 0 && (
        <p className="mt-2 text-xs text-violet-600 dark:text-violet-400">
          ReAct iterations: {reaactIterations}
        </p>
      )}
      {traceEntries.length > 0 && (
        <p className="mt-1 text-xs text-slate-400">Trace events: {traceEntries.length}</p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Write AnalysisProgressTracker**

```typescript
"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { Loader2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { getJobStatus } from "@/lib/api";
import { StageTimeline } from "./StageTimeline";
import { StageDetailCard } from "./StageDetailCard";

export function AnalysisProgressTracker() {
  const jobId = useStore((s) => s.jobId);
  const connect = useStore((s) => s.connect);
  const disconnect = useStore((s) => s.disconnect);
  const clear = useStore((s) => s.clear);
  const cancelJob = useStore((s) => s.cancelJob);
  const stages = useStore((s) => s.stages);
  const loadAnalysis = useStore((s) => s.loadAnalysis);
  const setJobCompleted = useStore((s) => s.setJobCompleted);

  useEffect(() => {
    if (!jobId) return;
    connect(jobId);
    return () => { disconnect(); };
  }, [jobId, connect, disconnect]);

  useEffect(() => {
    if (stages.complete?.status === "completed" && jobId) {
      getJobStatus(jobId).then((job) => {
        if (job.result) {
          loadAnalysis(job.result, job.result.contract_text ?? "");
          setJobCompleted();
        }
      }).catch(() => {});
    }
  }, [stages.complete?.status, jobId, loadAnalysis, setJobCompleted]);

  const handleCancel = () => {
    disconnect();
    clear();
    cancelJob();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-[#0a0a0f]"
    >
      <div className="w-full max-w-lg space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-[#111118]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-violet-500" />
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">Analyzing Contract</h2>
          </div>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleCancel}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <StageTimeline />
        <StageDetailCard />
        <p className="text-center text-xs text-slate-400">This may take a minute. The analysis runs across multiple AI agents.</p>
      </div>
    </motion.div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
cd contract-analyzer-frontend && npx tsc --noEmit
git add contract-analyzer-frontend/src/app/progress/
git commit -m "feat: create SSE-driven AnalysisProgressTracker"
```

---

## Phase 4: Live Agent Trace

### Task 4.1: Create SpecialistBadge

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/trace/SpecialistBadge.tsx`

```typescript
"use client";

import { Shield, TrendingUp, Scale } from "lucide-react";

type Specialist = "privacy" | "financial" | "generalist";

const config: Record<Specialist, { label: string; icon: React.ReactNode }> = {
  privacy: { label: "Privacy Specialist", icon: <Shield className="h-3 w-3" /> },
  financial: { label: "Financial Specialist", icon: <TrendingUp className="h-3 w-3" /> },
  generalist: { label: "Generalist Agent", icon: <Scale className="h-3 w-3" /> },
};

export function SpecialistBadge({ specialist }: { specialist: string }) {
  const cfg = config[specialist as Specialist] ?? config.generalist;
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-violet-500/30 bg-violet-500/10 px-2 py-0.5 text-[11px] font-medium text-violet-700 dark:text-violet-400">
      {cfg.icon}
      {cfg.label}
    </span>
  );
}
```

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/trace/SpecialistBadge.tsx
git commit -m "feat: create SpecialistBadge"
```

### Task 4.2: Create StageNode and LangGraphDAG

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/trace/StageNode.tsx`
- Create: `contract-analyzer-frontend/src/app/console/trace/LangGraphDAG.tsx`

StageNode renders a single pipeline node with status icon (pending/active/completed/failed). LangGraphDAG renders the 6-node pipeline horizontally with arrows.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/trace/
git commit -m "feat: create LangGraphDAG with animated pipeline visualization"
```

### Task 4.3: Create ReActLoopViewer and RetrievalInspector

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/trace/ReActLoopViewer.tsx`
- Create: `contract-analyzer-frontend/src/app/console/trace/RetrievalInspector.tsx`

ReActLoopViewer shows tool call iteration cards with `staggerChildren` Framer Motion animation. RetrievalInspector shows dual-column FAISS (blue) / BM25 (amber) chunks with relevance score bars.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/trace/
git commit -m "feat: create ReActLoopViewer and RetrievalInspector"
```

### Task 4.4: Create LiveTraceOverlay

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/trace/LiveTraceOverlay.tsx`

520px slide-over from the right with the DAG, ReAct viewer, retrieval inspector, and event log. Toggle button appears during analysis.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/trace/LiveTraceOverlay.tsx
git commit -m "feat: create LiveTraceOverlay with full agent trace view"
```

---

## Phase 5: Verification & Citation

### Task 5.1: Create ConfidenceIndicator and CitationIntegrityBadge

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/verification/ConfidenceIndicator.tsx`
- Create: `contract-analyzer-frontend/src/app/console/verification/CitationIntegrityBadge.tsx`

ConfidenceIndicator: horizontal bar 0-100%, color-mapped (red/amber/emerald), animated fill with optional adjusted-confidence sub-bar. CitationIntegrityBadge: pill with icon for verified_clean / verified_with_flags / hallucinated / unsupported / unverified.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/verification/
git commit -m "feat: create ConfidenceIndicator and CitationIntegrityBadge"
```

### Task 5.2: Create VerificationFlagCard and VerificationPanel

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/verification/VerificationFlagCard.tsx`
- Create: `contract-analyzer-frontend/src/app/console/verification/VerificationPanel.tsx`

VerificationFlagCard: severity-colored left-border card with flag type label and detail. VerificationPanel: stats (clean/hallucinated/citations), grouped flag list, click-to-select finding.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/verification/
git commit -m "feat: create VerificationPanel with flag cards and stats"
```

### Task 5.3: Wire verification into InspectorPanel and FindingsTab

**Files:**
- Modify: `contract-analyzer-frontend/src/app/console/InspectorPanel.tsx`
- Modify: `contract-analyzer-frontend/src/app/console/tabs/FindingsTab.tsx`

Replace "finding" placeholder in InspectorPanel with `<VerificationPanel />`. Add `CitationIntegrityBadge` and `ConfidenceIndicator` to each finding card in FindingsTab.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/
git commit -m "feat: wire verification badges and panel into findings and inspector"
```

---

## Phase 6: Escalation Workflow

### Task 6.1: Create ResolutionActions and TicketCard

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/escalation/ResolutionActions.tsx`
- Create: `contract-analyzer-frontend/src/app/console/escalation/TicketCard.tsx`

ResolutionActions: 3-button group (Approve green, Escalate amber, Block red outline) with `onResolve` callback. TicketCard: severity icon, reason text, linked clause, standard chip, resolution buttons. Calls `resolveTicket` API with optimistic update (mark resolved immediately, toast + revert on error).

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/escalation/
git commit -m "feat: create TicketCard with inline resolution workflow"
```

### Task 6.2: Create EscalationPanel and wire into Inspector

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/escalation/EscalationPanel.tsx`
- Modify: `contract-analyzer-frontend/src/app/console/InspectorPanel.tsx`

EscalationPanel: header with pending count, human review required callout, list of unresolved TicketCards. Replace "escalation" placeholder in InspectorPanel.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/
git commit -m "feat: create EscalationPanel and wire into inspector"
```

---

## Phase 7: Enhanced Contract Viewer

### Task 7.1: Create ClauseGutter

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/contract/ClauseGutter.tsx`

Renders a 24px gutter column with 2px color bars per clause type. First line of each clause gets rounded top. Hover widens to 4px. Click selects clause.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/contract/ClauseGutter.tsx
git commit -m "feat: create ClauseGutter with 15 clause-type color indicators"
```

### Task 7.2: Create enhanced ContractViewer

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/contract/ContractViewer.tsx`

Wraps ClauseGutter + line-numbered text display. Toggleable legend showing all 15 clause types. Finding-aware left borders (red for critical, orange for high, amber for medium). Click clause to select. Uses `useStore` selectors.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/contract/ContractViewer.tsx
git commit -m "feat: create enhanced ContractViewer with clause-type gutters"
```

### Task 7.3: Create CrossJurisdictionDiff

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/contract/CrossJurisdictionDiff.tsx`

Dialog modal comparing governing law vs. knowledge base. Left: contract jurisdiction. Right: applicable/excluded standards with reasons from `standards_applicability`. Opened from JurisdictionBar "Compare" button.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/contract/CrossJurisdictionDiff.tsx
git add contract-analyzer-frontend/src/components/JurisdictionBar.tsx
git commit -m "feat: add CrossJurisdictionDiff modal and JurisdictionBar compare button"
```

### Task 7.4: Create InlineFindingsPanel

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/contract/InlineFindingsPanel.tsx`

Shows findings for selected clause. Each finding card includes CitationIntegrityBadge, ConfidenceIndicator, risk badge, category badge, issue description, referenced standards. Wire into InspectorPanel's "clause" view.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/contract/InlineFindingsPanel.tsx
git add contract-analyzer-frontend/src/app/console/InspectorPanel.tsx
git commit -m "feat: create verification-aware InlineFindingsPanel"
```

---

## Phase 8: Export

### Task 8.1: Create ExportDialog and ExportButton

**Files:**
- Create: `contract-analyzer-frontend/src/app/console/export/ExportDialog.tsx`
- Create: `contract-analyzer-frontend/src/app/console/export/ExportButton.tsx`

ExportDialog: checkbox list for sections (summary, findings, recommendations, audit_trail, verification, escalation). CSV export via client-side Blob download. PDF export via `window.print()` with `@media print` stylesheet. ExportButton: dropdown trigger in ConsoleLayout top bar.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/export/
git add contract-analyzer-frontend/src/app/console/ConsoleLayout.tsx
git commit -m "feat: add PDF/CSV export with section selection"
```

---

## Phase 9: Polish

### Task 9.1: Mobile responsive and print styles

**Files:**
- Modify: `contract-analyzer-frontend/src/app/console/ConsoleLayout.tsx`
- Modify: `contract-analyzer-frontend/src/app/globals.css`

Add responsive breakpoints: below `lg` single column, sidebar hidden, inspector as full-screen sheet. Print stylesheet: hide chrome, serif body, grayscale, full-width.

- [ ] **Commit**

```bash
git add contract-analyzer-frontend/src/app/console/ConsoleLayout.tsx contract-analyzer-frontend/src/app/globals.css
git commit -m "feat: add mobile responsive layout and print styles"
```

### Task 9.2: Accessibility and reduced motion

**Files:**
- Modify: various component files

Add `aria-label` to interactive elements. Add `role` attributes to custom components. Add `focus-visible` outline styles. Verify Framer Motion respects `prefers-reduced-motion` (built-in).

- [ ] **Commit**

```bash
git add -A
git commit -m "feat: add ARIA labels, focus-visible styles, reduced motion support"
```

### Task 9.3: Final integration — build and lint

- [ ] **Run build:**

```bash
cd contract-analyzer-frontend && npm run build
```

Expected: successful production build.

- [ ] **Run lint:**

```bash
cd contract-analyzer-frontend && npm run lint
```

Expected: no lint errors.

- [ ] **Fix any issues and commit:**

```bash
git add -A
git commit -m "fix: resolve build and lint issues from integration"
```

---

## Backend Changes Reference

1. **SSE endpoint** `GET /api/v1/jobs/{job_id}/stream` — `JobEventBus` class with per-job `asyncio.Queue`
2. **Enhanced audit trail** — LangGraph nodes append `reaact_iterations`, `tool_calls[]`, `retrieved_chunks[]`, `specialist`, `duration_ms`
3. **Ticket resolution** `POST /api/v1/analyses/{id}/tickets/{tid}/resolve` — body `{ decision }`
4. **Ensure** `verification_report` and `escalation_tickets` serialize in sync and async responses
