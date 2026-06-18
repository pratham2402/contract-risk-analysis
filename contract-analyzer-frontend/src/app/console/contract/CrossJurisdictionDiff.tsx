"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Scale, CheckCircle2, XCircle, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { cn, STANDARD_LABELS } from "@/lib/utils";
import type { StandardsApplicability } from "@/lib/types";

interface CrossJurisdictionDiffProps {
  open: boolean;
  onClose: () => void;
}

export function CrossJurisdictionDiff({
  open,
  onClose,
}: CrossJurisdictionDiffProps) {
  const analysis = useStore((s) => s.analysis);

  if (!analysis) return null;

  const jurisdiction = analysis.jurisdiction_analysis;
  const applicability = analysis.standards_applicability ?? [];

  const applicable = applicability.filter((s) => s.applies);
  const excluded = applicability.filter((s) => !s.applies);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/30"
            onClick={onClose}
          />

          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-4 z-50 mx-auto my-auto max-h-[85vh] max-w-4xl overflow-y-auto rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-[#0e0e14]"
          >
            {/* Header */}
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 dark:border-slate-800 dark:bg-[#0e0e14]">
              <div className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-violet-500" />
                <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">
                  Cross-Jurisdiction Analysis
                </h2>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-6 p-6">
              {/* Left: Contract jurisdiction */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-500 flex items-center gap-1.5">
                  <Globe className="h-4 w-4" />
                  Contract Jurisdiction
                </h3>

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    Governing Law
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {jurisdiction?.governing_law ?? "Not specified"}
                  </p>
                  {jurisdiction?.party_a_location && (
                    <>
                      <p className="mt-3 text-sm font-medium text-slate-700 dark:text-slate-300">
                        Party A
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {jurisdiction.party_a_location}
                      </p>
                    </>
                  )}
                  {jurisdiction?.party_b_location && (
                    <>
                      <p className="mt-3 text-sm font-medium text-slate-700 dark:text-slate-300">
                        Party B
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {jurisdiction.party_b_location}
                      </p>
                    </>
                  )}
                </div>
              </div>

              {/* Right: Knowledge base comparison */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-500 flex items-center gap-1.5">
                  <Scale className="h-4 w-4" />
                  Regulatory Knowledge Base
                </h3>

                {/* Applicable */}
                {applicable.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-500">
                      Applicable ({applicable.length})
                    </span>
                    <div className="space-y-2">
                      {applicable.map((item) => (
                        <div
                          key={item.standard}
                          className="rounded-lg border border-emerald-200 bg-emerald-50/50 p-3 dark:border-emerald-900 dark:bg-emerald-950/10"
                        >
                          <div className="flex items-start gap-2">
                            <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                            <div>
                              <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                {STANDARD_LABELS[item.standard] ?? item.standard}
                              </p>
                              {item.reason && (
                                <p className="mt-0.5 text-xs text-slate-500">
                                  {item.reason}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Excluded */}
                {excluded.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                      Excluded ({excluded.length})
                    </span>
                    <div className="space-y-2">
                      {excluded.map((item) => (
                        <div
                          key={item.standard}
                          className="rounded-lg border border-slate-200 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-slate-900/50 opacity-60"
                        >
                          <div className="flex items-start gap-2">
                            <XCircle className="h-4 w-4 text-slate-300 dark:text-slate-600 mt-0.5 shrink-0" />
                            <div>
                              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                                {STANDARD_LABELS[item.standard] ?? item.standard}
                              </p>
                              {item.reason && (
                                <p className="mt-0.5 text-xs text-slate-400">
                                  {item.reason}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

/** Button that opens the diff dialog */
export function CrossJurisdictionDiffTrigger() {
  const [open, setOpen] = useState(false);
  const analysis = useStore((s) => s.analysis);
  const jurisdiction = analysis?.jurisdiction_analysis;

  if (!jurisdiction?.governing_law) return null;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 text-xs text-violet-600 hover:underline dark:text-violet-400"
      >
        <Scale className="h-3.5 w-3.5" />
        Compare Jurisdiction
      </button>
      <CrossJurisdictionDiff open={open} onClose={() => setOpen(false)} />
    </>
  );
}
