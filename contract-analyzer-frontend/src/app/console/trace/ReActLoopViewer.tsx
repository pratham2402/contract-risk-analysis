"use client";

import { motion, AnimatePresence } from "framer-motion";
import { RefreshCw, Wrench } from "lucide-react";
import { useStore } from "@/stores";
import { formatTime } from "@/lib/utils";

export function ReActLoopViewer() {
  const traceEntries = useStore((s) => s.traceEntries);
  const reaactIterations = useStore((s) => s.reaactIterations);

  if (traceEntries.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-xs text-slate-400">
        Waiting for ReAct loop events...
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <RefreshCw className="h-3.5 w-3.5" />
        <span>
          ReAct Loop — {reaactIterations} iteration
          {reaactIterations !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto">
        <AnimatePresence initial={false}>
          {traceEntries.map((entry, i) => (
            <motion.div
              key={`${entry.timestamp}-${i}`}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ type: "spring", stiffness: 500, damping: 30 }}
              className="rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 p-3"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase">
                    {entry.specialist ?? "Agent"}
                  </span>
                  {entry.reaact_iteration != null && (
                    <span className="text-[10px] text-slate-400">
                      Iter {entry.reaact_iteration}
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-slate-400 tabular-nums">
                  {formatTime(entry.timestamp)}
                </span>
              </div>

              {/* Action */}
              {entry.action && (
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-1.5">
                  {entry.action}
                </p>
              )}

              {/* Tool calls */}
              {entry.tool_calls && entry.tool_calls.length > 0 && (
                <div className="space-y-1">
                  {entry.tool_calls.map((tc, i) => (
                    <div
                      key={`${tc.tool}-${i}`}
                      className="flex items-start gap-1.5 rounded bg-slate-50 dark:bg-slate-800 px-2 py-1.5"
                    >
                      <Wrench className="h-3 w-3 text-violet-500 mt-0.5 shrink-0" />
                      <div className="min-w-0 flex-1">
                        <span className="text-[11px] font-medium text-slate-500">
                          {tc.tool}:
                        </span>
                        <span className="text-[11px] text-slate-600 dark:text-slate-300 ml-1">
                          {tc.input.length > 80 ? tc.input.slice(0, 80) + "..." : tc.input}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Retrieved evidence count */}
              {entry.retrieved_chunks &&
                entry.retrieved_chunks.length > 0 && (
                  <div className="mt-1.5 text-[10px] text-violet-400">
                    +{entry.retrieved_chunks.length} evidence chunks retrieved
                  </div>
                )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
