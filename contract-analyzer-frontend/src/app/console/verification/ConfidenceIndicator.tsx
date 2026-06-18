"use client";

import { motion } from "framer-motion";
import { cn, confidenceColor } from "@/lib/utils";

interface ConfidenceIndicatorProps {
  confidence: number;
  adjustedConfidence?: number | null;
  className?: string;
}

export function ConfidenceIndicator({
  confidence,
  adjustedConfidence,
  className,
}: ConfidenceIndicatorProps) {
  const pct = Math.round(confidence * 100);
  const adjPct =
    adjustedConfidence != null ? Math.round(adjustedConfidence * 100) : null;

  return (
    <div className={cn("space-y-1", className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Confidence</span>
        <span className={cn("font-semibold tabular-nums", confidenceColor(confidence))}>
          {pct}%
        </span>
      </div>
      <div className="relative h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className={cn(
            "h-full rounded-full",
            confidence >= 0.8
              ? "bg-emerald-500"
              : confidence >= 0.6
                ? "bg-amber-500"
                : "bg-red-500"
          )}
        />
        {adjPct != null && adjPct !== pct && (
          <div
            className="absolute top-0 h-full w-0.5 bg-slate-800 dark:bg-white"
            style={{ left: `${adjPct}%` }}
            title={`Adjusted: ${adjPct}%`}
          />
        )}
      </div>
      {adjPct != null && adjPct !== pct && (
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-muted-foreground">After verification</span>
          <span className={cn("font-medium tabular-nums", confidenceColor(adjustedConfidence!))}>
            {adjPct}%
          </span>
        </div>
      )}
    </div>
  );
}
