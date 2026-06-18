"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";
import { listAnalyses, submitContract } from "@/lib/api";
import type { AnalysisResponse, ContractListItem, RiskLevel } from "@/lib/types";

interface FindingsFilter {
  riskLevels: RiskLevel[];
  category: string;
  standard: string;
  search: string;
}

type RecommendationsView = "decision" | "owner";
type MainTab = "overview" | "findings" | "actions" | "audit-standards";

interface UseAnalysisReturn {
  currentAnalysis: AnalysisResponse | null;
  contractText: string;
  pastAnalyses: ContractListItem[];
  isLoading: boolean;
  isAnalyzing: boolean;
  isLoadingDetail: boolean;
  error: string | null;
  selectedClauseId: string | null;
  findingsFilter: FindingsFilter;
  recommendationsView: RecommendationsView;
  mainTab: MainTab;
  selectedAnalysisId: string | null;
  setSelectedClauseId: (id: string | null) => void;
  setFindingsFilter: (filter: Partial<FindingsFilter>) => void;
  clearFindingsFilter: () => void;
  setRecommendationsView: (view: RecommendationsView) => void;
  setMainTab: (tab: MainTab) => void;
  handleSubmit: (name: string, text: string, file?: File) => Promise<void>;
  handleSelectAnalysis: (id: string) => Promise<void>;
  refreshList: () => Promise<void>;
  dismissError: () => void;
}

const defaultFilter: FindingsFilter = {
  riskLevels: [],
  category: "",
  standard: "",
  search: "",
};

export function useAnalysis(): UseAnalysisReturn {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [contractText, setContractText] = useState("");
  const [pastAnalyses, setPastAnalyses] = useState<ContractListItem[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedClauseId, setSelectedClauseId] = useState<string | null>(null);
  const [findingsFilter, setFindingsFilter] = useState<FindingsFilter>(defaultFilter);
  const [recommendationsView, setRecommendationsView] = useState<RecommendationsView>("decision");
  const [mainTab, setMainTab] = useState<MainTab>("overview");
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null);

  const isLoading = isAnalyzing || isLoadingDetail;

  const refreshList = useCallback(async () => {
    try {
      const list = await listAnalyses();
      setPastAnalyses(list);
    } catch {
      // silently fail - list is non-critical
    }
  }, []);

  const handleSubmit = useCallback(
    async (name: string, text: string, file?: File) => {
      setIsAnalyzing(true);
      setError(null);
      try {
        const result = await submitContract(name, text, file);
        setCurrentAnalysis(result);
        setContractText(text || result.contract_text || "");
        setSelectedAnalysisId(result.analysis_id);
        setSelectedClauseId(null);
        setFindingsFilter(defaultFilter);
        setMainTab("overview");
        await refreshList();
      } catch (e) {
        const msg = e instanceof Error ? e.message : "An unexpected error occurred";
        setError(msg);
        toast.error(msg);
      } finally {
        setIsAnalyzing(false);
      }
    },
    [refreshList]
  );

  const handleSelectAnalysis = useCallback(
    async (id: string) => {
      setSelectedAnalysisId(id);
      setError(null);
      setIsLoadingDetail(true);
      try {
        const { getAnalysis } = await import("@/lib/api");
        const detail = await getAnalysis(id);
        if (detail.analysis) {
          setCurrentAnalysis(detail.analysis);
        } else {
          setCurrentAnalysis(detail as unknown as AnalysisResponse);
        }
        setContractText(detail.contract_text || "");
        setMainTab("overview");
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to load analysis";
        setError(msg);
        toast.error(msg);
      } finally {
        setIsLoadingDetail(false);
      }
    },
    []
  );

  const clearFindingsFilter = useCallback(() => {
    setFindingsFilter(defaultFilter);
  }, []);

  const dismissError = useCallback(() => setError(null), []);

  return {
    currentAnalysis,
    contractText,
    pastAnalyses,
    isLoading,
    isAnalyzing,
    isLoadingDetail,
    error,
    selectedClauseId,
    findingsFilter,
    recommendationsView,
    mainTab,
    selectedAnalysisId,
    setSelectedClauseId,
    setFindingsFilter: (partial) =>
      setFindingsFilter((prev) => ({ ...prev, ...partial })),
    clearFindingsFilter,
    setRecommendationsView,
    setMainTab,
    handleSubmit,
    handleSelectAnalysis,
    refreshList,
    dismissError,
  };
}
