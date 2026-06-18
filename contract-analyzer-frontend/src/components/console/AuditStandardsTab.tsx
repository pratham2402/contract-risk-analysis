"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { AuditTrail } from "./AuditTrail";
import { StandardsPanel } from "./StandardsPanel";
import type { AuditTrailEntry, StandardsApplicability } from "@/lib/types";

interface AuditStandardsTabProps {
  auditTrail: AuditTrailEntry[];
  totalDurationMs: number;
  standardsApplicability: StandardsApplicability[];
}

export function AuditStandardsTab({
  auditTrail,
  totalDurationMs,
  standardsApplicability,
}: AuditStandardsTabProps) {
  return (
    <div className="flex h-full">
      {/* Audit Trail - 60% */}
      <div className="w-[60%] shrink-0 border-r border-border overflow-hidden">
        <ScrollArea className="h-full">
          <AuditTrail auditTrail={auditTrail} totalDurationMs={totalDurationMs} />
        </ScrollArea>
      </div>

      {/* Standards Applicability - 40% */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <StandardsPanel applicability={standardsApplicability} />
        </ScrollArea>
      </div>
    </div>
  );
}
