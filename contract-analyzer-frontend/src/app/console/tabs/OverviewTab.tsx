"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  Shield,
  Clock,
  ChevronDown,
  BookOpen,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ContractViewer } from "@/components/console/ContractViewer";
import { useStore } from "@/stores";
import {
  cn,
  RISK_COLORS,
  STANDARD_LABELS,
  CATEGORY_LABELS,
  formatDuration,
} from "@/lib/utils";
import { riskSeverityScore } from "@/lib/utils";
import type { Finding, ParsedClause } from "@/lib/types";

export function OverviewTab() {
  const analysis = useStore((s) => s.analysis);
  const contractText = useStore((s) => s.contractText);
  const selectedClauseId = useStore((s) => s.selectedClauseId);
  const selectClause = useStore((s) => s.selectClause);

  const [localClauseId, setLocalClauseId] = useState<string | null>(null);

  const effectiveClauseId = selectedClauseId ?? localClauseId;

  if (!analysis) return null;

  const criticalHigh = analysis.findings.filter(
    (f) => f.risk_level === "critical" || f.risk_level === "high"
  ).length;

  const total = analysis.summary.total_findings || 1;

  const selectedClause = effectiveClauseId
    ? analysis.clauses.find((c) => c.id === effectiveClauseId)
    : null;

  const clauseFindings = selectedClause
    ? analysis.findings.filter((f) => f.clause_id === selectedClause.id)
    : [];

  const handleClauseSelect = (id: string) => {
    selectClause(id);
    setLocalClauseId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="flex flex-col h-full">
      {/* Top section: stat cards + risk bar */}
      <div className="shrink-0 p-4 pb-0 space-y-3">
        {/* Stat cards */}
        <div className="grid grid-cols-3 gap-3">
          <StatCard
            label="Total Findings"
            value={analysis.summary.total_findings}
            icon={<AlertTriangle className="h-4 w-4" />}
            delay={0}
          />
          <StatCard
            label="Critical / High"
            value={criticalHigh}
            icon={<Shield className="h-4 w-4" />}
            delay={0.05}
            accent="destructive"
          />
          <StatCard
            label="Duration"
            value={formatDuration(analysis.total_duration_ms)}
            icon={<Clock className="h-4 w-4" />}
            delay={0.1}
            isString
          />
        </div>

        {/* Compact distribution bar */}
        <div>
          <div className="flex h-2 rounded-full overflow-hidden">
            {(["critical", "high", "medium", "low", "info"] as const).map(
              (level) => {
                const count = analysis.summary.risk_counts[level] ?? 0;
                const pct = (count / total) * 100;
                if (pct === 0) return null;
                return (
                  <motion.div
                    key={level}
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className={cn(
                      "h-full",
                      level === "critical" && "bg-red-500",
                      level === "high" && "bg-orange-500",
                      level === "medium" && "bg-amber-500",
                      level === "low" && "bg-sky-500",
                      level === "info" && "bg-slate-500"
                    )}
                  />
                );
              }
            )}
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            {analysis.summary.total_clauses} clauses &middot;{" "}
            {analysis.summary.total_recommendations} actions &middot;{" "}
            Click a clause below to see its findings
          </p>
        </div>
      </div>

      {/* Contract viewer + inline findings */}
      <div className="flex-1 flex flex-col overflow-hidden mt-3 border-t border-border">
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <ContractViewer
              contractText={contractText}
              clauses={analysis.clauses}
              findings={analysis.findings}
              selectedClauseId={effectiveClauseId}
              onClauseSelect={handleClauseSelect}
            />
          </ScrollArea>
        </div>

        {/* Inline findings panel */}
        <AnimatePresence>
          {selectedClause && clauseFindings.length > 0 && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="shrink-0 border-t border-border bg-card/50 overflow-hidden"
            >
              <div className="p-3">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="text-xs font-semibold">
                    &sect;{selectedClause.clause_number || selectedClause.title}
                  </h4>
                  <span className="text-xs text-muted-foreground">
                    {selectedClause.title}
                  </span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {clauseFindings.length} finding{clauseFindings.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <div className="space-y-2 max-h-64 overflow-auto">
                  {clauseFindings.map((finding) => (
                    <InlineFindingCard key={finding.id} finding={finding} />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function InlineFindingCard({ finding }: { finding: Finding }) {
  const style = RISK_COLORS[finding.risk_level];
  const visibleStandards = finding.referenced_standards.slice(0, 2);
  const hiddenCount = finding.referenced_standards.length - 2;

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn("rounded-md border p-2.5", style.border)}
    >
      <div className="flex items-center gap-1.5 mb-1.5">
        <Badge
          className={cn(
            "text-[11px] font-bold uppercase px-1.5 py-0 h-4",
            style.bg,
            style.text
          )}
        >
          {finding.risk_level}
        </Badge>
        <Badge variant="outline" className="text-[11px] px-1.5 py-0 h-4">
          {CATEGORY_LABELS[finding.category] ?? finding.category.replace(/_/g, " ")}
        </Badge>
      </div>
      <p className="text-xs leading-snug mb-1.5">{finding.issue_description}</p>

      {finding.referenced_standards.length > 0 && (
        <div className="flex flex-wrap items-center gap-1 mb-1.5">
          {visibleStandards.map((s) => (
            <span
              key={s.standard + (s.article ?? "")}
              className="inline-flex items-center gap-1 rounded bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground"
            >
              <BookOpen className="h-2.5 w-2.5" />
              {STANDARD_LABELS[s.standard] ?? s.standard}
              {s.article && (
                <span className="text-primary/70">{s.article}</span>
              )}
            </span>
          ))}
          {hiddenCount > 0 && (
            <span className="text-[11px] text-muted-foreground">
              +{hiddenCount} more
            </span>
          )}
        </div>
      )}

      <Collapsible>
        <CollapsibleTrigger className="flex items-center gap-1 py-0.5 text-xs text-muted-foreground hover:text-foreground">
          <ChevronDown className="h-3 w-3 transition-transform group-data-[open]:rotate-180" />
          Explanation
        </CollapsibleTrigger>
        <CollapsibleContent>
          <p className="text-xs text-muted-foreground leading-relaxed pb-1">
            {finding.explanation}
          </p>
        </CollapsibleContent>
      </Collapsible>
    </motion.div>
  );
}

function StatCard({
  label,
  value,
  icon,
  delay,
  accent,
  isString,
}: {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  delay: number;
  accent?: string;
  isString?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.2 }}
    >
      <Card
        className={cn(
          "border-border",
          accent === "destructive" && "border-red-500/30",
          accent === "orange" && "border-orange-500/30"
        )}
      >
        <CardContent className="p-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground uppercase tracking-wider">
              {label}
            </span>
            <span className="text-muted-foreground/50">{icon}</span>
          </div>
          <span
            className={cn(
              "text-lg font-bold tabular-nums",
              typeof value === "number" &&
                value > 0 &&
                accent === "destructive" &&
                "text-red-400",
              typeof value === "number" &&
                value > 0 &&
                accent === "orange" &&
                "text-orange-400"
            )}
          >
            {value}
          </span>
        </CardContent>
      </Card>
    </motion.div>
  );
}
