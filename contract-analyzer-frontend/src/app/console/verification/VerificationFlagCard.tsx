"use client";

import { AlertTriangle, ShieldAlert, Zap, BookX, AlertCircle } from "lucide-react";
import { cn, FLAG_SEVERITY_COLORS } from "@/lib/utils";
import type { FlagSeverity } from "@/lib/utils";
import type { VerificationFlag } from "@/lib/types";

const FLAG_TYPE_ICONS: Record<string, React.ReactNode> = {
  hallucinated_citation: <ShieldAlert className="h-3.5 w-3.5" />,
  unsupported_citation: <BookX className="h-3.5 w-3.5" />,
  disconnected_reasoning: <AlertCircle className="h-3.5 w-3.5" />,
  risk_level_mismatch: <AlertTriangle className="h-3.5 w-3.5" />,
  generic_exclusion: <Zap className="h-3.5 w-3.5" />,
};

const FLAG_TYPE_LABELS: Record<string, string> = {
  hallucinated_citation: "Hallucinated Citation",
  unsupported_citation: "Unsupported Citation",
  disconnected_reasoning: "Disconnected Reasoning",
  risk_level_mismatch: "Risk Level Mismatch",
  generic_exclusion: "Generic Exclusion",
};

interface VerificationFlagCardProps {
  flag: VerificationFlag;
  onFindingClick?: (findingId: string) => void;
}

export function VerificationFlagCard({
  flag,
  onFindingClick,
}: VerificationFlagCardProps) {
  const sevColors = FLAG_SEVERITY_COLORS[flag.severity as FlagSeverity] ?? FLAG_SEVERITY_COLORS.info;
  const icon = FLAG_TYPE_ICONS[flag.flag_type] ?? <AlertCircle className="h-3.5 w-3.5" />;
  const label = FLAG_TYPE_LABELS[flag.flag_type] ?? flag.flag_type;

  return (
    <div
      className={cn(
        "rounded-lg border p-3 border-l-[3px]",
        sevColors.border,
        sevColors.bg
      )}
    >
      <div className="flex items-start gap-2">
        <span className={cn("shrink-0 mt-0.5", sevColors.text)}>{icon}</span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn("text-xs font-semibold", sevColors.text)}>
              {label}
            </span>
            <span
              className={cn(
                "text-[10px] uppercase font-medium px-1.5 py-0 rounded-full",
                sevColors.bg,
                sevColors.text
              )}
            >
              {flag.severity}
            </span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            {flag.detail}
          </p>
          {onFindingClick && (
            <button
              onClick={() => onFindingClick(flag.finding_id)}
              className="mt-1.5 text-[11px] text-violet-600 dark:text-violet-400 hover:underline"
            >
              View finding &rarr;
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
