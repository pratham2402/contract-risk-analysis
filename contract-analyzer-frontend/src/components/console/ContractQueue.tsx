"use client";

import { motion } from "framer-motion";
import { FileText, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";
import type { ContractListItem } from "@/lib/types";

interface ContractQueueProps {
  analyses: ContractListItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

const statusIcons: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />,
  pending: <Clock className="h-3.5 w-3.5 text-yellow-400" />,
  error: <AlertCircle className="h-3.5 w-3.5 text-red-400" />,
};

export function ContractQueue({
  analyses,
  selectedId,
  onSelect,
}: ContractQueueProps) {
  return (
    <div className="p-2">
      <p className="px-2 pb-2 pt-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        Contract Queue
      </p>
      {analyses.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <FileText className="h-6 w-6 text-muted-foreground/40" />
          <p className="mt-2 text-xs text-muted-foreground">
            No contracts analyzed yet
          </p>
        </div>
      ) : (
        <div className="space-y-0.5">
          {analyses.map((item, i) => (
            <motion.button
              key={item.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
              className={cn(
                "w-full rounded-md px-3 py-2.5 text-left transition-colors",
                selectedId === item.id
                  ? "bg-accent border-l-2 border-l-primary"
                  : "hover:bg-accent/50 border-l-2 border-l-transparent"
              )}
              onClick={() => onSelect(item.id)}
            >
              <div className="flex items-center gap-2">
                <span className="flex-1 truncate text-xs font-medium">
                  {item.name}
                </span>
                <span className="shrink-0">
                  {statusIcons[item.status] ?? statusIcons.pending}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatDate(item.created_at)}</span>
                <span>·</span>
                <span>{item.finding_count} findings</span>
                <span>·</span>
                <span>{item.clause_count} clauses</span>
              </div>
            </motion.button>
          ))}
        </div>
      )}
    </div>
  );
}
