"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useStore } from "@/stores";
import type { MainTab } from "@/stores/analysis.slice";
import { OverviewTab } from "./tabs/OverviewTab";
import { FindingsTab } from "./tabs/FindingsTab";
import { ActionsTab } from "./tabs/ActionsTab";
import { AuditTab } from "./tabs/AuditTab";

export function MainPanel() {
  const mainTab = useStore((s) => s.mainTab);
  const setMainTab = useStore((s) => s.setMainTab);
  const analysis = useStore((s) => s.analysis);

  if (!analysis) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-slate-400">
          No analysis loaded. Submit a contract to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <Tabs
        value={mainTab}
        onValueChange={(v) => setMainTab(v as MainTab)}
        className="flex h-full flex-col"
      >
        <div className="shrink-0 border-b border-slate-200 px-4 dark:border-slate-800">
          <TabsList className="h-9">
            <TabsTrigger value="overview" className="text-xs">
              Overview
            </TabsTrigger>
            <TabsTrigger value="findings" className="text-xs">
              Findings
            </TabsTrigger>
            <TabsTrigger value="actions" className="text-xs">
              Actions
            </TabsTrigger>
            <TabsTrigger value="audit-standards" className="text-xs">
              Audit & Standards
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-hidden">
          {mainTab === "overview" && <OverviewTab />}
          {mainTab === "findings" && <FindingsTab />}
          {mainTab === "actions" && <ActionsTab />}
          {mainTab === "audit-standards" && <AuditTab />}
        </div>
      </Tabs>
    </div>
  );
}
