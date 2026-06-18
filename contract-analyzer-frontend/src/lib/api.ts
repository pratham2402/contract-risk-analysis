import type { AnalysisResponse, ContractDetail, ContractListItem } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function submitContract(
  name: string,
  text: string,
  file?: File
): Promise<AnalysisResponse> {
  if (file) {
    const form = new FormData();
    form.append("file", file);
    if (name) form.append("name", name);
    const res = await fetch(`${BASE}/analyze`, { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail ?? "Upload failed");
    }
    return res.json();
  }

  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name || "Unnamed Contract", text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail ?? "Analysis failed");
  }
  return res.json();
}

export async function listAnalyses(
  limit = 50,
  offset = 0
): Promise<ContractListItem[]> {
  const res = await fetch(`${BASE}/analyses?limit=${limit}&offset=${offset}`);
  if (!res.ok) return [];
  return res.json();
}

export async function getAnalysis(id: string): Promise<ContractDetail> {
  const res = await fetch(`${BASE}/analyses/${id}`);
  if (!res.ok) throw new Error("Analysis not found");
  return res.json();
}

// ── Async submission ─────────────────────────────────────────

export interface JobSubmitResponse {
  job_id: string;
  status: string;
  contract_name: string;
}

export interface JobStatusResponse {
  job_id: string;
  contract_name: string;
  status: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
  result: AnalysisResponse | null;
}

export async function submitAsync(
  name: string,
  text: string,
  file?: File
): Promise<JobSubmitResponse> {
  if (file) {
    const form = new FormData();
    form.append("file", file);
    if (name) form.append("name", name);
    const res = await fetch(`${BASE}/analyze/async`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail ?? "Upload failed");
    }
    return res.json();
  }

  const res = await fetch(`${BASE}/analyze/async`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name || "Unnamed Contract", text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Submission failed" }));
    throw new Error(err.detail ?? "Submission failed");
  }
  return res.json();
}

export async function getJobStatus(
  jobId: string
): Promise<JobStatusResponse> {
  const res = await fetch(`${BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export function connectJobStream(jobId: string): EventSource {
  const url = `${BASE}/jobs/${jobId}/stream`;
  return new EventSource(url);
}

export async function resolveTicket(
  analysisId: string,
  ticketId: string,
  decision: "approve" | "escalate" | "block"
): Promise<void> {
  const res = await fetch(
    `${BASE}/analyses/${analysisId}/tickets/${ticketId}/resolve`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Resolution failed" }));
    throw new Error(err.detail ?? "Resolution failed");
  }
}
