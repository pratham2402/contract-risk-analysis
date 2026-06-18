export type RiskLevel = "critical" | "high" | "medium" | "low" | "info";

export type Decision = "approve" | "escalate" | "block";

export type Owner = "legal" | "finance" | "procurement" | "security" | "compliance" | "executive";

export type ClauseType =
  | "liability"
  | "indemnification"
  | "data_protection"
  | "termination"
  | "payment"
  | "confidentiality"
  | "ip_rights"
  | "service_level"
  | "force_majeure"
  | "governing_law"
  | "insurance"
  | "warranty"
  | "audit_rights"
  | "subcontracting"
  | "other";

export type FindingCategory =
  | "data_protection"
  | "security"
  | "liability"
  | "indemnification"
  | "contract_formation"
  | "breach_of_contract"
  | "termination"
  | "confidentiality"
  | "ip_rights"
  | "service_level"
  | "financial_reporting"
  | "payment_security"
  | "healthcare_privacy"
  | "education_privacy"
  | "operational"
  | "governance"
  | "privacy"
  | "other";

export interface StandardRef {
  standard: string;
  article: string | null;
  clause: string | null;
  description: string;
  relevance_score: number;
}

export interface ParsedClause {
  id: string;
  clause_type: ClauseType;
  clause_number: string | null;
  title: string;
  text: string;
  start_line: number;
  end_line: number;
  metadata: Record<string, unknown>;
}

export interface Finding {
  id: string;
  clause_id: string | null;
  issue_description: string;
  risk_level: RiskLevel;
  category: string;
  referenced_standards: StandardRef[];
  explanation: string;
  reasoning_trace: string;
  confidence: number;
  metadata: Record<string, unknown>;
}

export interface Recommendation {
  id: string;
  finding_id: string;
  issue_description: string;
  risk_level: RiskLevel;
  referenced_standards: StandardRef[];
  explanation: string;
  reasoning_trace: string;
  recommended_action: string;
  negotiation_suggestion: string | null;
  owner: Owner;
  priority: number;
  decision: Decision;
  metadata: Record<string, unknown>;
}

export interface JurisdictionAnalysis {
  governing_law: string;
  party_a_name: string;
  party_a_location: string;
  party_b_name: string;
  party_b_location: string;
  data_subject_locations: string;
  contract_type: string;
  subject_matter: string;
}

export interface StandardsApplicability {
  standard: string;
  applies: boolean;
  reason: string;
}

export interface AuditTrailEntry {
  timestamp: string;
  stage: string;
  action: string;
  clause_count?: number;
  finding_count?: number;
  recommendation_count?: number;
  standards_consulted?: number;
  contract_type?: string;
  errors?: string[];
}

export interface AnalysisSummary {
  total_clauses: number;
  total_findings: number;
  total_recommendations: number;
  risk_counts: Record<RiskLevel, number>;
  decision_counts: Record<Decision, number>;
}

export interface AnalysisResponse {
  analysis_id: string;
  status: string;
  clause_count: number;
  finding_count: number;
  recommendation_count: number;
  total_duration_ms: number;
  contract_text?: string;
  summary: AnalysisSummary;
  clauses: ParsedClause[];
  findings: Finding[];
  recommendations: Recommendation[];
  jurisdiction_analysis: JurisdictionAnalysis;
  standards_applicability: StandardsApplicability[];
  audit_trail: AuditTrailEntry[];
  verification_report: VerificationReport | null;
  escalation_tickets: EscalationTicket[];
  agent_trace: AgentTraceEntry[];
  retrieved_evidence: RetrievedChunk[];
}

export interface ContractListItem {
  id: string;
  name: string;
  status: string;
  created_at: string;
  total_duration_ms: number;
  clause_count: number;
  finding_count: number;
  recommendation_count: number;
  summary: AnalysisSummary | null;
}

export interface ContractDetail extends ContractListItem {
  contract_text: string;
  analysis: AnalysisResponse;
}

// ── Verification ────────────────────────────────────────────

export interface VerificationFlag {
  finding_id: string;
  flag_type: "hallucinated_citation" | "unsupported_citation"
    | "disconnected_reasoning" | "risk_level_mismatch" | "generic_exclusion";
  severity: "block" | "warn" | "info";
  detail: string;
}

export interface VerificationReport {
  verified: boolean;
  total_findings: number;
  total_citations: number;
  flags: VerificationFlag[];
  hallucination_count: number;
  adjusted_confidence: number;
}

// ── Escalation ──────────────────────────────────────────────

export interface EscalationTicket {
  ticket_id: string;
  reason: string;
  clause_id: string | null;
  standard: string | null;
  severity: string;
  timestamp: string;
  resolved?: boolean;
  resolution?: { decision: string; timestamp: string };
}

// ── Agent Trace ─────────────────────────────────────────────

export interface ToolCallEntry {
  tool: string;
  input: string;
  timestamp: string;
}

export interface RetrievedChunk {
  source: "faiss" | "bm25";
  standard: string;
  article: string | null;
  snippet: string;
  relevance_score: number;
}

export interface AgentTraceEntry {
  timestamp: string;
  stage: string;
  action: string;
  specialist?: string;
  reaact_iteration?: number;
  tool_calls?: ToolCallEntry[];
  retrieved_chunks?: RetrievedChunk[];
}

// ── SSE Events ──────────────────────────────────────────────

export interface SSEStageEvent {
  type: "stage";
  stage: string;
  status: "started" | "in_progress" | "completed" | "failed";
  timestamp: string;
  message: string;
}

export interface SSETraceEvent {
  type: "trace";
  trace: AgentTraceEntry;
}

export interface SSEErrorEvent {
  type: "error";
  stage: string;
  message: string;
}

export type SSEEvent = SSEStageEvent | SSETraceEvent | SSEErrorEvent;
