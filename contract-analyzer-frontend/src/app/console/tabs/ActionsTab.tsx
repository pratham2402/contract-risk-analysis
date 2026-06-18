"use client";

import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, User, ArrowUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useStore } from "@/stores";
import {
  cn,
  DECISION_COLORS,
  RISK_COLORS,
  OWNER_LABELS,
} from "@/lib/utils";
import type { Finding, Recommendation } from "@/lib/types";

const DECISIONS = ["block", "escalate", "approve"] as const;

export function ActionsTab() {
  const analysis = useStore((s) => s.analysis);
  const view = useStore((s) => s.recommendationsView);
  const setRecommendationsView = useStore((s) => s.setRecommendationsView);

  const recommendations = analysis?.recommendations ?? [];
  const findings = analysis?.findings ?? [];

  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted mb-3">
          <ArrowUp className="h-6 w-6 text-muted-foreground/40" />
        </div>
        <p className="text-sm font-medium">No recommendations</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Nothing actionable found
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3 pt-3">
      {/* View toggle */}
      <div className="flex rounded-md bg-muted p-0.5">
        <button
          className={cn(
            "flex-1 py-1 text-xs font-medium rounded-sm transition-colors",
            view === "decision"
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
          onClick={() => setRecommendationsView("decision")}
        >
          By Decision
        </button>
        <button
          className={cn(
            "flex-1 py-1 text-xs font-medium rounded-sm transition-colors",
            view === "owner"
              ? "bg-card text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          )}
          onClick={() => setRecommendationsView("owner")}
        >
          By Owner
        </button>
      </div>

      {view === "decision" ? (
        <DecisionView recommendations={recommendations} findings={findings} />
      ) : (
        <OwnerView recommendations={recommendations} findings={findings} />
      )}
    </div>
  );
}

function DecisionView({
  recommendations,
  findings,
}: {
  recommendations: Recommendation[];
  findings: Finding[];
}) {
  const grouped = DECISIONS.map((d) => ({
    decision: d,
    items: recommendations.filter((r) => r.decision === d),
  }));

  return (
    <div className="grid grid-cols-3 gap-2">
      {grouped.map(({ decision, items }) => {
        const colors = DECISION_COLORS[decision];
        return (
          <div key={decision} className="space-y-2">
            <div className="flex items-center justify-between">
              <span
                className={cn(
                  "text-xs font-bold uppercase",
                  colors.text
                )}
              >
                {decision}
              </span>
              <span className="text-xs text-muted-foreground">
                {items.length}
              </span>
            </div>
            <AnimatePresence mode="popLayout">
              {items.map((rec, i) => (
                <motion.div
                  key={rec.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: i * 0.03 }}
                >
                  <RecCard rec={rec} findings={findings} compact />
                </motion.div>
              ))}
            </AnimatePresence>
            {items.length === 0 && (
              <p className="text-xs text-muted-foreground/50 italic">
                None
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}

function OwnerView({
  recommendations,
  findings,
}: {
  recommendations: Recommendation[];
  findings: Finding[];
}) {
  const owners = [...new Set(recommendations.map((r) => r.owner))].sort();
  const grouped = owners.map((o) => ({
    owner: o,
    items: recommendations.filter((r) => r.owner === o),
  }));

  return (
    <div className="space-y-3">
      {grouped.map(({ owner, items }, groupIdx) => (
        <motion.div
          key={owner}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: groupIdx * 0.05 }}
        >
          <div className="flex items-center gap-2 mb-2">
            <User className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-xs font-medium">
              {OWNER_LABELS[owner] ?? owner}
            </span>
            <span className="text-xs text-muted-foreground">
              ({items.length})
            </span>
          </div>
          <div className="space-y-2">
            {items.map((rec, i) => (
              <RecCard
                key={rec.id}
                rec={rec}
                findings={findings}
                delay={i * 0.02}
              />
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  );
}

function RecCard({
  rec,
  findings,
  compact,
  delay,
}: {
  rec: Recommendation;
  findings: Finding[];
  compact?: boolean;
  delay?: number;
}) {
  const riskStyle = RISK_COLORS[rec.risk_level];
  const decisionStyle = DECISION_COLORS[rec.decision];
  const linkedFindings = findings.filter((f) => f.id === rec.finding_id);

  return (
    <motion.div
      initial={delay !== undefined ? { opacity: 0, x: 8 } : undefined}
      animate={delay !== undefined ? { opacity: 1, x: 0 } : undefined}
      transition={delay !== undefined ? { delay } : undefined}
      className={cn(
        "rounded-lg border bg-card p-2.5",
        decisionStyle.bg.replace("/50", "/20"),
        "border-l-2",
        riskStyle.border
      )}
    >
      <div className="flex items-center gap-1.5 mb-1.5">
        <Badge
          className={cn(
            "text-[11px] font-bold uppercase px-1.5 py-0 h-4",
            decisionStyle.bg,
            decisionStyle.text
          )}
        >
          {rec.decision}
        </Badge>
        <Badge
          className={cn(
            "text-[11px] uppercase px-1.5 py-0 h-4",
            riskStyle.bg,
            riskStyle.text
          )}
        >
          {rec.risk_level}
        </Badge>
        {!compact && (
          <div className="flex items-center gap-0.5 ml-auto">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  i < rec.priority
                    ? rec.priority <= 2
                      ? "bg-red-500"
                      : rec.priority <= 3
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    : "bg-muted"
                )}
              />
            ))}
          </div>
        )}
      </div>

      <p className="text-xs leading-snug mb-1.5">
        {rec.recommended_action}
      </p>

      {rec.negotiation_suggestion && !compact && (
        <div className="rounded bg-muted/50 px-2 py-1.5 mb-1.5 flex items-start gap-1.5">
          <MessageCircle className="h-3 w-3 text-muted-foreground mt-0.5 shrink-0" />
          <p className="text-xs text-muted-foreground italic leading-relaxed">
            {rec.negotiation_suggestion}
          </p>
        </div>
      )}

      {!compact && (
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          <span className="flex items-center gap-0.5">
            <User className="h-2.5 w-2.5" />
            {OWNER_LABELS[rec.owner] ?? rec.owner}
          </span>
          {linkedFindings.length > 0 && (
            <span>Linked: {linkedFindings.length} findings</span>
          )}
        </div>
      )}
    </motion.div>
  );
}
