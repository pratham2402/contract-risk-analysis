"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Loader2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { getJobStatus } from "@/lib/api";
import { StageTimeline } from "./StageTimeline";
import { StageDetailCard } from "./StageDetailCard";

export function AnalysisProgressTracker() {
  const jobId = useStore((s) => s.jobId);
  const connect = useStore((s) => s.connect);
  const disconnect = useStore((s) => s.disconnect);
  const clear = useStore((s) => s.clear);
  const cancelJob = useStore((s) => s.cancelJob);
  const stages = useStore((s) => s.stages);
  const loadAnalysis = useStore((s) => s.loadAnalysis);
  const setJobCompleted = useStore((s) => s.setJobCompleted);
  const loadAttempted = useRef(false);

  // Connect to SSE stream
  useEffect(() => {
    if (!jobId) return;
    connect(jobId);
    return () => {
      disconnect();
    };
  }, [jobId, connect, disconnect]);

  // When complete stage finishes, fetch the result
  useEffect(() => {
    if (
      stages.complete?.status === "completed" &&
      jobId &&
      !loadAttempted.current
    ) {
      loadAttempted.current = true;
      getJobStatus(jobId)
        .then((job) => {
          if (job.result) {
            loadAnalysis(job.result, job.result.contract_text ?? "");
            setJobCompleted();
          }
        })
        .catch(() => {
          loadAttempted.current = false;
        });
    }
  }, [stages.complete?.status, jobId, loadAnalysis, setJobCompleted]);

  const handleCancel = () => {
    disconnect();
    clear();
    cancelJob();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex min-h-screen items-center justify-center bg-slate-50 p-4 dark:bg-[#0a0a0f]"
    >
      <div className="w-full max-w-lg space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-[#111118]">
        {/* Header with cancel button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-violet-500" />
            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">
              Analyzing Contract
            </h2>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={handleCancel}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Timeline */}
        <StageTimeline />

        {/* Detail card */}
        <StageDetailCard />

        {/* Footer */}
        <p className="text-center text-xs text-slate-400">
          This may take a minute. The analysis runs across multiple AI agents.
        </p>
      </div>
    </motion.div>
  );
}
