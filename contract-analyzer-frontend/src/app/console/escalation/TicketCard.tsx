"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, ShieldAlert, AlertCircle, Info, Clock, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useStore } from "@/stores";
import { resolveTicket } from "@/lib/api";
import { cn, STANDARD_LABELS, formatTime } from "@/lib/utils";
import { ResolutionActions, type ResolutionDecision } from "./ResolutionActions";
import type { EscalationTicket } from "@/lib/types";
import { toast } from "sonner";

const severityConfig: Record<
  string,
  { icon: React.ReactNode; bg: string; text: string }
> = {
  critical: {
    icon: <ShieldAlert className="h-3.5 w-3.5" />,
    bg: "bg-red-50 dark:bg-red-950/20",
    text: "text-red-600 dark:text-red-400",
  },
  high: {
    icon: <AlertTriangle className="h-3.5 w-3.5" />,
    bg: "bg-orange-50 dark:bg-orange-950/20",
    text: "text-orange-600 dark:text-orange-400",
  },
  medium: {
    icon: <AlertCircle className="h-3.5 w-3.5" />,
    bg: "bg-amber-50 dark:bg-amber-950/20",
    text: "text-amber-600 dark:text-amber-400",
  },
  low: {
    icon: <Info className="h-3.5 w-3.5" />,
    bg: "bg-sky-50 dark:bg-sky-950/20",
    text: "text-sky-600 dark:text-sky-400",
  },
};

interface TicketCardProps {
  ticket: EscalationTicket;
}

export function TicketCard({ ticket }: TicketCardProps) {
  const analysis = useStore((s) => s.analysis);
  const [resolved, setResolved] = useState(ticket.resolved ?? false);
  const [resolution, setResolution] = useState(ticket.resolution);
  const [isResolving, setIsResolving] = useState(false);

  const sevCfg = severityConfig[ticket.severity] ?? severityConfig.medium;

  async function handleResolve(decision: ResolutionDecision) {
    if (!analysis?.analysis_id) return;
    setIsResolving(true);

    // Optimistic update
    const previousResolved = resolved;
    const previousResolution = resolution;
    setResolved(true);
    setResolution({ decision, timestamp: new Date().toISOString() });

    try {
      await resolveTicket(analysis.analysis_id, ticket.ticket_id, decision);
      toast.success(`Ticket ${ticket.ticket_id}: ${decision}d`);
    } catch (e) {
      // Revert on error
      setResolved(previousResolved);
      setResolution(previousResolution);
      const msg = e instanceof Error ? e.message : "Resolution failed";
      toast.error(msg);
    } finally {
      setIsResolving(false);
    }
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "rounded-lg border p-3",
        resolved
          ? "border-emerald-200 bg-emerald-50/50 dark:border-emerald-900 dark:bg-emerald-950/10"
          : "border-rose-200 bg-rose-50/50 dark:border-rose-900 dark:bg-rose-950/10"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={cn(sevCfg.text)}>{sevCfg.icon}</span>
          <Badge
            className={cn(
              "text-[10px] font-bold uppercase px-1.5 py-0 h-4",
              sevCfg.bg,
              sevCfg.text
            )}
          >
            {ticket.severity}
          </Badge>
          {resolved && (
            <Badge className="bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400 text-[10px] px-1.5 py-0 h-4">
              <CheckCircle2 className="mr-0.5 h-2.5 w-2.5" />
              {resolution?.decision ?? "Resolved"}
            </Badge>
          )}
        </div>
        <span className="text-[10px] text-slate-400 tabular-nums flex items-center gap-1">
          <Clock className="h-2.5 w-2.5" />
          {formatTime(ticket.timestamp)}
        </span>
      </div>

      {/* Reason */}
      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-2">
        {ticket.reason}
      </p>

      {/* Metadata chips */}
      <div className="flex flex-wrap items-center gap-1.5 mb-2">
        {ticket.clause_id && (
          <span className="text-[10px] text-slate-400">
            Clause: {ticket.clause_id}
          </span>
        )}
        {ticket.standard && (
          <span className="inline-flex items-center gap-1 rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
            {STANDARD_LABELS[ticket.standard] ?? ticket.standard}
          </span>
        )}
      </div>

      {/* Resolution actions */}
      {!resolved && (
        <ResolutionActions
          onResolve={handleResolve}
          disabled={isResolving}
        />
      )}
    </motion.div>
  );
}
