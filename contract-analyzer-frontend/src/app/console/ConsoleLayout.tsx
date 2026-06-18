"use client";

import { type ReactNode, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConsoleSidebar } from "./ConsoleSidebar";
import { InspectorPanel } from "./InspectorPanel";
import { CrossJurisdictionDiffTrigger } from "./contract/CrossJurisdictionDiff";
import { ExportButton } from "./export/ExportButton";

export function ConsoleLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-white dark:bg-[#0a0a0f]">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 240, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="h-full shrink-0 overflow-hidden border-r border-slate-200 dark:border-slate-800"
          >
            <ConsoleSidebar />
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <div className="flex h-10 items-center gap-2 border-b border-slate-200 px-3 dark:border-slate-800">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setSidebarOpen((v) => !v)}
            aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
          >
            {sidebarOpen ? (
              <PanelLeftClose className="h-4 w-4" />
            ) : (
              <PanelLeftOpen className="h-4 w-4" />
            )}
          </Button>
          <span className="text-xs font-semibold tracking-widest text-slate-500">
            COMPLIANCE ANALYZER
          </span>
          <div className="flex-1" />
          <CrossJurisdictionDiffTrigger />
          <ExportButton />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </main>

      {/* Inspector */}
      <aside className="h-full w-[380px] shrink-0 overflow-y-auto border-l border-slate-200 dark:border-slate-800">
        <InspectorPanel />
      </aside>
    </div>
  );
}
