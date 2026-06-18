"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Eye,
  X,
  ChevronLeft,
  Activity,
  Search,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { LangGraphDAG } from "./LangGraphDAG";
import { ReActLoopViewer } from "./ReActLoopViewer";
import { RetrievalInspector } from "./RetrievalInspector";

type TraceTab = "dag" | "react" | "retrieval";

export function LiveTraceOverlay() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<TraceTab>("dag");

  const isConnected = useStore((s) => s.isConnected);
  const traceEntries = useStore((s) => s.traceEntries);

  return (
    <>
      {/* Toggle button */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 16 }}
            onClick={() => setOpen(true)}
            className="fixed right-0 top-1/2 -translate-y-1/2 z-40 flex items-center gap-1.5 rounded-l-lg border border-r-0 border-violet-500/30 bg-violet-500/10 px-3 py-6 text-xs text-violet-600 dark:text-violet-400 hover:bg-violet-500/20 transition-colors"
          >
            <Eye className="h-3.5 w-3.5" />
            <span className="[writing-mode:vertical-lr] font-medium">
              LIVE TRACE
            </span>
            {traceEntries.length > 0 && (
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-violet-500 animate-pulse" />
            )}
          </motion.button>
        )}
      </AnimatePresence>

      {/* Slide-over panel */}
      <AnimatePresence>
        {open && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/20"
              onClick={() => setOpen(false)}
            />

            {/* Panel */}
            <motion.aside
              initial={{ x: 520 }}
              animate={{ x: 0 }}
              exit={{ x: 520 }}
              transition={{ type: "spring", stiffness: 400, damping: 40 }}
              className="fixed right-0 top-0 z-50 h-full w-[520px] border-l border-slate-200 bg-white shadow-xl dark:border-slate-800 dark:bg-[#0e0e14] flex flex-col"
            >
              {/* Header */}
              <div className="shrink-0 flex items-center justify-between border-b border-slate-200 px-4 h-12 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => setOpen(false)}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Activity className="h-4 w-4 text-violet-500" />
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    Live Agent Trace
                  </span>
                  {isConnected && (
                    <span className="flex items-center gap-1 text-[10px] text-emerald-500">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Connected
                    </span>
                  )}
                </div>
              </div>

              {/* Tab bar */}
              <div className="shrink-0 flex border-b border-slate-200 dark:border-slate-800">
                <TabButton
                  active={tab === "dag"}
                  icon={<Activity className="h-3.5 w-3.5" />}
                  label="Pipeline"
                  onClick={() => setTab("dag")}
                />
                <TabButton
                  active={tab === "react"}
                  icon={<RefreshCw className="h-3.5 w-3.5" />}
                  label="ReAct Loop"
                  onClick={() => setTab("react")}
                  badge={traceEntries.length}
                />
                <TabButton
                  active={tab === "retrieval"}
                  icon={<Search className="h-3.5 w-3.5" />}
                  label="Evidence"
                  onClick={() => setTab("retrieval")}
                />
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-4">
                <AnimatePresence mode="wait">
                  {tab === "dag" && (
                    <motion.div
                      key="dag"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <LangGraphDAG />
                      <div className="mt-4">
                        <ReActLoopViewer />
                      </div>
                    </motion.div>
                  )}
                  {tab === "react" && (
                    <motion.div
                      key="react"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <ReActLoopViewer />
                    </motion.div>
                  )}
                  {tab === "retrieval" && (
                    <motion.div
                      key="retrieval"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <RetrievalInspector />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

function TabButton({
  active,
  icon,
  label,
  onClick,
  badge,
}: {
  active: boolean;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  badge?: number;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium transition-colors border-b-2 -mb-px ${
        active
          ? "border-violet-500 text-violet-600 dark:text-violet-400"
          : "border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
      }`}
    >
      {icon}
      {label}
      {badge != null && badge > 0 && (
        <span className="inline-flex items-center justify-center h-4 min-w-[16px] rounded-full bg-violet-500/10 px-1 text-[10px] tabular-nums text-violet-500">
          {badge}
        </span>
      )}
    </button>
  );
}
