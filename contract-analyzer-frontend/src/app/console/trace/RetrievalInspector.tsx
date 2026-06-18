"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Database, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useStore } from "@/stores";
import { cn, RETRIEVAL_SOURCE_COLORS } from "@/lib/utils";
import type { RetrievedChunk } from "@/lib/types";

export function RetrievalInspector() {
  const chunks = useStore((s) => s.retrievedChunks);
  const [activeSource, setActiveSource] = useState<"all" | "faiss" | "bm25">(
    "all"
  );

  const filtered =
    activeSource === "all"
      ? chunks
      : chunks.filter((c) => c.source === activeSource);

  if (chunks.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-xs text-slate-400">
        <Database className="mr-1.5 h-3.5 w-3.5" />
        No evidence retrieved yet
      </div>
    );
  }

  const faissCount = chunks.filter((c) => c.source === "faiss").length;
  const bm25Count = chunks.filter((c) => c.source === "bm25").length;

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Search className="h-3.5 w-3.5" />
          <span>Retrieved Evidence ({chunks.length})</span>
        </div>
      </div>

      {/* Source filter */}
      <div className="flex gap-1.5">
        <SourceChip
          label="All"
          count={chunks.length}
          active={activeSource === "all"}
          onClick={() => setActiveSource("all")}
        />
        <SourceChip
          label="FAISS"
          count={faissCount}
          active={activeSource === "faiss"}
          onClick={() => setActiveSource("faiss")}
          source="faiss"
        />
        <SourceChip
          label="BM25"
          count={bm25Count}
          active={activeSource === "bm25"}
          onClick={() => setActiveSource("bm25")}
          source="bm25"
        />
      </div>

      {/* Chunk list */}
      <div className="space-y-2 max-h-80 overflow-y-auto">
        <AnimatePresence initial={false} mode="popLayout">
          {filtered.map((chunk, i) => (
            <ChunkCard key={`${chunk.source}-${i}`} chunk={chunk} index={i} />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

function SourceChip({
  label,
  count,
  active,
  onClick,
  source,
}: {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
  source?: string;
}) {
  const colors =
    source && source in RETRIEVAL_SOURCE_COLORS
      ? RETRIEVAL_SOURCE_COLORS[source]
      : null;

  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium transition-colors border",
        active
          ? colors
            ? `${colors.bg} ${colors.text} border-current/20`
            : "bg-slate-800 text-slate-200 border-slate-700"
          : "border-slate-200 text-slate-400 hover:text-slate-600 dark:border-slate-800 dark:hover:text-slate-300"
      )}
    >
      {label}
      <span className="tabular-nums opacity-70">{count}</span>
    </button>
  );
}

function ChunkCard({
  chunk,
  index,
}: {
  chunk: RetrievedChunk;
  index: number;
}) {
  const colors = RETRIEVAL_SOURCE_COLORS[chunk.source] ?? {};
  const scorePct = Math.round((chunk.relevance_score ?? 0) * 100);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ delay: index * 0.02 }}
      className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-2.5"
    >
      <div className="flex items-center justify-between mb-1">
        <Badge
          variant="outline"
          className={cn(
            "text-[10px] px-1.5 py-0 h-4 font-medium",
            colors.bg,
            colors.text
          )}
        >
          {chunk.source.toUpperCase()}
        </Badge>
      </div>

      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed line-clamp-3">
        {chunk.snippet}
      </p>

      {/* Relevance bar */}
      {chunk.relevance_score != null && (
        <div className="mt-2 flex items-center gap-2">
          <div className="flex-1 h-1 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${scorePct}%` }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className={cn(
                "h-full rounded-full",
                chunk.source === "faiss" ? "bg-blue-500" : "bg-amber-500"
              )}
            />
          </div>
          <span className="text-[10px] text-slate-400 tabular-nums w-8 text-right">
            {scorePct}%
          </span>
        </div>
      )}
    </motion.div>
  );
}
