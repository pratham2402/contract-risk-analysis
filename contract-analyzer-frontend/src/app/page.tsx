"use client";

import { useStore } from "@/stores";
import { ConsoleLayout } from "./console/ConsoleLayout";
import { MainPanel } from "./console/MainPanel";
import { SubmissionView } from "./submit/SubmissionView";
import { AnalysisProgressTracker } from "./progress/AnalysisProgressTracker";
import { LiveTraceOverlay } from "./console/trace/LiveTraceOverlay";

export default function Page() {
  const analysis = useStore((s) => s.analysis);
  const jobStatus = useStore((s) => s.jobStatus);

  // Show progress tracker during async analysis
  if (jobStatus === "submitting" || jobStatus === "running") {
    return (
      <>
        <AnalysisProgressTracker />
        <LiveTraceOverlay />
      </>
    );
  }

  // Show console when analysis is loaded
  if (analysis) {
    return (
      <ConsoleLayout>
        <MainPanel />
      </ConsoleLayout>
    );
  }

  // Default: submission view
  return <SubmissionView />;
}
