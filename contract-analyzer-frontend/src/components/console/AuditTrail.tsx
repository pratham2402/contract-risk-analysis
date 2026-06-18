"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Clock, ChevronDown, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn, formatTime, formatDuration } from "@/lib/utils";
import type { AuditTrailEntry } from "@/lib/types";

interface AuditTrailProps {
  auditTrail: AuditTrailEntry[];
  totalDurationMs: number;
}

const STAGE_LABELS: Record<string, string> = {
  init: "Initialize",
  contract_parsing: "Contract Parsing",
  risk_evaluation: "Risk Evaluation",
  decision_generation: "Decision Generation",
  finalize: "Finalize",
  error: "Error",
};

export function AuditTrail({ auditTrail, totalDurationMs }: AuditTrailProps) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? auditTrail : auditTrail.slice(-3);

  if (auditTrail.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <p className="text-xs text-muted-foreground">No audit trail available</p>
      </div>
    );
  }

  return (
    <div className="p-3 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2 shrink-0">
        <div className="flex items-center gap-2">
          <Clock className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
            Audit Trail
          </span>
        </div>
        <span className="text-xs text-muted-foreground tabular-nums">
          {formatDuration(totalDurationMs)}
        </span>
      </div>

      <div className="flex-1 space-y-1 overflow-hidden">
        <AnimatePresence initial={false}>
          {visible.map((entry, i) => {
            const isError =
              entry.errors && entry.errors.length > 0;
            const isLast = i === visible.length - 1;

            return (
              <motion.div
                key={`${entry.timestamp}-${entry.stage}`}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className={cn(
                  "flex items-start gap-2 text-xs",
                  isError && "text-red-400"
                )}
              >
                {/* Timeline dot + line */}
                <div className="flex flex-col items-center pt-0.5">
                  <div
                    className={cn(
                      "h-2 w-2 rounded-full",
                      isError ? "bg-red-500" : "bg-primary/60"
                    )}
                  />
                  {!isLast && (
                    <div className="w-px flex-1 min-h-[8px] bg-border mt-0.5" />
                  )}
                </div>

                <div className="flex-1 min-w-0 pb-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-muted-foreground font-mono tabular-nums">
                      {formatTime(entry.timestamp)}
                    </span>
                    <span
                      className={cn(
                        "text-xs font-medium px-1.5 py-0 rounded",
                        isError
                          ? "bg-red-950/50 text-red-400"
                          : "bg-accent text-accent-foreground"
                      )}
                    >
                      {STAGE_LABELS[entry.stage] ?? entry.stage}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {entry.action.replace(/_/g, " ")}
                    </span>
                  </div>

                  <div className="mt-0.5 flex items-center gap-3 text-xs text-muted-foreground">
                    {entry.clause_count !== undefined && (
                      <span>Clauses: {entry.clause_count}</span>
                    )}
                    {entry.finding_count !== undefined && (
                      <span>Findings: {entry.finding_count}</span>
                    )}
                    {entry.recommendation_count !== undefined && (
                      <span>Recs: {entry.recommendation_count}</span>
                    )}
                    {entry.standards_consulted !== undefined && (
                      <span>Standards: {entry.standards_consulted}</span>
                    )}
                  </div>

                  {isError && entry.errors && (
                    <div className="mt-1 flex items-start gap-1">
                      <AlertCircle className="h-3 w-3 text-red-400 shrink-0 mt-0.5" />
                      <span className="text-xs text-red-400">
                        {entry.errors.join("; ")}
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {auditTrail.length > 3 && (
        <Button
          variant="ghost"
          size="sm"
          className="mt-1 h-6 text-xs text-muted-foreground w-full shrink-0"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Show less" : `Show full trace (${auditTrail.length} steps)`}
          <ChevronDown
            className={cn(
              "ml-1 h-3 w-3 transition-transform",
              expanded && "rotate-180"
            )}
          />
        </Button>
      )}
    </div>
  );
}
