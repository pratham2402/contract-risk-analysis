"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Scale, ChevronDown } from "lucide-react";
import { useState } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn, STANDARD_LABELS } from "@/lib/utils";
import type { StandardsApplicability } from "@/lib/types";

interface StandardsPanelProps {
  applicability: StandardsApplicability[];
}

export function StandardsPanel({
  applicability,
}: StandardsPanelProps) {
  const [showExcluded, setShowExcluded] = useState(false);

  if (applicability.length === 0) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <p className="text-xs text-muted-foreground">
          No standards applicability data
        </p>
      </div>
    );
  }

  const applicable = applicability.filter((s) => s.applies);
  const excluded = applicability.filter((s) => !s.applies);

  return (
    <div className="p-3 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3 shrink-0">
        <div className="flex items-center gap-2">
          <Scale className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
            Standards Applicability
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          {applicable.length} of {applicability.length} apply
        </span>
      </div>

      <div className="flex-1 overflow-auto">
        {/* Applicable standards */}
        {applicable.length > 0 && (
          <div className="mb-3">
            <span className="text-[10px] font-medium uppercase tracking-wider text-green-400/70 mb-2 block">
              Applicable
            </span>
            <div className="grid grid-cols-2 gap-2">
              {applicable.map((item, i) => (
                <motion.div
                  key={item.standard}
                  initial={{ opacity: 0, x: 12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="rounded-lg border border-green-500/30 bg-green-950/10 p-2.5"
                >
                  <div className="flex items-start gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-400 shrink-0 mt-0.5" />
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-foreground">
                        {STANDARD_LABELS[item.standard] ?? item.standard}
                      </p>
                      <p className="text-xs text-muted-foreground leading-relaxed mt-0.5">
                        {item.reason || "Applies"}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Excluded standards — collapsible */}
        {excluded.length > 0 && (
          <Collapsible open={showExcluded} onOpenChange={setShowExcluded}>
            <CollapsibleTrigger className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground w-full py-1">
              <ChevronDown className={cn(
                "h-3 w-3 transition-transform",
                showExcluded && "rotate-180"
              )} />
              <span className="text-[10px] font-medium uppercase tracking-wider">
                Reviewed & Excluded ({excluded.length})
              </span>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {excluded.map((item, i) => (
                  <motion.div
                    key={item.standard}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                    className="rounded-lg border border-border bg-card/50 p-2.5 opacity-70"
                  >
                    <div className="flex items-start gap-1.5">
                      <XCircle className="h-3.5 w-3.5 text-muted-foreground/30 shrink-0 mt-0.5" />
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-muted-foreground">
                          {STANDARD_LABELS[item.standard] ?? item.standard}
                        </p>
                        <p className="text-xs text-muted-foreground/60 leading-relaxed mt-0.5">
                          {item.reason || "Not applicable"}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}
      </div>
    </div>
  );
}
