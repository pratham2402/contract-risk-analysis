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

/**
 * Placeholder inline findings panel — will be properly implemented
 * when clause-level drill-down is built.
 */
function InlineFindingsPanel({ clauseId }: { clauseId: string }) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold tracking-widest text-slate-400">
        CLAUSE FINDINGS
      </h3>
      <p className="text-sm text-slate-400">
        Findings for clause {clauseId} — in Phase 5
      </p>
    </div>
  );
}
