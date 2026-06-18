"use client";

import { cn, RISK_COLORS } from "@/lib/utils";
import type { Finding, ParsedClause } from "@/lib/types";
import { riskSeverityScore } from "@/lib/utils";

interface ContractViewerProps {
  contractText: string;
  clauses: ParsedClause[];
  findings: Finding[];
  selectedClauseId: string | null;
  onClauseSelect?: (clauseId: string) => void;
}

export function ContractViewer({
  contractText,
  clauses,
  findings,
  selectedClauseId,
  onClauseSelect,
}: ContractViewerProps) {
  if (!contractText) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-sm text-muted-foreground">
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

  return (
    <div className="p-3 font-mono text-sm leading-7">
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
              clause && "bg-accent/10",
              isSelected && "bg-primary/10 ring-1 ring-primary/30",
              riskStyle && clause && riskStyle.border + " border-l-2",
              clause && onClauseSelect && "cursor-pointer"
            )}
            onClick={() => {
              if (clause && onClauseSelect) {
                onClauseSelect(clause.id);
              }
            }}
          >
            <span className="w-12 shrink-0 text-right pr-3 text-muted-foreground/50 select-none">
              {lineNum}
            </span>
            <span className="flex-1 whitespace-pre-wrap break-all pr-2">
              {line || " "}
            </span>
            {clause && lineNum === clause.start_line && (
              <span className="shrink-0 text-xs text-primary/60 pr-3 self-center">
                §{clause.clause_number || clause.title}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
