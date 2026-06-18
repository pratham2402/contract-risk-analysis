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

  const message = currentStage
    ? (stageMessages[currentStage] ?? "Processing...")
    : "Initializing...";

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-[#1a1a24]">
      <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p>
      {reaactIterations > 0 && (
        <p className="mt-2 text-xs text-violet-600 dark:text-violet-400">
          ReAct iterations: {reaactIterations}
        </p>
      )}
      {traceEntries.length > 0 && (
        <p className="mt-1 text-xs text-slate-400">
          Trace events: {traceEntries.length}
        </p>
      )}
    </div>
  );
}
