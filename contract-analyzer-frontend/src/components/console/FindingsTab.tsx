"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, X, Filter, BookOpen, ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  cn,
  RISK_COLORS,
  STANDARD_LABELS,
  CATEGORY_LABELS,
} from "@/lib/utils";
import type { Finding, ParsedClause, RiskLevel } from "@/lib/types";

interface FindingsTabProps {
  findings: Finding[];
  clauses: ParsedClause[];
  filter: {
    riskLevels: RiskLevel[];
    category: string;
    standard: string;
    search: string;
  };
  onFilterChange: (filter: Partial<{
    riskLevels: RiskLevel[];
    category: string;
    standard: string;
    search: string;
  }>) => void;
  onClearFilter: () => void;
  onFindingClick: (clauseId: string | null) => void;
}

const RISK_LEVELS: RiskLevel[] = ["critical", "high", "medium", "low", "info"];

export function FindingsTab({
  findings,
  clauses,
  filter,
  onFilterChange,
  onClearFilter,
  onFindingClick,
}: FindingsTabProps) {
  const [showExcludedFor, setShowExcludedFor] = useState<string | null>(null);

  const categories = [...new Set(findings.map((f) => f.category))].sort();
  const standards = [
    ...new Set(
      findings.flatMap((f) =>
        f.referenced_standards.map((s) => s.standard)
      )
    ),
  ].sort();

  const filtered = findings.filter((f) => {
    if (filter.riskLevels.length && !filter.riskLevels.includes(f.risk_level))
      return false;
    if (filter.category && f.category !== filter.category) return false;
    if (
      filter.standard &&
      !f.referenced_standards.some((s) => s.standard === filter.standard)
    )
      return false;
    if (filter.search) {
      const q = filter.search.toLowerCase();
      if (
        !f.issue_description.toLowerCase().includes(q) &&
        !f.explanation.toLowerCase().includes(q)
      )
        return false;
    }
    return true;
  });

  const hasFilter =
    filter.riskLevels.length > 0 ||
    !!filter.category ||
    !!filter.standard ||
    !!filter.search;

  function getClauseForFinding(finding: Finding): ParsedClause | undefined {
    return finding.clause_id
      ? clauses.find((c) => c.id === finding.clause_id)
      : undefined;
  }

  return (
    <div className="space-y-3 pt-3">
      {/* Filter toolbar */}
      <div className="space-y-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            placeholder="Search findings..."
            value={filter.search}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            className="h-8 pl-7 text-xs"
          />
        </div>

        <div className="flex flex-wrap gap-1">
          {RISK_LEVELS.map((level) => {
            const active = filter.riskLevels.includes(level);
            const style = RISK_COLORS[level];
            return (
              <button
                key={level}
                className={cn(
                  "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium transition-colors border",
                  active
                    ? `${style.bg} ${style.text} ${style.border}`
                    : "border-border text-muted-foreground hover:text-foreground"
                )}
                onClick={() => {
                  const next = filter.riskLevels.includes(level)
                    ? filter.riskLevels.filter((l) => l !== level)
                    : [...filter.riskLevels, level];
                  onFilterChange({ riskLevels: next });
                }}
              >
                {level}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          <select
            className="flex-1 h-7 rounded-md border border-border bg-transparent px-2 text-xs text-muted-foreground"
            value={filter.category}
            onChange={(e) => onFilterChange({ category: e.target.value })}
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {CATEGORY_LABELS[c] ?? c.replace(/_/g, " ")}
              </option>
            ))}
          </select>
          <select
            className="flex-1 h-7 rounded-md border border-border bg-transparent px-2 text-xs text-muted-foreground"
            value={filter.standard}
            onChange={(e) => onFilterChange({ standard: e.target.value })}
          >
            <option value="">All standards</option>
            {standards.map((s) => (
              <option key={s} value={s}>
                {STANDARD_LABELS[s] ?? s}
              </option>
            ))}
          </select>
          {hasFilter && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-muted-foreground"
              onClick={onClearFilter}
            >
              <X className="mr-1 h-3 w-3" />
              Clear
            </Button>
          )}
        </div>

        <p className="text-xs text-muted-foreground">
          Showing {filtered.length} of {findings.length} findings
        </p>
      </div>

      {/* Findings list */}
      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          {findings.length === 0 ? (
            <>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-950/30 mb-3">
                <svg
                  className="h-6 w-6 text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <p className="text-sm font-medium">No findings</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Contract appears compliant
              </p>
            </>
          ) : (
            <p className="text-xs text-muted-foreground">
              No findings match your filters
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <AnimatePresence mode="popLayout">
            {filtered.map((finding, i) => {
              const style = RISK_COLORS[finding.risk_level];
              const clause = getClauseForFinding(finding);
              const visibleStandards = finding.referenced_standards.slice(0, 2);
              const hiddenCount =
                finding.referenced_standards.length - 2;

              return (
                <motion.div
                  key={finding.id}
                  layout
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ delay: i * 0.02 }}
                  className={cn(
                    "rounded-lg border bg-card overflow-hidden",
                    style.border
                  )}
                >
                  <div className="p-3">
                    {/* Header */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <Badge
                          className={cn(
                            "text-[11px] font-bold uppercase px-1.5 py-0 h-4",
                            style.bg,
                            style.text
                          )}
                        >
                          {finding.risk_level}
                        </Badge>
                        <Badge
                          variant="outline"
                          className="text-[11px] px-1.5 py-0 h-4"
                        >
                          {CATEGORY_LABELS[finding.category] ?? finding.category.replace(/_/g, " ")}
                        </Badge>
                      </div>
                    </div>

                    {/* Issue */}
                    <p className="text-xs font-semibold leading-snug mb-2">
                      {finding.issue_description}
                    </p>

                    {/* Standards cited */}
                    {finding.referenced_standards.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1 mb-2">
                        {visibleStandards.map((s) => (
                          <span
                            key={s.standard + (s.article ?? "")}
                            className="inline-flex items-center gap-1 rounded bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground"
                          >
                            <BookOpen className="h-2.5 w-2.5" />
                            {STANDARD_LABELS[s.standard] ?? s.standard}
                            {s.article && (
                              <span className="text-primary/70">
                                {s.article}
                              </span>
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

                    {/* Collapsible sections for Explanation + Reasoning */}
                    <Collapsible className="mt-1">
                      <CollapsibleTrigger className="flex items-center gap-1 py-1 text-xs text-muted-foreground hover:text-foreground">
                        <ChevronDown className="h-3 w-3 transition-transform group-data-[open]:rotate-180" />
                        Explanation
                      </CollapsibleTrigger>
                      <CollapsibleContent className="pb-1">
                        <p className="text-xs text-muted-foreground leading-relaxed">
                          {finding.explanation}
                        </p>
                      </CollapsibleContent>
                    </Collapsible>
                    <Collapsible>
                      <CollapsibleTrigger className="flex items-center gap-1 py-1 text-xs text-muted-foreground hover:text-foreground">
                        <ChevronDown className="h-3 w-3 transition-transform group-data-[open]:rotate-180" />
                        Reasoning Trace
                      </CollapsibleTrigger>
                      <CollapsibleContent className="pb-1">
                        <p className="text-xs text-muted-foreground leading-relaxed font-mono">
                          {finding.reasoning_trace}
                        </p>
                      </CollapsibleContent>
                    </Collapsible>

                    {/* Footer */}
                    <div className="mt-2 flex items-center gap-3">
                      <span className="text-[11px] text-muted-foreground">
                        {finding.referenced_standards.length} standard{finding.referenced_standards.length !== 1 ? "s" : ""} cited
                      </span>
                      {clause && (
                        <button
                          className="text-xs text-primary hover:underline shrink-0 ml-auto"
                          onClick={() =>
                            onFindingClick(finding.clause_id)
                          }
                        >
                          §{clause.clause_number || clause.title}
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
