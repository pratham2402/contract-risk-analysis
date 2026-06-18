"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { StageStatus } from "@/stores/livetrace.slice";

const STAGE_LABELS: Record<string, string> = {
  parsing: "Parse",
  classifying: "Classify",
  risk_evaluation: "Risk Eval",
  verifying: "Verify",
  decision_generation: "Decide",
  complete: "Done",
};

interface StageNodeProps {
  stageKey: string;
  status: StageStatus | undefined;
  isActive: boolean;
  delay?: number;
}

export function StageNode({
  stageKey,
  status,
  isActive,
  delay = 0,
}: StageNodeProps) {
  const label = STAGE_LABELS[stageKey] ?? stageKey;
  const isCompleted = status?.status === "completed";
  const isFailed = status?.status === "failed";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.2 }}
      className="flex flex-col items-center gap-1"
    >
      <div className="relative flex h-9 w-9 items-center justify-center">
        {isCompleted ? (
          <CheckCircle2 className="h-5 w-5 text-emerald-500" />
        ) : isFailed ? (
          <XCircle className="h-5 w-5 text-red-500" />
        ) : isActive ? (
          <Loader2 className="h-5 w-5 animate-spin text-violet-500" />
        ) : (
          <Circle className="h-3 w-3 text-slate-300 dark:text-slate-700" />
        )}
      </div>
      <span
        className={cn(
          "text-[10px] font-medium whitespace-nowrap",
          isActive && "text-violet-600 dark:text-violet-400",
          isCompleted && "text-emerald-600 dark:text-emerald-400",
          isFailed && "text-red-600 dark:text-red-400",
          !isActive && !isCompleted && !isFailed && "text-slate-400"
        )}
      >
        {label}
      </span>

    </motion.div>
  );
}
