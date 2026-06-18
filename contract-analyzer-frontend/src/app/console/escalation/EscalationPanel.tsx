"use client";

import { motion } from "framer-motion";
import { AlertTriangle, UserCheck } from "lucide-react";
import { useStore } from "@/stores";
import { TicketCard } from "./TicketCard";
import type { EscalationTicket } from "@/lib/types";

export function EscalationPanel() {
  const analysis = useStore((s) => s.analysis);
  const tickets = analysis?.escalation_tickets ?? [];

  if (tickets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center px-4">
        <UserCheck className="h-8 w-8 text-slate-300 dark:text-slate-600 mb-3" />
        <p className="text-sm font-medium text-slate-500">
          No escalation tickets
        </p>
        <p className="mt-1 text-xs text-slate-400">
          No findings required human review for this analysis
        </p>
      </div>
    );
  }

  const unresolved = tickets.filter((t) => !t.resolved);
  const resolved = tickets.filter((t) => t.resolved);

  // Sort: unresolved first, by severity
  const severityOrder: Record<string, number> = {
    critical: 0,
    high: 1,
    medium: 2,
    low: 3,
  };

  const sortedUnresolved = [...unresolved].sort(
    (a, b) =>
      (severityOrder[a.severity] ?? 99) - (severityOrder[b.severity] ?? 99)
  );

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-rose-500" />
          <h3 className="text-xs font-semibold tracking-widest text-slate-400">
            ESCALATION TICKETS
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 tabular-nums">
          {unresolved.length} pending / {tickets.length} total
        </span>
      </div>

      {/* Human review callout */}
      {unresolved.length > 0 && (
        <div className="rounded-md border border-rose-200 bg-rose-50 p-3 dark:border-rose-900 dark:bg-rose-950/20">
          <p className="text-sm font-medium text-rose-700 dark:text-rose-400">
            Human review required
          </p>
          <p className="mt-1 text-xs text-rose-600 dark:text-rose-500">
            {unresolved.length} ticket{unresolved.length > 1 ? "s" : ""} require
            your decision before the analysis can be finalized.
          </p>
        </div>
      )}

      {/* Unresolved tickets */}
      {sortedUnresolved.length > 0 && (
        <div className="space-y-2">
          {sortedUnresolved.map((ticket, i) => (
            <motion.div
              key={ticket.ticket_id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <TicketCard ticket={ticket} />
            </motion.div>
          ))}
        </div>
      )}

      {/* Resolved tickets (collapsed by default) */}
      {resolved.length > 0 && (
        <details className="group">
          <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 py-1 select-none">
            Resolved tickets ({resolved.length})
          </summary>
          <div className="space-y-2 mt-2 opacity-70">
            {resolved.map((ticket) => (
              <TicketCard key={ticket.ticket_id} ticket={ticket} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
