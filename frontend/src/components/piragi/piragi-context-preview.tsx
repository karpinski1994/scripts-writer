"use client";

import { usePiragiStore } from "@/stores/piragi-store";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FileText, Search, Loader2, Check } from "lucide-react";

interface PiragiContextPreviewProps {
  projectId: string;
  stepType: string;
}

export function PiragiContextPreview({ projectId, stepType }: PiragiContextPreviewProps) {
  const { connectedDocuments, stepContexts, isQuerying, queryDocuments, setStepContext } =
    usePiragiStore();

  const context = stepContexts[stepType];
  const isConnected = !!connectedDocuments?.document_paths;

  const handleQuery = async () => {
    const defaultQueries: Record<string, string> = {
      icp: "audience insights demographics pain points",
      hook: "effective hooks viral patterns",
      narrative: "story templates narrative patterns",
      retention: "retention techniques engagement",
      cta: "call to action urgency conversion",
    };
    const query = defaultQueries[stepType] || "relevant context";
    const result = await queryDocuments(projectId, query, stepType);
    if (result && result.results.length > 0) {
      const contextText = result.results.map((r) => r.chunk).join("\n\n");
      setStepContext(stepType, contextText);
    }
  };

  if (!isConnected) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <FileText className="h-4 w-4" />
          Piragi RAG Context
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2">
          {context ? (
            <Check className="h-4 w-4 text-green-600" />
          ) : (
            <div className="h-4 w-4" />
          )}
          <span className="text-sm">
            {context ? "Context available" : "No context loaded"}
          </span>
        </div>

        {context && (
          <div className="text-sm bg-muted p-2 rounded max-h-24 overflow-auto">
            <p className="font-medium text-xs text-muted-foreground mb-1">
              Context preview:
            </p>
            <p className="text-xs line-clamp-3">{context}</p>
          </div>
        )}

        <Button
          variant="outline"
          size="sm"
          onClick={handleQuery}
          disabled={isQuerying}
          className="w-full"
        >
          {isQuerying ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <Search className="h-4 w-4 mr-2" />
          )}
          Query for insights
        </Button>
      </CardContent>
    </Card>
  );
}