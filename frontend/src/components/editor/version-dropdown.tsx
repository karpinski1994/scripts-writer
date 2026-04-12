"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useEditorStore } from "@/stores/editor-store";
import type { ScriptVersion } from "@/types/script";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface VersionDropdownProps {
  projectId: string;
}

export function VersionDropdown({ projectId }: VersionDropdownProps) {
  const { currentVersionId, versionNumber, cancelPendingSave, setCurrentVersionId, setVersionNumber, setContent, markClean } =
    useEditorStore();

  const { data: versions } = useQuery<ScriptVersion[]>({
    queryKey: ["scripts", projectId],
    queryFn: () => api.get<ScriptVersion[]>(`/api/v1/projects/${projectId}/scripts`),
    enabled: !!projectId,
  });

  const handleVersionChange = (value: string | null) => {
    if (!value) return;
    const selected = versions?.find((v) => v.id === value);
    if (!selected) return;
    cancelPendingSave();
    setCurrentVersionId(selected.id);
    setVersionNumber(selected.version_number);
    setContent(selected.content);
    markClean();
  };

  return (
    <Select value={currentVersionId ?? ""} onValueChange={handleVersionChange}>
      <SelectTrigger className="w-48">
        <SelectValue placeholder={`v${versionNumber}`} />
      </SelectTrigger>
      <SelectContent>
        {versions?.map((v) => (
          <SelectItem key={v.id} value={v.id}>
            v{v.version_number} — {new Date(v.created_at).toLocaleDateString()}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
