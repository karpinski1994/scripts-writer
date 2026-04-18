"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useEffect } from "react";
import { api } from "@/lib/api";
import type { ProjectDetail } from "@/types/project";
import type { ScriptVersion } from "@/types/script";
import { useEditorStore } from "@/stores/editor-store";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2 } from "lucide-react";
import { ScriptEditor } from "@/components/editor/script-editor";
import { VersionDropdown } from "@/components/editor/version-dropdown";

export default function EditorPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const { setCurrentVersionId, setVersionNumber, setContent, markClean, reset, save, setProjectId } =
    useEditorStore();

  useEffect(() => {
    if (id) {
      setProjectId(id);
    }
  }, [id, setProjectId]);

  const { data: project, isLoading: projectLoading } = useQuery<ProjectDetail>({
    queryKey: ["project", id],
    queryFn: () => api.get<ProjectDetail>(`/api/v1/projects/${id}`),
    enabled: !!id,
  });

  const { data: versions, isLoading: versionsLoading } = useQuery<ScriptVersion[]>({
    queryKey: ["scripts", id],
    queryFn: () => api.get<ScriptVersion[]>(`/api/v1/projects/${id}/scripts`),
    enabled: !!id,
  });

  useEffect(() => {
    if (versions && versions.length > 0) {
      const latest = versions[0];
      const store = useEditorStore.getState();
      if (store.currentVersionId !== latest.id) {
        setCurrentVersionId(latest.id);
        setVersionNumber(latest.version_number);
        setContent(latest.content);
        markClean();
      }
    }
  }, [versions, setCurrentVersionId, setVersionNumber, setContent, markClean]);

  useEffect(() => {
    return () => {
      const store = useEditorStore.getState();
      if (store.isDirty) {
        save();
      }
      reset();
    };
  }, [reset, save]);

  if (projectLoading || versionsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="icon-sm">
          <Link href={`/projects/${id}`}>
            <ArrowLeft />
          </Link>
        </Button>
        <h1 className="text-xl font-bold tracking-tight">
          {project?.name ?? "Script Editor"}
        </h1>
        <VersionDropdown projectId={id} />
      </div>

      {!versions || versions.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24">
          <p className="text-lg text-muted-foreground">No script versions yet</p>
          <p className="text-sm text-muted-foreground">
            Generate a script from the pipeline first.
          </p>
          <Button asChild variant="outline">
            <Link href={`/projects/${id}`}>
              Back to Pipeline
            </Link>
          </Button>
        </div>
      ) : (
        <ScriptEditor projectId={id} />
      )}
    </div>
  );
}
