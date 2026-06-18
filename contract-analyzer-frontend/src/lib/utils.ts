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
