"use client";

import { Loader2 } from "lucide-react";

interface AnalysisLoadingOverlayProps {
  isAnalyzing: boolean;
}

export function AnalysisLoadingOverlay({ isAnalyzing }: AnalysisLoadingOverlayProps) {
  if (!isAnalyzing) return null;

  return (
    <div className="flex flex-1 items-center justify-center">
      <div className="text-center space-y-4">
        <Loader2 className="mx-auto h-10 w-10 animate-spin text-primary" />
        <div>
          <p className="text-base font-medium text-foreground">
            Analyzing your contract
          </p>
          <p className="mt-1 text-sm text-muted-foreground max-w-sm">
            Agents are parsing clauses, retrieving regulatory standards, evaluating
            compliance risks, and generating recommendations.
          </p>
        </div>
      </div>
    </div>
  );
}