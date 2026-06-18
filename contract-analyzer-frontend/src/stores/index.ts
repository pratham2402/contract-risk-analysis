"use client";

import { create } from "zustand";
import {
  createSubmissionSlice,
  type SubmissionSlice,
} from "./submission.slice";
import {
  createAnalysisSlice,
  type AnalysisSlice,
} from "./analysis.slice";
import {
  createLiveTraceSlice,
  type LiveTraceSlice,
} from "./livetrace.slice";

export type AppStore = SubmissionSlice & AnalysisSlice & LiveTraceSlice;

export const useStore = create<AppStore>()((...args) => ({
  ...createSubmissionSlice(...args),
  ...createAnalysisSlice(...args),
  ...createLiveTraceSlice(...args),
}));
