"use client";

import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useStore } from "@/stores";

const STAGE_LABELS: Record<string, string> = {
  parsing: "Parsing Contract",
  classifying: "Classifying Clauses",
  risk_evaluation: "Evaluating Risk",
  verifying: "Verifying Citations",
  decision_generation: "Generating Decisions",
  complete: "Complete",
};

const STAGE_ORDER = [
  "parsing",
  "classifying",
  "risk_evaluation",
  "verifying",
  "decision_generation",
  "complete",
];

/** Placeholder — will be fully built in Phase 3 */
export function AnalysisProgressTracker() {
  const stages = useStore((s) => s.stages);
  const jobStatus = useStore((s) => s.jobStatus);

  const entries = STAGE_ORDER.map((key) => {
    const stage = stages[key];
    return {
      stage: key,
      status: stage?.status ?? "pending",
    };
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 dark:bg-[#0a0a0f]">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-[#111118]"
      >
        <div className="text-center space-y-2">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-violet-500" />
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">
            Analyzing Contract
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Multi-agent pipeline in progress — this may take a minute
          </p>
        </div>

        <div className="space-y-3">
          {entries.map((entry, i) => {
            const label = STAGE_LABELS[entry.stage] ?? entry.stage;
            const isActive = entry.status === "active";
            const isDone = entry.status === "completed";
            const isFailed = entry.status === "failed";

            return (
              <motion.div
                key={entry.stage}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex items-center gap-3"
              >
                <div
                  className={`h-2.5 w-2.5 rounded-full shrink-0 ${
                    isFailed
                      ? "bg-red-500"
                      : isDone
                        ? "bg-emerald-500"
                        : isActive
                          ? "bg-violet-500 animate-pulse"
                          : "bg-slate-300 dark:bg-slate-600"
                  }`}
                />
                <span
                  className={`text-sm ${
                    isActive
                      ? "text-slate-800 font-medium dark:text-slate-200"
                      : isDone
                        ? "text-slate-500 dark:text-slate-400"
                        : isFailed
                          ? "text-red-500"
                          : "text-slate-400 dark:text-slate-500"
                  }`}
                >
                  {label}
                </span>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
