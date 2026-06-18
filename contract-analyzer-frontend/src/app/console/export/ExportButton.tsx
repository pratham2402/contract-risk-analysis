"use client";

import { useState } from "react";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ExportDialog } from "./ExportDialog";

export function ExportButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="h-7 w-7"
        onClick={() => setOpen(true)}
      >
        <Download className="h-4 w-4 text-slate-400" />
      </Button>
      <ExportDialog open={open} onClose={() => setOpen(false)} />
    </>
  );
}
