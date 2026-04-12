"use client";

import { useState } from "react";
import { useNotebookLMStore } from "@/stores/notebooklm-store";
import { Button } from "@/components/ui/button";
import { Loader2, BookOpen, ChevronDown, ChevronRight } from "lucide-react";

interface NotebookLMContextProps {
  stepType: string;
  projectId: string;
}

export function NotebookLMContext({ stepType, projectId }: NotebookLMContextProps) {
  const { connectedNotebook, stepContexts, isQuerying, fetchStepContext } = useNotebookLMStore();
  const [expanded, setExpanded] = useState(false);
  const context = stepContexts[stepType];

  if (!connectedNotebook) return null;

  const handleFetch = async () => {
    await fetchStepContext(projectId, stepType);
    setExpanded(true);
  };

  return (
    <div className="rounded-md border">
      <button
        className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-muted transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? <ChevronDown className="size-4" /> : <ChevronRight className="size-4" />}
        <BookOpen className="size-4 text-muted-foreground" />
        <span className="font-medium">NotebookLM Context</span>
        <span className="ml-auto text-xs text-muted-foreground">{connectedNotebook.notebook_title}</span>
      </button>

      {expanded && (
        <div className="border-t px-3 py-2 space-y-2">
          {context ? (
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">{context}</p>
          ) : (
            <div className="flex items-center gap-2">
              <p className="text-sm text-muted-foreground">No context loaded for this step.</p>
              <Button variant="outline" size="sm" onClick={handleFetch} disabled={isQuerying}>
                {isQuerying && <Loader2 className="size-3 animate-spin" />}
                Query
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
