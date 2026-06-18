"use client";

import { useState } from "react";
import { cn, RISK_COLORS, CLAUSE_TYPE_LABELS } from "@/lib/utils";
import { useStore } from "@/stores";
import type { Finding, ParsedClause } from "@/lib/types";
import { riskSeverityScore } from "@/lib/utils";
import { ClauseGutter } from "./ClauseGutter";

export function ContractViewer() {
  const analysis = useStore((s) => s.analysis);
  const contractText = useStore((s) => s.contractText);
  const selectedClauseId = useStore((s) => s.selectedClauseId);
  const selectClause = useStore((s) => s.selectClause);

  const [showLegend, setShowLegend] = useState(false);

  const clauses = analysis?.clauses ?? [];
  const findings = analysis?.findings ?? [];

  if (!contractText) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-sm text-slate-400">
          Submit a contract to view analysis
        </p>
      </div>
    );
  }

  const lines = contractText.split("\n");
  const lineMap = new Map<number, ParsedClause>();
  const findingMap = new Map<number, Finding[]>();

  for (const clause of clauses) {
    for (let i = clause.start_line; i <= clause.end_line; i++) {
      lineMap.set(i, clause);
    }
  }

  for (const finding of findings) {
    if (finding.clause_id) {
      const clause = clauses.find((c) => c.id === finding.clause_id);
      if (clause) {
        for (let i = clause.start_line; i <= clause.end_line; i++) {
          const existing = findingMap.get(i) || [];
          existing.push(finding);
          findingMap.set(i, existing);
        }
      }
    }
  }

  const hasClauses = clauses.length > 0;

  return (
    <div className="flex flex-col h-full">
      {/* Clause type legend toggle */}
      {hasClauses && (
        <div className="shrink-0 border-b border-slate-200 dark:border-slate-800 px-3 py-1.5">
          <button
            onClick={() => setShowLegend(!showLegend)}
            className="text-[11px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >
            {showLegend ? "Hide" : "Show"} clause type legend
          </button>
          {showLegend && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {Object.entries(CLAUSE_TYPE_LABELS).map(([key, label]) => (
                <span
                  key={key}
                  className={cn(
                    "inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[10px]",
                    "border-l-[3px]",
                    `border-l-${getLegacyColor(key)}-500`,
                    "bg-slate-50 dark:bg-slate-800/50 text-slate-600 dark:text-slate-300"
                  )}
                >
                  {label}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Scrollable text area */}
      <div className="flex-1 overflow-y-auto">
        <div className={cn("font-mono text-sm leading-7", !hasClauses && "p-3")}>
          {lines.map((line, idx) => {
            const lineNum = idx + 1;
            const clause = lineMap.get(lineNum);
            const lineFindings = findingMap.get(lineNum);
            const isSelected = clause && clause.id === selectedClauseId;
            const worstRisk = lineFindings?.reduce((worst, f) => {
              const current = riskSeverityScore(f.risk_level);
              const prev = riskSeverityScore(worst);
              return current > prev ? f.risk_level : worst;
            }, "info" as Finding["risk_level"]);
            const riskStyle = worstRisk ? RISK_COLORS[worstRisk] : null;

            return (
              <div
                key={lineNum}
                className={cn(
                  "flex hover:bg-accent/30 transition-colors",
                  clause && "bg-accent/5",
                  isSelected && "bg-primary/10 ring-1 ring-primary/30",
                  clause && "cursor-pointer"
                )}
                onClick={() => {
                  if (clause) selectClause(clause.id);
                }}
              >
                {/* Clause type gutter */}
                {hasClauses && (
                  <ClauseGutter
                    clause={clause ?? { clause_type: "other", title: "" } as ParsedClause}
                    isSelected={!!isSelected}
                  />
                )}

                {/* Line number */}
                <span className="w-12 shrink-0 text-right pr-3 text-slate-400/50 select-none text-xs">
                  {lineNum}
                </span>

                {/* Text line */}
                <span
                  className={cn(
                    "flex-1 whitespace-pre-wrap break-all pr-2",
                    riskStyle && clause && riskStyle.border && "border-l-2"
                  )}
                >
                  {line || " "}
                </span>

                {/* Clause marker */}
                {clause && lineNum === clause.start_line && (
                  <span className="shrink-0 text-xs text-violet-500 pr-3 self-center">
                    §{clause.clause_number || clause.title}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/** Helper to return legacy Tailwind color for the legend */
function getLegacyColor(clauseType: string): string {
  const map: Record<string, string> = {
    liability: "red",
    indemnification: "orange",
    data_protection: "blue",
    termination: "rose",
    payment: "emerald",
    confidentiality: "violet",
    ip_rights: "purple",
    service_level: "cyan",
    force_majeure: "amber",
    governing_law: "indigo",
    insurance: "green",
    warranty: "teal",
    audit_rights: "sky",
    subcontracting: "slate",
    other: "gray",
  };
  return map[clauseType] ?? "gray";
}
