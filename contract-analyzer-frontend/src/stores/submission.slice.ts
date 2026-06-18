import type { StateCreator } from "zustand";

export type JobStatus = "idle" | "submitting" | "running" | "completed" | "failed";

export interface SubmissionSlice {
  inputName: string;
  inputText: string;
  inputFile: File | undefined;
  jobId: string | null;
  jobStatus: JobStatus;
  error: string | null;

  setInput: (name: string, text: string, file?: File) => void;
  setSubmitting: (jobId: string) => void;
  setJobRunning: () => void;
  setJobCompleted: () => void;
  setJobFailed: (error: string) => void;
  cancelJob: () => void;
  reset: () => void;
}

export const createSubmissionSlice: StateCreator<
  SubmissionSlice,
  [],
  [],
  SubmissionSlice
> = (set) => ({
  inputName: "",
  inputText: "",
  inputFile: undefined,
  jobId: null,
  jobStatus: "idle",
  error: null,

  setInput: (name, text, file) =>
    set({ inputName: name, inputText: text, inputFile: file ?? undefined }),

  setSubmitting: (jobId) =>
    set({
      jobId,
      jobStatus: "submitting",
      error: null,
    }),

  setJobRunning: () => set({ jobStatus: "running" }),

  setJobCompleted: () => set({ jobStatus: "completed" }),

  setJobFailed: (error) =>
    set({
      jobStatus: "failed",
      error,
    }),

  cancelJob: () =>
    set({
      jobId: null,
      jobStatus: "idle",
      error: null,
    }),

  reset: () =>
    set({
      inputName: "",
      inputText: "",
      inputFile: undefined,
      jobId: null,
      jobStatus: "idle",
      error: null,
    }),
});
