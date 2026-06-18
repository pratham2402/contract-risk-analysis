"use client";

import { useState } from "react";
import { CheckCircle2, ShieldAlert, XOctagon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ResolutionDecision = "approve" | "escalate" | "block";

interface ResolutionActionsProps {
  onResolve: (decision: ResolutionDecision) => Promise<void>;
  disabled?: boolean;
}

export function ResolutionActions({
  onResolve,
  disabled = false,
}: ResolutionActionsProps) {
  const [resolving, setResolving] = useState<ResolutionDecision | null>(null);

  async function handleDecision(decision: ResolutionDecision) {
    setResolving(decision);
    try {
      await onResolve(decision);
    } finally {
      setResolving(null);
    }
  }

  const btnClass = (active: boolean) =>
    cn(
      "flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
      disabled && "opacity-50 cursor-not-allowed"
    );

  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        disabled={disabled || resolving !== null}
        onClick={() => handleDecision("approve")}
        className="border-emerald-500/30 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/20 dark:text-emerald-400 dark:hover:bg-emerald-950/40"
      >
        {resolving === "approve" ? (
          <span className="mr-1 h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : (
          <CheckCircle2 className="h-3.5 w-3.5" />
        )}
        Approve
      </Button>

      <Button
        variant="outline"
        size="sm"
        disabled={disabled || resolving !== null}
        onClick={() => handleDecision("escalate")}
        className="border-amber-500/30 bg-amber-50 text-amber-700 hover:bg-amber-100 dark:bg-amber-950/20 dark:text-amber-400 dark:hover:bg-amber-950/40"
      >
        {resolving === "escalate" ? (
          <span className="mr-1 h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : (
          <ShieldAlert className="h-3.5 w-3.5" />
        )}
        Escalate
      </Button>

      <Button
        variant="outline"
        size="sm"
        disabled={disabled || resolving !== null}
        onClick={() => handleDecision("block")}
        className="border-red-500/30 bg-red-50 text-red-700 hover:bg-red-100 dark:bg-red-950/20 dark:text-red-400 dark:hover:bg-red-950/40"
      >
        {resolving === "block" ? (
          <span className="mr-1 h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : (
          <XOctagon className="h-3.5 w-3.5" />
        )}
        Block
      </Button>
    </div>
  );
}
