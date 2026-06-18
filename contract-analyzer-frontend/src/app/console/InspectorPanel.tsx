"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, AlertTriangle, FileSearch } from "lucide-react";
import { useStore } from "@/stores";
import type { InspectorView } from "@/stores/analysis.slice";
import { VerificationPanel } from "./verification/VerificationPanel";
import { ConfidenceIndicator } from "./verification/ConfidenceIndicator";
import { CitationIntegrityBadge } from "./verification/CitationIntegrityBadge";
import { RISK_COLORS, STANDARD_LABELS, CATEGORY_LABELS, cn } from "@/lib/utils";
import { EscalationPanel } from "./escalation/EscalationPanel";

export function InspectorPanel() {
  const analysis = useStore((s) => s.analysis);
  const selectedClauseId = useStore((s) => s.selectedClauseId);
  const selectedFindingId = useStore((s) => s.selectedFindingId);

  const inspectorView: InspectorView = useMemo(() => {
    if (selectedFindingId) return "finding";
    if (selectedClauseId) return "clause";
    if (analysis?.escalation_tickets?.some((t) => !t.resolved))
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
    <div className="h-full overflow-y-auto">
      <motion.div
        key={inspectorView}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {inspectorView === "summary" && <SummaryCard />}
        {inspectorView === "clause" && (
          <InlineFindingsPanel clauseId={selectedClauseId!} />
        )}
        {inspectorView === "finding" && (
          <FindingDetailPanel findingId={selectedFindingId!} />
        )}
        {inspectorView === "escalation" && <EscalationPanel />}
      </motion.div>
    </div>
  );
}

/** Summary view: stats grid + verification banner */
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
    <div className="space-y-4 p-4">
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

      {/* Verification report summary banner */}
      {vrf && (
        <div className="flex items-center justify-between rounded-lg border border-slate-200 dark:border-slate-800 p-3">
          <CitationIntegrityBadge report={vrf} />
          <span className="text-xs text-slate-400 tabular-nums">
            {vrf.total_citations} citations
          </span>
        </div>
      )}

      {hallucinations > 0 && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 dark:border-red-900 dark:bg-red-950/20">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">
            {hallucinations} hallucinated citation
            {hallucinations > 1 ? "s" : ""} detected
          </p>
          <p className="mt-1 text-xs text-red-600 dark:text-red-500">
            These findings cite standards that do not contain the claimed text.
          </p>
        </div>
      )}

      {unresolvedTickets > 0 && (
        <div className="rounded-md border border-rose-200 bg-rose-50 p-3 dark:border-rose-900 dark:bg-rose-950/20">
          <p className="text-sm font-medium text-rose-700 dark:text-rose-400">
            {unresolvedTickets} unresolved escalation ticket
            {unresolvedTickets > 1 ? "s" : ""}
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

/** Finding detail: shows full finding info + confidence */
function FindingDetailPanel({ findingId }: { findingId: string }) {
  const analysis = useStore((s) => s.analysis);
  const finding = analysis?.findings.find((f) => f.id === findingId);

  if (!finding) {
    return (
      <div className="p-4 text-center text-sm text-slate-400">
        Finding not found
      </div>
    );
  }

  const style = RISK_COLORS[finding.risk_level];

  return (
    <div className="space-y-4 p-4">
      <h3 className="text-xs font-semibold tracking-widest text-slate-400">
        FINDING DETAIL
      </h3>

      <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1a1a24] p-3 space-y-3">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span
            className={cn(
              "text-[11px] font-bold uppercase rounded-full px-2 py-0.5",
              style.bg,
              style.text
            )}
          >
            {finding.risk_level}
          </span>
          <span className="text-[11px] text-slate-500 rounded-full border border-slate-200 px-2 py-0.5 dark:border-slate-700">
            {CATEGORY_LABELS[finding.category] ?? finding.category}
          </span>
        </div>

        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-snug">
          {finding.issue_description}
        </p>

        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          {finding.explanation}
        </p>

        {/* Confidence */}
        {finding.confidence != null && (
          <ConfidenceIndicator
            confidence={finding.confidence}
            adjustedConfidence={analysis?.verification_report?.adjusted_confidence ?? null}
          />
        )}

        {/* Referenced standards */}
        {finding.referenced_standards.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-[10px] font-semibold text-slate-400">
              REFERENCED STANDARDS
            </span>
            <div className="flex flex-wrap gap-1">
              {finding.referenced_standards.map((s, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[11px] text-slate-600 dark:text-slate-300"
                >
                  {STANDARD_LABELS[s.standard] ?? s.standard}
                  {s.article && (
                    <span className="text-violet-500">{s.article}</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Reasoning trace */}
        {finding.reasoning_trace && (
          <div className="space-y-1.5">
            <span className="text-[10px] font-semibold text-slate-400">
              REASONING TRACE
            </span>
            <p className="text-xs text-slate-500 font-mono leading-relaxed">
              {finding.reasoning_trace}
            </p>
          </div>
        )}
      </div>

      {/* Verification panel below finding detail */}
      <VerificationPanel />
    </div>
  );
}

/** Clause-level findings list */
function InlineFindingsPanel({ clauseId }: { clauseId: string }) {
  const analysis = useStore((s) => s.analysis);
  const selectFinding = useStore((s) => s.selectFinding);

  const clause = analysis?.clauses.find((c) => c.id === clauseId);
  const clauseFindings =
    analysis?.findings.filter((f) => f.clause_id === clauseId) ?? [];

  return (
    <div className="space-y-3 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold tracking-widest text-slate-400">
          CLAUSE FINDINGS
        </h3>
        <span className="text-[11px] text-slate-400 tabular-nums">
          {clauseFindings.length} finding
          {clauseFindings.length !== 1 ? "s" : ""}
        </span>
      </div>

      {clause && (
        <p className="text-sm text-slate-700 dark:text-slate-300 font-medium">
          &sect;{clause.clause_number ?? clause.title} — {clause.title}
        </p>
      )}

      {clauseFindings.length === 0 ? (
        <p className="text-sm text-slate-400">No findings for this clause</p>
      ) : (
        <div className="space-y-2">
          {clauseFindings.map((finding, i) => {
            const style = RISK_COLORS[finding.risk_level];

            return (
              <motion.button
                key={finding.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() => selectFinding(finding.id)}
                className={cn(
                  "w-full text-left rounded-lg border p-2.5 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50",
                  style.border
                )}
              >
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span
                    className={cn(
                      "text-[11px] font-bold uppercase rounded-full px-1.5 py-0",
                      style.bg,
                      style.text
                    )}
                  >
                    {finding.risk_level}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {CATEGORY_LABELS[finding.category] ?? finding.category}
                  </span>
                </div>
                <p className="text-xs leading-snug text-slate-700 dark:text-slate-300 line-clamp-3">
                  {finding.issue_description}
                </p>
                {finding.confidence != null && (
                  <div className="mt-2">
                    <ConfidenceIndicator
                      confidence={finding.confidence}
                      className="!space-y-0.5"
                    />
                  </div>
                )}
              </motion.button>
            );
          })}
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
