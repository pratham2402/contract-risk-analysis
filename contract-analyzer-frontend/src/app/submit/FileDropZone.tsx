"use client";

import { useRef, useState, type DragEvent } from "react";
import { Upload, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileDropZoneProps {
  file: File | null;
  onFileSelect: (file: File) => void;
  onClear: () => void;
  accept?: string;
  maxSizeMB?: number;
  disabled?: boolean;
}

export function FileDropZone({
  file,
  onFileSelect,
  onClear,
  accept = ".pdf,.docx,.txt",
  maxSizeMB = 10,
  disabled = false,
}: FileDropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) onFileSelect(f);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFileSelect(f);
  }

  // File already selected — show badge
  if (file) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
        <FileText className="h-8 w-8 text-violet-500 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{file.name}</p>
          <p className="text-xs text-muted-foreground">
            {(file.size / 1024).toFixed(1)} KB
          </p>
        </div>
        <button
          onClick={onClear}
          disabled={disabled}
          className="shrink-0 rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground disabled:opacity-50"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    );
  }

  // Empty drop zone
  return (
    <div
      className={cn(
        "relative rounded-xl border-2 border-dashed p-12 text-center transition-colors cursor-pointer",
        isDragOver
          ? "border-violet-500 bg-violet-50 dark:bg-violet-950/20"
          : "border-slate-200 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-500"
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <Upload className="mx-auto h-10 w-10 text-muted-foreground" />
      <p className="mt-3 text-sm font-medium text-foreground">
        Drop your contract here
      </p>
      <p className="mt-1 text-xs text-muted-foreground">
        or click to browse — PDF, DOCX, TXT (max {maxSizeMB}MB)
      </p>
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={handleFileChange}
        disabled={disabled}
      />
    </div>
  );
}
