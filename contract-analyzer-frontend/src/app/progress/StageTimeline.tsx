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
            {/* Vertical connector line */}
            {!isLast && (
              <div className="absolute left-[11px] top-6 bottom-0 w-px bg-slate-200 dark:bg-slate-800" />
            )}

            {/* Status icon */}
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

            {/* Stage label */}
            <div className="py-1">
              <p
                className={`text-sm font-medium ${
                  isActive
                    ? "text-violet-600 dark:text-violet-400"
                    : isCompleted
                      ? "text-slate-700 dark:text-slate-300"
                      : isFailed
                        ? "text-red-600 dark:text-red-400"
                        : "text-slate-400"
                }`}
              >
                {stage.label}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
