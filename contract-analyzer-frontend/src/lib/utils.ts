import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { ClauseType, Decision, Owner, RiskLevel } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const RISK_COLORS: Record<
  RiskLevel,
  { bg: string; text: string; border: string; dot: string }
> = {
  critical: {
    bg: "bg-red-600/20",
    text: "text-red-300",
    border: "border-red-500/60",
    dot: "bg-red-500",
  },
  high: {
    bg: "bg-orange-600/20",
    text: "text-orange-300",
    border: "border-orange-500/60",
    dot: "bg-orange-500",
  },
  medium: {
    bg: "bg-amber-600/15",
    text: "text-amber-300",
    border: "border-amber-500/50",
    dot: "bg-amber-500",
  },
  low: {
    bg: "bg-sky-600/15",
    text: "text-sky-300",
    border: "border-sky-500/50",
    dot: "bg-sky-500",
  },
  info: {
    bg: "bg-slate-700/40",
    text: "text-slate-300",
    border: "border-slate-500/50",
    dot: "bg-slate-500",
  },
};

export const DECISION_COLORS: Record<
  Decision,
  { bg: string; text: string }
> = {
  block: { bg: "bg-red-950/50", text: "text-red-400" },
  escalate: { bg: "bg-orange-950/50", text: "text-orange-400" },
  approve: { bg: "bg-green-950/50", text: "text-green-400" },
};

export const OWNER_LABELS: Record<Owner, string> = {
  legal: "Legal",
  finance: "Finance",
  procurement: "Procurement",
  security: "Security",
  compliance: "Compliance",
  executive: "Executive",
};

export const CLAUSE_TYPE_LABELS: Record<ClauseType, string> = {
  liability: "Liability",
  indemnification: "Indemnification",
  data_protection: "Data Protection",
  termination: "Termination",
  payment: "Payment",
  confidentiality: "Confidentiality",
  ip_rights: "IP Rights",
  service_level: "Service Level",
  force_majeure: "Force Majeure",
  governing_law: "Governing Law",
  insurance: "Insurance",
  warranty: "Warranty",
  audit_rights: "Audit Rights",
  subcontracting: "Subcontracting",
  other: "Other",
};

export const CATEGORY_LABELS: Record<string, string> = {
  data_protection: "Data Protection",
  security: "Security",
  liability: "Liability",
  contract_formation: "Contract Formation",
  confidentiality: "Confidentiality",
  payment: "Payment Terms",
  ip_rights: "IP Rights",
  termination: "Termination",
  indemnification: "Indemnification",
  service_level: "Service Level",
  governing_law: "Governing Law",
  insurance: "Insurance",
  warranty: "Warranty",
  audit_rights: "Audit Rights",
  subcontracting: "Subcontracting",
  force_majeure: "Force Majeure",
  other: "Other",
};

export const STANDARD_LABELS: Record<string, string> = {
  GDPR: "GDPR",
  DPDPA: "DPDPA 2023",
  CCPA: "CCPA/CPRA",
  HIPAA: "HIPAA",
  PCI_DSS: "PCI DSS",
  FERPA: "FERPA",
  GLBA: "GLBA",
  ISO27001: "ISO 27001",
  SOC2: "SOC 2",
  NIST_CSF: "NIST CSF 2.0",
  SOX: "SOX",
  FedRAMP: "FedRAMP",
  IND_CONTRACT: "Indian Contract Act 1872",
  IT_ACT: "IT Act 2000",
};

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function confidenceBar(confidence: number): {
  color: string;
  width: number;
} {
  return {
    width: Math.round(confidence * 100),
    color:
      confidence >= 0.8
        ? "bg-green-500"
        : confidence >= 0.6
          ? "bg-yellow-500"
          : "bg-red-500",
  };
}

export function riskSeverityScore(level: RiskLevel): number {
  const map: Record<RiskLevel, number> = {
    critical: 4,
    high: 3,
    medium: 2,
    low: 1,
    info: 0,
  };
  return map[level];
}

// ── Clause Gutter Colors ──────────────────────────────────────────

export const CLAUSE_TYPE_COLORS: Record<ClauseType, { bg: string; text: string }> = {
  liability: { bg: "bg-red-500/10", text: "text-red-500" },
  indemnification: { bg: "bg-orange-500/10", text: "text-orange-500" },
  data_protection: { bg: "bg-blue-500/10", text: "text-blue-500" },
  termination: { bg: "bg-rose-500/10", text: "text-rose-500" },
  payment: { bg: "bg-emerald-500/10", text: "text-emerald-500" },
  confidentiality: { bg: "bg-violet-500/10", text: "text-violet-500" },
  ip_rights: { bg: "bg-purple-500/10", text: "text-purple-500" },
  service_level: { bg: "bg-cyan-500/10", text: "text-cyan-500" },
  force_majeure: { bg: "bg-amber-500/10", text: "text-amber-500" },
  governing_law: { bg: "bg-indigo-500/10", text: "text-indigo-500" },
  insurance: { bg: "bg-green-500/10", text: "text-green-500" },
  warranty: { bg: "bg-teal-500/10", text: "text-teal-500" },
  audit_rights: { bg: "bg-sky-500/10", text: "text-sky-500" },
  subcontracting: { bg: "bg-slate-500/10", text: "text-slate-500" },
  other: { bg: "bg-gray-500/10", text: "text-gray-500" },
};

export const CLAUSE_TYPE_BORDER_COLORS: Record<ClauseType, string> = {
  liability: "border-l-red-500",
  indemnification: "border-l-orange-500",
  data_protection: "border-l-blue-500",
  termination: "border-l-rose-500",
  payment: "border-l-emerald-500",
  confidentiality: "border-l-violet-500",
  ip_rights: "border-l-purple-500",
  service_level: "border-l-cyan-500",
  force_majeure: "border-l-amber-500",
  governing_law: "border-l-indigo-500",
  insurance: "border-l-green-500",
  warranty: "border-l-teal-500",
  audit_rights: "border-l-sky-500",
  subcontracting: "border-l-slate-500",
  other: "border-l-gray-500",
};

// ── Confidence Helpers ────────────────────────────────────────────

export function confidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "text-green-600 dark:text-green-400";
  if (confidence >= 0.6) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

export function confidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return "High";
  if (confidence >= 0.6) return "Medium";
  return "Low";
}

// ── Flag Severity Colors ──────────────────────────────────────────

export type FlagSeverity = "block" | "warn" | "info";

export const FLAG_SEVERITY_COLORS: Record<
  FlagSeverity,
  { bg: string; text: string; border: string }
> = {
  block: {
    bg: "bg-red-50 dark:bg-red-950/20",
    text: "text-red-600 dark:text-red-400",
    border: "border-red-200 dark:border-red-900",
  },
  warn: {
    bg: "bg-amber-50 dark:bg-amber-950/20",
    text: "text-amber-600 dark:text-amber-400",
    border: "border-amber-200 dark:border-amber-900",
  },
  info: {
    bg: "bg-sky-50 dark:bg-sky-950/20",
    text: "text-sky-600 dark:text-sky-400",
    border: "border-sky-200 dark:border-sky-900",
  },
};

// ── Verification Status ───────────────────────────────────────────

export const VERIFICATION_STATUS_COLORS: Record<
  string,
  { bg: string; text: string; border: string }
> = {
  verified: {
    bg: "bg-emerald-50 dark:bg-emerald-950/20",
    text: "text-emerald-600 dark:text-emerald-400",
    border: "border-emerald-200 dark:border-emerald-900",
  },
  unverified: {
    bg: "bg-red-50 dark:bg-red-950/20",
    text: "text-red-600 dark:text-red-400",
    border: "border-red-200 dark:border-red-900",
  },
};

export const VERIFICATION_STATUS_LABELS: Record<string, string> = {
  verified: "Verified",
  unverified: "Needs Review",
};

// ── Retrieval Source Colors ───────────────────────────────────────

export const RETRIEVAL_SOURCE_COLORS: Record<string, { bg: string; text: string }> = {
  faiss: {
    bg: "bg-indigo-100 dark:bg-indigo-950/30",
    text: "text-indigo-600 dark:text-indigo-400",
  },
  bm25: {
    bg: "bg-amber-100 dark:bg-amber-950/30",
    text: "text-amber-600 dark:text-amber-400",
  },
};
