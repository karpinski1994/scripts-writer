"use client";

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "./use-websocket";
import { usePipelineStore } from "@/stores/pipeline-store";

export function useAgentStream(projectId: string | null) {
  const { lastEvent, connectionStatus } = useWebSocket(projectId);
  const queryClient = useQueryClient();
  const { setStepRunning, setStepCompleted, setStepFailed } =
    usePipelineStore();

  useEffect(() => {
    if (!lastEvent || !projectId) return;

    const event = lastEvent.event as string;
    const stepType = lastEvent.step_type as string;

    if (event === "agent_start") {
      setStepRunning(stepType);
    } else if (event === "agent_complete") {
      setStepCompleted(stepType, lastEvent.output_data);
      queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
    } else if (event === "agent_failed") {
      setStepFailed(stepType);
      queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
    }
  }, [lastEvent, projectId, setStepRunning, setStepCompleted, setStepFailed, queryClient]);

  return { connectionStatus };
}
