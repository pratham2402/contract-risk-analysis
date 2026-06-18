"use client";

import { motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { useStore } from "@/stores";
import { StageNode } from "./StageNode";

const PIPELINE_STAGES = [
  "parsing",
  "classifying",
  "risk_evaluation",
  "verifying",
  "decision_generation",
  "complete",
];

export function LangGraphDAG() {
  const stages = useStore((s) => s.stages);
  const currentStage = useStore((s) => s.currentStage);

  return (
    <div className="flex items-center justify-center gap-0 py-4 overflow-x-auto">
      {PIPELINE_STAGES.map((key, i) => {
        const isLast = i === PIPELINE_STAGES.length - 1;

        return (
          <div key={key} className="flex items-center gap-0">
            <StageNode
              stageKey={key}
              status={stages[key]}
              isActive={currentStage === key}
              delay={i * 0.1}
            />
            {!isLast && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.4 }}
                transition={{ delay: i * 0.1 + 0.15 }}
              >
                <ChevronRight className="h-4 w-4 text-slate-400 shrink-0" />
              </motion.div>
            )}
          </div>
        );
      })}
    </div>
  );
}
