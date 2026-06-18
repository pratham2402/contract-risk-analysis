"use client";

import { useEffect, useState } from "react";
import { ArrowLeft, History } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LandingPage } from "@/components/LandingPage";
import { ContractQueue } from "@/components/console/ContractQueue";
import { JurisdictionBar } from "@/components/console/JurisdictionBar";
import { OverviewTab } from "@/components/console/OverviewTab";
import { FindingsTab } from "@/components/console/FindingsTab";
import { RecommendationsTab } from "@/components/console/RecommendationsTab";
import { AuditStandardsTab } from "@/components/console/AuditStandardsTab";
import { AnalysisLoadingOverlay } from "@/components/console/AnalysisLoadingOverlay";
import { AnalysisSkeleton } from "@/components/console/AnalysisSkeleton";
import { ErrorBanner } from "@/components/console/ErrorBanner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useAnalysis } from "@/hooks/useAnalysis";

export default function ConsolePage() {
  const analysis = useAnalysis();

  useEffect(() => {
    analysis.refreshList();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const hasData = analysis.currentAnalysis !== null;

  const viewState = analysis.isAnalyzing
    ? "loading"
    : analysis.isLoadingDetail
      ? "loading_detail"
      : hasData
        ? "results"
        : "landing";

  // ── Landing ──────────────────────────────────────────────
  if (viewState === "landing") {
    return (
      <LandingPage
        onSubmit={analysis.handleSubmit}
        isAnalyzing={analysis.isAnalyzing}
      />
    );
  }

  // ── Loading ──────────────────────────────────────────────
  if (viewState === "loading") {
    return (
      <div className="flex flex-col h-screen bg-background">
        <ErrorBanner error={analysis.error} onDismiss={analysis.dismissError} />
        <AnalysisLoadingOverlay isAnalyzing={true} />
      </div>
    );
  }

  if (viewState === "loading_detail") {
    return (
      <div className="flex flex-col h-screen bg-background">
        <ErrorBanner error={analysis.error} onDismiss={analysis.dismissError} />
        <div className="flex-1 p-4">
          <AnalysisSkeleton />
        </div>
      </div>
    );
  }

  // ── Results ──────────────────────────────────────────────
  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Top bar */}
      <header className="shrink-0 flex items-center justify-between border-b border-border px-4 h-12">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => window.location.reload()}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <span className="text-base font-bold tracking-tight text-primary">
            COMPLIANCE ANALYZER
          </span>
        </div>

        <div className="flex items-center gap-1">
          {/* Past analyses drawer */}
          <Sheet>
            <SheetTrigger
              render={
                <Button variant="ghost" size="icon" className="h-8 w-8" tabIndex={-1} />
              }
            >
              <History className="h-4 w-4" />
            </SheetTrigger>
            <SheetContent side="right" className="w-80">
              <SheetHeader>
                <SheetTitle>Past Analyses</SheetTitle>
              </SheetHeader>
              <div className="mt-4">
                <ScrollArea className="h-[calc(100vh-8rem)]">
                  <ContractQueue
                    analyses={analysis.pastAnalyses}
                    selectedId={analysis.selectedAnalysisId}
                    onSelect={(id) => analysis.handleSelectAnalysis(id)}
                  />
                </ScrollArea>
              </div>
            </SheetContent>
          </Sheet>

          <ThemeToggle />
        </div>
      </header>

      {/* Error banner */}
      <ErrorBanner error={analysis.error} onDismiss={analysis.dismissError} />

      {/* Jurisdiction bar */}
      {analysis.currentAnalysis && (
        <div className="shrink-0">
          <JurisdictionBar
            jurisdiction={analysis.currentAnalysis.jurisdiction_analysis}
          />
        </div>
      )}

      {/* Tabs */}
      {analysis.currentAnalysis && (
        <Tabs
          value={analysis.mainTab}
          onValueChange={(v) =>
            analysis.setMainTab(v as typeof analysis.mainTab)
          }
          className="flex flex-col flex-1 overflow-hidden"
        >
          <TabsList className="mx-4 mt-2 shrink-0 grid w-[calc(100%-2rem)] grid-cols-4">
            <TabsTrigger value="overview" className="text-sm">
              Overview
            </TabsTrigger>
            <TabsTrigger value="findings" className="text-sm">
              Findings
            </TabsTrigger>
            <TabsTrigger value="actions" className="text-sm">
              Actions
            </TabsTrigger>
            <TabsTrigger value="audit-standards" className="text-sm">
              Audit &amp; Standards
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-hidden mt-2">
            <TabsContent
              value="overview"
              className="h-full mt-0 data-[state=inactive]:hidden"
            >
              <OverviewTab
                analysis={analysis.currentAnalysis}
                contractText={analysis.contractText}
              />
            </TabsContent>

            <TabsContent
              value="findings"
              className="h-full mt-0 data-[state=inactive]:hidden"
            >
              <ScrollArea className="h-full">
                <div className="px-4 pb-4">
                  <FindingsTab
                    findings={analysis.currentAnalysis.findings}
                    clauses={analysis.currentAnalysis.clauses}
                    filter={analysis.findingsFilter}
                    onFilterChange={analysis.setFindingsFilter}
                    onClearFilter={analysis.clearFindingsFilter}
                    onFindingClick={analysis.setSelectedClauseId}
                  />
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent
              value="actions"
              className="h-full mt-0 data-[state=inactive]:hidden"
            >
              <ScrollArea className="h-full">
                <div className="px-4 pb-4">
                  <RecommendationsTab
                    recommendations={analysis.currentAnalysis.recommendations}
                    findings={analysis.currentAnalysis.findings}
                    view={analysis.recommendationsView}
                    onViewChange={analysis.setRecommendationsView}
                  />
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent
              value="audit-standards"
              className="h-full mt-0 data-[state=inactive]:hidden"
            >
              <AuditStandardsTab
                auditTrail={analysis.currentAnalysis.audit_trail}
                totalDurationMs={analysis.currentAnalysis.total_duration_ms}
                standardsApplicability={
                  analysis.currentAnalysis.standards_applicability
                }
              />
            </TabsContent>
          </div>
        </Tabs>
      )}
    </div>
  );
}
