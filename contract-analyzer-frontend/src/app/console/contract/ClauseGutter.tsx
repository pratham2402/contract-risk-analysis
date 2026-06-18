"use client";

import { cn, CLAUSE_TYPE_BORDER_COLORS } from "@/lib/utils";
import type { ParsedClause, ClauseType } from "@/lib/types";

interface ClauseGutterProps {
  clause: ParsedClause;
  isSelected: boolean;
  onClick?: () => void;
}

export function ClauseGutter({
  clause,
  isSelected,
  onClick,
}: ClauseGutterProps) {
  const borderColor =
    CLAUSE_TYPE_BORDER_COLORS[clause.clause_type as ClauseType] ??
    CLAUSE_TYPE_BORDER_COLORS.other;

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-[6px] shrink-0 transition-all hover:w-[10px]",
        borderColor,
        "border-l-[3px]",
        isSelected && "w-[10px] border-l-[4px] bg-primary/10"
      )}
      title={`${clause.clause_type}: ${clause.title}`}
    />
  );
}
