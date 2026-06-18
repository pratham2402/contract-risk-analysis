"use client";

import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import type { VerificationReport } from "@/lib/types";

type IntegrityStatus =
  | "verified_clean"
  | "verified_with_flags"
  | "hallucinated"
  | "unsupported"
  | "unverified";

interface CitationIntegrityBadgeProps {
  report: VerificationReport;
  className?: string;
}

function deriveStatus(report: VerificationReport): IntegrityStatus {
  if (!report.verified) return "unverified";
  if (report.hallucination_count > 0) return "hallucinated";
  if (report.flags.length > 0) return "verified_with_flags";
  return "verified_clean";
}

const statusConfig: Record<
  IntegrityStatus,
  { label: string; icon: React.ReactNode; className: string }
> = {
  verified_clean: {
    label: "Verified Clean",
    icon: <CheckCircle2 className="h-3 w-3" />,
    className:
      "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900",
  },
  verified_with_flags: {
    label: "Verified with Flags",
    icon: <AlertTriangle className="h-3 w-3" />,
    className:
      "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900",
  },
  hallucinated: {
    label: "Hallucinated",
    icon: <ShieldAlert className="h-3 w-3" />,
    className:
      "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900",
  },
  unsupported: {
    label: "Unsupported",
    icon: <XCircle className="h-3 w-3" />,
    className:
      "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900",
  },
  unverified: {
    label: "Unverified",
    icon: <HelpCircle className="h-3 w-3" />,
    className:
      "bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700",
  },
};

export function CitationIntegrityBadge({
  report,
  className,
}: CitationIntegrityBadgeProps) {
  const status = deriveStatus(report);
  const cfg = statusConfig[status];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium",
        cfg.className,
        className
      )}
    >
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

export type { IntegrityStatus };
