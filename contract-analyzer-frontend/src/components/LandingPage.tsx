"use client";

import { useRef, useState, type DragEvent } from "react";
import { Upload, FileText, X } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { SAMPLES } from "@/lib/samples";

interface LandingPageProps {
  onSubmit: (name: string, text: string, file?: File) => Promise<void>;
  isAnalyzing: boolean;
}

type InputMode = "upload" | "paste";

export function LandingPage({ onSubmit, isAnalyzing }: LandingPageProps) {
  const [mode, setMode] = useState<InputMode>("upload");
  const [text, setText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) setSelectedFile(file);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) setSelectedFile(file);
  }

  function clearFile() {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function handleSubmit() {
    if (isAnalyzing) return;
    const contractName = selectedFile?.name.replace(/\.[^.]+$/, "") ?? "Unnamed Contract";
    onSubmit(contractName, text, selectedFile ?? undefined);
  }

  function loadSample(key: string) {
    const sample = SAMPLES[key];
    if (sample) {
      setText(sample.text);
      setSelectedFile(null);
      setMode("paste");
    }
  }

  const canSubmit = !isAnalyzing && (!!selectedFile || text.length >= 10);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-xl space-y-6">
        {/* Brand */}
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground">
            Contract Compliance Analyzer
          </h1>
          <p className="mt-1 text-base text-muted-foreground">
            AI-powered contract compliance & risk analysis
          </p>
        </div>

        {/* Mode toggle */}
        <div className="flex rounded-lg bg-muted p-1">
          <button
            onClick={() => setMode("upload")}
            className={cn(
              "flex-1 rounded-md py-2 text-base font-medium transition-colors",
              mode === "upload"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Upload className="mr-1.5 inline-block h-4 w-4" />
            Upload Document
          </button>
          <button
            onClick={() => setMode("paste")}
            className={cn(
              "flex-1 rounded-md py-2 text-base font-medium transition-colors",
              mode === "paste"
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <FileText className="mr-1.5 inline-block h-4 w-4" />
            Paste Text
          </button>
        </div>

        {/* Upload mode */}
        {mode === "upload" && !selectedFile && (
          <div
            className={cn(
              "relative rounded-xl border-2 border-dashed p-12 text-center transition-colors cursor-pointer",
              isDragOver
                ? "border-primary bg-primary/5"
                : "border-border hover:border-muted-foreground/30"
            )}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="mx-auto h-10 w-10 text-muted-foreground" />
            <p className="mt-3 text-base font-medium text-foreground">
              Drop your contract here
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              or click to browse — PDF, DOCX, TXT (max 10MB)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={handleFileChange}
              disabled={isAnalyzing}
            />
          </div>
        )}

        {/* File selected badge */}
        {mode === "upload" && selectedFile && (
          <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-4">
            <FileText className="h-8 w-8 text-primary shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-base font-medium truncate">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={clearFile}
              className="shrink-0 rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
              disabled={isAnalyzing}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Paste mode */}
        {mode === "paste" && (
          <Textarea
            placeholder="Paste your full contract text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="min-h-[280px] resize-y font-mono text-base"
            disabled={isAnalyzing}
          />
        )}

        {/* Submit */}
        <button
          className="inline-flex w-full h-12 items-center justify-center rounded-lg bg-primary text-primary-foreground text-lg font-medium transition-all disabled:pointer-events-none disabled:opacity-50"
          disabled={!canSubmit}
          onClick={handleSubmit}
        >
          {isAnalyzing ? (
            <>
              <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              Analyzing...
            </>
          ) : (
            "Run Analysis"
          )}
        </button>

        {/* Sample contracts */}
        <div className="text-center">
          <span className="text-sm text-muted-foreground">
            Try a sample:{" "}
          </span>
          {Object.entries(SAMPLES).map(([key, sample]) => (
            <button
              key={key}
              onClick={() => loadSample(key)}
              disabled={isAnalyzing}
              className="text-sm font-medium text-primary hover:underline disabled:opacity-50"
            >
              {sample.name}
              {key !== Object.keys(SAMPLES).pop() && (
                <span className="text-muted-foreground"> · </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
