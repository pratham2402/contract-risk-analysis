import type { StateCreator } from "zustand";
import type {
  AnalysisResponse,
  ContractListItem,
  RiskLevel,
} from "@/lib/types";

export type MainTab = "overview" | "findings" | "actions" | "audit-standards";
export type RecommendationsView = "decision" | "owner";

export interface FindingsFilter {
  riskLevels: RiskLevel[];
  category: string;
  standard: string;
  search: string;
}

export interface AnalysisSlice {
  analysis: AnalysisResponse | null;
  contractText: string;
  pastAnalyses: ContractListItem[];
  mainTab: MainTab;
  selectedClauseId: string | null;
  selectedFindingId: string | null;
  findingsFilter: FindingsFilter;
  recommendationsView: RecommendationsView;
  isLoadingDetail: boolean;
  error: string | null;

  loadAnalysis: (analysis: AnalysisResponse, text: string) => void;
  selectClause: (id: string | null) => void;
  selectFinding: (id: string | null) => void;
  setMainTab: (tab: MainTab) => void;
  setFindingsFilter: (partial: Partial<FindingsFilter>) => void;
  clearFindingsFilter: () => void;
  setRecommendationsView: (view: RecommendationsView) => void;
  setPastAnalyses: (list: ContractListItem[]) => void;
  dismissError: () => void;
}

const defaultFilter: FindingsFilter = {
  riskLevels: [],
  category: "",
  standard: "",
  search: "",
};

export const createAnalysisSlice: StateCreator<AnalysisSlice> = (set) => ({
  analysis: null,
  contractText: "",
  pastAnalyses: [],
  mainTab: "overview",
  selectedClauseId: null,
  selectedFindingId: null,
  findingsFilter: defaultFilter,
  recommendationsView: "decision",
  isLoadingDetail: false,
  error: null,

  loadAnalysis: (analysis, text) =>
    set({
      analysis,
      contractText: text || analysis.contract_text || "",
      mainTab: "overview",
      selectedClauseId: null,
      selectedFindingId: null,
      findingsFilter: defaultFilter,
      isLoadingDetail: false,
      error: null,
    }),

  selectClause: (id) =>
    set({ selectedClauseId: id, selectedFindingId: null }),

  selectFinding: (id) =>
    set({ selectedFindingId: id, selectedClauseId: null }),

  setMainTab: (tab) => set({ mainTab: tab }),

  setFindingsFilter: (partial) =>
    set((s) => ({ findingsFilter: { ...s.findingsFilter, ...partial } })),

  clearFindingsFilter: () => set({ findingsFilter: defaultFilter }),

  setRecommendationsView: (view) => set({ recommendationsView: view }),

  setPastAnalyses: (list) => set({ pastAnalyses: list }),

  dismissError: () => set({ error: null }),
});
