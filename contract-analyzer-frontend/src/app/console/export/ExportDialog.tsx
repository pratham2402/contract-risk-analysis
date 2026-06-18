"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  FileText,
  Download,
  FileJson,
  CheckCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/stores";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

type ExportFormat = "csv" | "pdf";
type ExportSection =
  | "summary"
  | "findings"
  | "recommendations"
  | "audit_trail"
  | "verification"
  | "escalation";

const SECTION_LABELS: Record<ExportSection, string> = {
  summary: "Summary & Statistics",
  findings: "Findings",
  recommendations: "Recommendations",
  audit_trail: "Audit Trail",
  verification: "Verification Report",
  escalation: "Escalation Tickets",
};

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
}

export function ExportDialog({ open, onClose }: ExportDialogProps) {
  const analysis = useStore((s) => s.analysis);
  const contractText = useStore((s) => s.contractText);

  const [format, setFormat] = useState<ExportFormat>("csv");
  const [sections, setSections] = useState<ExportSection[]>([
    "summary",
    "findings",
    "recommendations",
  ]);
  const [exporting, setExporting] = useState(false);

  if (!analysis) return null;

  function toggleSection(section: ExportSection) {
    setSections((prev) =>
      prev.includes(section)
        ? prev.filter((s) => s !== section)
        : [...prev, section]
    );
  }

  function toggleAll() {
    if (sections.length === 6) {
      setSections([]);
    } else {
      setSections([
        "summary",
        "findings",
        "recommendations",
        "audit_trail",
        "verification",
        "escalation",
      ]);
    }
  }

  async function handleExport() {
    if (sections.length === 0) {
      toast.error("Select at least one section to export");
      return;
    }

    setExporting(true);

    try {
      if (format === "csv") {
        exportCSV(analysis!, contractText, sections);
      } else {
        exportPDF();
      }
      toast.success(
        `Exported ${sections.length} section${sections.length > 1 ? "s" : ""} as ${format.toUpperCase()}`
      );
      onClose();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Export failed";
      toast.error(msg);
    } finally {
      setExporting(false);
    }
  }

  const allSelected = sections.length === 6;

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/30"
            onClick={onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 z-50 m-auto h-fit w-full max-w-md rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-[#111118]"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <Download className="h-4 w-4 text-violet-500" />
                <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                  Export Analysis
                </h2>
              </div>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-5 p-5">
              {/* Format toggle */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-500">
                  FORMAT
                </label>
                <div className="flex rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
                  <FormatButton
                    active={format === "csv"}
                    icon={<FileText className="h-3.5 w-3.5" />}
                    label="CSV"
                    onClick={() => setFormat("csv")}
                  />
                  <FormatButton
                    active={format === "pdf"}
                    icon={<FileJson className="h-3.5 w-3.5" />}
                    label="PDF"
                    onClick={() => setFormat("pdf")}
                  />
                </div>
              </div>

              {/* Section checkboxes */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-slate-500">
                    SECTIONS
                  </label>
                  <button
                    onClick={toggleAll}
                    className="text-[11px] text-violet-600 hover:underline dark:text-violet-400"
                  >
                    {allSelected ? "Deselect all" : "Select all"}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {(
                    [
                      "summary",
                      "findings",
                      "recommendations",
                      "audit_trail",
                      "verification",
                      "escalation",
                    ] as ExportSection[]
                  ).map((section) => {
                    const checked = sections.includes(section);
                    return (
                      <label
                        key={section}
                        className={cn(
                          "flex items-center gap-2 rounded-md border px-3 py-2 cursor-pointer transition-colors",
                          checked
                            ? "border-violet-500/30 bg-violet-50 dark:bg-violet-950/10"
                            : "border-slate-200 dark:border-slate-800 hover:border-slate-400"
                        )}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleSection(section)}
                          className="h-3.5 w-3.5 rounded border-slate-300 text-violet-500"
                        />
                        <span className="text-xs text-slate-700 dark:text-slate-300">
                          {SECTION_LABELS[section]}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Export button */}
              <Button
                onClick={handleExport}
                disabled={sections.length === 0 || exporting}
                className="w-full"
              >
                {exporting ? (
                  <>
                    <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Export {sections.length} section
                    {sections.length > 1 ? "s" : ""} as{" "}
                    {format.toUpperCase()}
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function FormatButton({
  active,
  icon,
  label,
  onClick,
}: {
  active: boolean;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-white text-slate-800 shadow-sm dark:bg-slate-700 dark:text-slate-200"
          : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
      )}
    >
      {icon}
      {label}
    </button>
  );
}

/** Generate CSV from analysis data and trigger download */
function exportCSV(
  analysis: ReturnType<typeof useStore.getState>["analysis"] & {},
  contractText: string,
  sections: ExportSection[]
) {
  const rows: string[] = [];

  rows.push("section,field,value");

  if (sections.includes("summary")) {
    const s = analysis?.summary;
    if (s) {
      rows.push(`summary,total_clauses,${s.total_clauses}`);
      rows.push(`summary,total_findings,${s.total_findings}`);
      rows.push(`summary,total_recommendations,${s.total_recommendations}`);
      rows.push(
        `summary,risk_counts,critical:${s.risk_counts.critical ?? 0}|high:${s.risk_counts.high ?? 0}|medium:${s.risk_counts.medium ?? 0}|low:${s.risk_counts.low ?? 0}|info:${s.risk_counts.info ?? 0}`
      );
    }
  }

  if (sections.includes("findings")) {
    for (const f of analysis?.findings ?? []) {
      rows.push(
        `findings,${f.id},${f.risk_level},${f.category},"${f.issue_description.replace(/"/g, '""')}",${f.confidence}`
      );
    }
  }

  if (sections.includes("recommendations")) {
    for (const r of analysis?.recommendations ?? []) {
      rows.push(
        `recommendations,${r.id},${r.decision},${r.risk_level},${r.owner},"${r.recommended_action.replace(/"/g, '""')}"`
      );
    }
  }

  if (sections.includes("audit_trail")) {
    for (const entry of analysis?.audit_trail ?? []) {
      rows.push(
        `audit_trail,${entry.timestamp},${entry.stage},${entry.action.replace(/"/g, '""')}`
      );
    }
  }

  if (sections.includes("verification")) {
    const vrf = analysis?.verification_report;
    if (vrf) {
      rows.push(`verification,verified,${vrf.verified}`);
      rows.push(`verification,total_citations,${vrf.total_citations}`);
      rows.push(`verification,hallucination_count,${vrf.hallucination_count}`);
      rows.push(
        `verification,adjusted_confidence,${vrf.adjusted_confidence}`
      );
      for (const flag of vrf.flags) {
        rows.push(
          `verification_flags,${flag.finding_id},${flag.flag_type},${flag.severity},"${flag.detail.replace(/"/g, '""')}"`
        );
      }
    }
  }

  if (sections.includes("escalation")) {
    for (const t of analysis?.escalation_tickets ?? []) {
      rows.push(
        `escalation,${t.ticket_id},${t.severity},${t.resolved ? "resolved" : "pending"},"${t.reason.replace(/"/g, '""')}"`
      );
    }
  }

  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `compliance-analysis-${analysis?.analysis_id ?? "export"}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/** Trigger browser print dialog for PDF export */
function exportPDF() {
  window.print();
}
