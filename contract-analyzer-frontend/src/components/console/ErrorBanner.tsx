"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, X, RefreshCw } from "lucide-react";

interface ErrorBannerProps {
  error: string | null;
  onDismiss: () => void;
  onRetry?: () => void;
}

export function ErrorBanner({ error, onDismiss, onRetry }: ErrorBannerProps) {
  return (
    <AnimatePresence>
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          className="flex items-start gap-3 mx-4 mt-4 rounded-lg border border-red-500/30 bg-red-950/20 px-4 py-3"
        >
          <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-red-400">
              Analysis failed
            </p>
            <p className="text-xs text-red-300/80 mt-0.5">{error}</p>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            {onRetry && (
              <button
                className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-red-400 hover:bg-red-950/40 transition-colors"
                onClick={onRetry}
              >
                <RefreshCw className="h-3 w-3" />
                Retry
              </button>
            )}
            <button
              className="rounded-md p-1 text-red-400/60 hover:text-red-400 hover:bg-red-950/40 transition-colors"
              onClick={onDismiss}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
