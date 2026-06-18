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
