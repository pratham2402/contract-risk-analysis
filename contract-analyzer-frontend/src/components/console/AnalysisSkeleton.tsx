"use client";

import { Skeleton } from "@/components/ui/skeleton";

export function AnalysisSkeleton() {
  return (
    <div className="p-6 space-y-6">
      {/* Jurisdiction bar skeleton */}
      <div className="flex gap-2">
        <Skeleton className="h-5 w-24 rounded-full" />
        <Skeleton className="h-5 w-20 rounded-full" />
        <Skeleton className="h-5 w-28 rounded-full" />
      </div>

      {/* Tab bar skeleton */}
      <Skeleton className="h-9 w-80" />

      {/* Stat cards row */}
      <div className="grid grid-cols-3 gap-4">
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
      </div>

      {/* Risk bar skeleton */}
      <Skeleton className="h-4 w-full rounded-full" />

      {/* Contract text skeleton */}
      <div className="space-y-2 rounded-xl border border-border p-4">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-4 w-8 shrink-0" />
            <Skeleton
              className="h-4 rounded"
              style={{ width: `${40 + Math.random() * 60}%` }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
