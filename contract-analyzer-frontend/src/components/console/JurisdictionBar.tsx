"use client";

import { Scale, MapPin, Building2, FileText } from "lucide-react";
import type { JurisdictionAnalysis } from "@/lib/types";

interface JurisdictionBarProps {
  jurisdiction: JurisdictionAnalysis;
}

export function JurisdictionBar({ jurisdiction }: JurisdictionBarProps) {
  const hasData =
    jurisdiction.governing_law ||
    jurisdiction.contract_type ||
    jurisdiction.party_a_name ||
    jurisdiction.subject_matter;

  if (!hasData) return null;

  function locationText(name: string, location: string) {
    if (!name && !location) return null;
    if (name && location) return `${name} (${location})`;
    return name || location;
  }

  const partyText = locationText(
    jurisdiction.party_a_name,
    jurisdiction.party_a_location
  );
  const partyBText = locationText(
    jurisdiction.party_b_name,
    jurisdiction.party_b_location
  );
  const parties =
    partyText && partyBText ? `${partyText} → ${partyBText}` : partyText || partyBText;

  return (
    <div className="flex items-center gap-2 px-4 h-10 shrink-0 border-b border-border bg-muted/30 overflow-x-auto">
      {jurisdiction.governing_law && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
          <Scale className="h-3.5 w-3.5" />
          <span>{jurisdiction.governing_law}</span>
        </div>
      )}
      {jurisdiction.contract_type && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
          <span className="text-border">|</span>
          <FileText className="h-3.5 w-3.5" />
          <span>{jurisdiction.contract_type.replace(/_/g, " ")}</span>
        </div>
      )}
      {parties && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
          <span className="text-border">|</span>
          <Building2 className="h-3.5 w-3.5" />
          <span className="truncate max-w-[300px]">{parties}</span>
        </div>
      )}
      {jurisdiction.subject_matter && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
          <span className="text-border">|</span>
          <MapPin className="h-3.5 w-3.5" />
          <span className="truncate max-w-[200px]">
            {jurisdiction.subject_matter}
          </span>
        </div>
      )}
    </div>
  );
}
