"use client";

import { Shield, TrendingUp, Scale } from "lucide-react";
import { cn } from "@/lib/utils";

type Specialist = "privacy" | "financial" | "generalist";

const config: Record<Specialist, { label: string; icon: React.ReactNode }> = {
  privacy: {
    label: "Privacy Specialist",
    icon: <Shield className="h-3 w-3" />,
  },
  financial: {
    label: "Financial Specialist",
    icon: <TrendingUp className="h-3 w-3" />,
  },
  generalist: {
    label: "Generalist Agent",
    icon: <Scale className="h-3 w-3" />,
  },
};

export function SpecialistBadge({
  specialist,
}: {
  specialist: string;
}) {
  const cfg = config[specialist as Specialist] ?? config.generalist;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border border-violet-500/30",
        "bg-violet-500/10 px-2 py-0.5 text-[11px] font-medium",
        "text-violet-700 dark:text-violet-400"
      )}
    >
      {cfg.icon}
      {cfg.label}
    </span>
  );
}
