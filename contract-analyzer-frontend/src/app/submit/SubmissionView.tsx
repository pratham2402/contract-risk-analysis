"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Loader2 } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useStore } from "@/stores";
import { submitAsync } from "@/lib/api";
import { SAMPLES } from "@/lib/samples";
import { FileDropZone } from "./FileDropZone";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

type InputMode = "upload" | "paste";

export function SubmissionView() {
  const [mode, setMode] = useState<InputMode>("upload");
  const [name, setName] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setInput = useStore((s) => s.setInput);
  const setSubmitting = useStore((s) => s.setSubmitting);
  const setJobRunning = useStore((s) => s.setJobRunning);
  const setJobFailed = useStore((s) => s.setJobFailed);

  const canSubmit =
    !isSubmitting &&
    ((mode === "upload" && file) || (mode === "paste" && text.length >= 10));

  async function handleSubmit() {
    if (!canSubmit) return;
    setIsSubmitting(true);
    setError(null);

    try {
      const contractName = name || file?.name?.replace(/\.[^.]+$/, "") || "Unnamed Contract";
      setInput(contractName, text, file ?? undefined);

      const job = await submitAsync(contractName, text, file ?? undefined);
      setSubmitting(job.job_id);
      setJobRunning();
      // SSE connection handled by parent page once progress view renders
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Submission failed";
      setError(msg);
      setJobFailed(msg);
      toast.error(msg);
      setIsSubmitting(false);
    }
  }

  function loadSample(key: string) {
    const sample = SAMPLES[key];
    if (sample) {
      setText(sample.text);
      setName(sample.name);
      setFile(null);
      setMode("paste");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4 dark:bg-[#0a0a0f]">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-2xl space-y-5 rounded-xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-[#111118]"
      >
        {/* Header */}
        <div className="text-center space-y-1.5">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-800 dark:text-slate-200">
            Contract Compliance Analyzer
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            AI-powered contract risk analysis against 17 regulatory standards
          </p>
        </div>

        {/* Input mode toggle */}
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
          <button
            onClick={() => setMode("upload")}
            className={cn(
              "flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              mode === "upload"
                ? "bg-white text-slate-800 shadow-sm dark:bg-slate-700 dark:text-slate-200"
                : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            )}
          >
            <Upload className="h-4 w-4" />
            Upload Document
          </button>
          <button
            onClick={() => setMode("paste")}
            className={cn(
              "flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              mode === "paste"
                ? "bg-white text-slate-800 shadow-sm dark:bg-slate-700 dark:text-slate-200"
                : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            )}
          >
            <FileText className="h-4 w-4" />
            Paste Text
          </button>
        </div>

        {/* Name field */}
        <Input
          placeholder="Contract name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="h-9 text-sm"
        />

        {/* Input area */}
        {mode === "upload" ? (
          <FileDropZone
            file={file}
            onFileSelect={setFile}
            onClear={() => setFile(null)}
            accept=".pdf,.docx,.txt"
            maxSizeMB={10}
            disabled={isSubmitting}
          />
        ) : (
          <Textarea
            placeholder="Paste your full contract text here (minimum 10 characters)..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="min-h-[280px] resize-y font-mono text-sm"
            disabled={isSubmitting}
          />
        )}

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/20 dark:text-red-400"
          >
            {error}
          </motion.div>
        )}

        {/* Submit button */}
        <Button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="w-full h-11 text-base"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Submitting...
            </>
          ) : (
            "Run Analysis"
          )}
        </Button>

        {/* Sample contracts */}
        <div className="flex items-center justify-center gap-2 text-sm">
          <span className="text-slate-400 dark:text-slate-500">
            Try a sample:
          </span>
          {Object.entries(SAMPLES).map(([key, sample], i) => (
            <span key={key} className="inline-flex items-center gap-2">
              {i > 0 && (
                <span className="text-slate-300 dark:text-slate-600">·</span>
              )}
              <button
                onClick={() => loadSample(key)}
                disabled={isSubmitting}
                className="text-violet-600 hover:underline disabled:opacity-50 dark:text-violet-400"
              >
                {sample.name}
              </button>
            </span>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
