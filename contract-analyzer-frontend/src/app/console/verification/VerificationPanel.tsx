"use client";

import { motion } from "framer-motion";
import { FileCheck, AlertTriangle, ShieldAlert, Quote } from "lucide-react";
import { useStore } from "@/stores";
import { cn } from "@/lib/utils";
import { CitationIntegrityBadge } from "./CitationIntegrityBadge";
import { VerificationFlagCard } from "./VerificationFlagCard";

export function VerificationPanel() {
  const analysis = useStore((s) => s.analysis);
  const selectFinding = useStore((s) => s.selectFinding);

  const report = analysis?.verification_report;

  if (!report) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center px-4">
        <FileCheck className="h-8 w-8 text-slate-300 dark:text-slate-600 mb-3" />
        <p className="text-sm font-medium text-slate-500">
          No verification data
        </p>
        <p className="mt-1 text-xs text-slate-400">
          Verification report not available for this analysis
        </p>
      </div>
    );
  }

  const cleanCount = report.total_findings - report.flags.length - report.hallucination_count;

  return (
    <div className="space-y-4 p-4">
      {/* Integrity badge */}
      <div className="flex items-center justify-between">
        <CitationIntegrityBadge report={report} />
        <span className="text-xs text-slate-400 tabular-nums">
          {report.total_citations} citations
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-2">
        <StatTile
          label="Clean"
          value={cleanCount}
          color="emerald"
          icon={<FileCheck className="h-3.5 w-3.5" />}
          delay={0}
        />
        <StatTile
          label="Flagged"
          value={report.flags.length}
          color="amber"
          icon={<AlertTriangle className="h-3.5 w-3.5" />}
          delay={0.05}
        />
        <StatTile
          label="Hallucinated"
          value={report.hallucination_count}
          color="red"
          icon={<ShieldAlert className="h-3.5 w-3.5" />}
          delay={0.1}
        />
      </div>

      {/* Confidence */}
      <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-muted-foreground">Confidence</span>
          <span className="text-xs font-semibold tabular-nums text-slate-700 dark:text-slate-300">
            {report.adjusted_confidence != null
              ? `${Math.round(report.adjusted_confidence * 100)}%`
              : "N/A"}
          </span>
        </div>
        {report.adjusted_confidence != null && (
          <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.round(report.adjusted_confidence * 100)}%` }}
              transition={{ duration: 0.6 }}
              className={cn(
                "h-full rounded-full",
                report.adjusted_confidence >= 0.8
                  ? "bg-emerald-500"
                  : report.adjusted_confidence >= 0.6
                    ? "bg-amber-500"
                    : "bg-red-500"
              )}
            />
          </div>
        )}
      </div>

      {/* Flag list */}
      {report.flags.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Quote className="h-3.5 w-3.5" />
            <span>Verification Flags ({report.flags.length})</span>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {report.flags.map((flag, i) => (
              <motion.div
                key={`${flag.finding_id}-${i}`}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <VerificationFlagCard
                  flag={flag}
                  onFindingClick={selectFinding}
                />
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatTile({
  label,
  value,
  color,
  icon,
  delay,
}: {
  label: string;
  value: number;
  color: "emerald" | "amber" | "red";
  icon: React.ReactNode;
  delay: number;
}) {
  const colorMap = {
    emerald: "border-emerald-500/20 bg-emerald-50 dark:bg-emerald-950/10",
    amber: "border-amber-500/20 bg-amber-50 dark:bg-amber-950/10",
    red: "border-red-500/20 bg-red-50 dark:bg-red-950/10",
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      className={cn("rounded-lg border p-2.5 text-center", colorMap[color])}
    >
      <span className="text-xs text-slate-500 dark:text-slate-400">{icon}</span>
      <p className="mt-0.5 text-lg font-bold tabular-nums text-slate-800 dark:text-slate-200">
        {value}
      </p>
      <p className="text-[10px] text-slate-500 dark:text-slate-400">{label}</p>
    </motion.div>
  );
}
