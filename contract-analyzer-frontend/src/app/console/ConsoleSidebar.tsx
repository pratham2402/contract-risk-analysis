"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Plus,
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { listAnalyses } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { ContractListItem } from "@/lib/types";

const statusIcon: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
  pending: <Clock className="h-4 w-4 text-amber-500" />,
  running: <Clock className="h-4 w-4 text-blue-500 animate-pulse" />,
  failed: <XCircle className="h-4 w-4 text-red-500" />,
  needs_review: <AlertCircle className="h-4 w-4 text-rose-500" />,
};

export function ConsoleSidebar() {
  const pastAnalyses = useStore((s) => s.pastAnalyses);
  const setPastAnalyses = useStore((s) => s.setPastAnalyses);
  const loadAnalysis = useStore((s) => s.loadAnalysis);
  const reset = useStore((s) => s.reset);

  useEffect(() => {
    listAnalyses()
      .then(setPastAnalyses)
      .catch(() => {});
  }, [setPastAnalyses]);

  const handleNew = () => {
    reset();
  };

  const handleSelect = async (item: ContractListItem) => {
    try {
      const { getAnalysis } = await import("@/lib/api");
      const detail = await getAnalysis(item.id);
      const analysis = detail.analysis ?? (detail as unknown as Parameters<typeof loadAnalysis>[0]);
      loadAnalysis(analysis, detail.contract_text ?? "");
    } catch {
      // silently fail — items may be stale
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-50 dark:bg-[#111118]">
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-2.5 dark:border-slate-800">
        <span className="text-xs font-semibold tracking-wider text-slate-500">
          PAST ANALYSES
        </span>
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleNew}>
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="space-y-0.5 p-2">
          {pastAnalyses.length === 0 && (
            <p className="px-3 py-8 text-center text-xs text-slate-400">
              No analyses yet
            </p>
          )}
          {pastAnalyses.map((item, i) => (
            <motion.button
              key={item.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03, duration: 0.2 }}
              onClick={() => handleSelect(item)}
              className="flex w-full items-start gap-2 rounded-md px-3 py-2 text-left transition-colors hover:bg-slate-200/60 dark:hover:bg-slate-800/60"
            >
              {statusIcon[item.status] ?? statusIcon.completed}
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-medium text-slate-700 dark:text-slate-300">
                  {item.name}
                </div>
                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <span>{formatDate(item.created_at)}</span>
                  {item.finding_count > 0 && (
                    <span>{item.finding_count} findings</span>
                  )}
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
