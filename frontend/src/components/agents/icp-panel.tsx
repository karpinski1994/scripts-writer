"use client";

import { useRef, useState } from "react";
import type { ICPAgentOutput, ICPProfile } from "@/types/agents";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { NotebookLMContext } from "@/components/shared/notebooklm-context";
import { PiragiContextPreview } from "@/components/piragi/piragi-context-preview";
import { Upload } from "lucide-react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

interface ICPPanelProps {
  data?: ICPAgentOutput;
  onApprove?: () => void;
  onRerun?: () => void;
  isRunning?: boolean;
  projectId: string;
  isPending?: boolean;
}

export function ICPPanel({ data, onApprove, onRerun, isRunning, projectId, isPending }: ICPPanelProps) {
  const [editing, setEditing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const icp: ICPProfile | undefined = data?.icp;

  // if (isPending && !data) {
  //   return (
  //     <Card>
  //       <CardContent className="flex flex-col items-center justify-center gap-4 py-12">
  //         <p className="text-muted-foreground">Complete the Subject step first to generate an ICP profile.</p>
  //       </CardContent>
  //     </Card>
  //   );
  // }


  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/api/v1/projects/${projectId}/icp/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error("Upload failed");
      }
      toast.success("ICP profile uploaded");
      queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] });
    } catch {
      toast.error("Failed to upload ICP profile");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">ICP Profile</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setEditing(!editing)}>
            {editing ? "View" : "Edit"}
          </Button>
          <Button variant="outline" size="sm" onClick={onRerun} disabled={isRunning}>
            Re-run
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.txt"
            className="hidden"
            onChange={handleUpload}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            <Upload />
            {uploading ? "Uploading..." : "Upload ICP"}
          </Button>
        </div>
      </div>
      {data && icp && <div>

        <Card>
          <CardHeader>
            <CardTitle>Demographics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 text-sm md:grid-cols-2">
              <div><span className="text-muted-foreground">Age:</span> {icp.demographics.age_range}</div>
              <div><span className="text-muted-foreground">Gender:</span> {icp.demographics.gender}</div>
              <div><span className="text-muted-foreground">Income:</span> {icp.demographics.income_level}</div>
              <div><span className="text-muted-foreground">Education:</span> {icp.demographics.education}</div>
              <div><span className="text-muted-foreground">Location:</span> {icp.demographics.location}</div>
              <div><span className="text-muted-foreground">Occupation:</span> {icp.demographics.occupation}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Psychographics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div><span className="text-muted-foreground">Values:</span> {icp.psychographics.values.join(", ")}</div>
              <div><span className="text-muted-foreground">Interests:</span> {icp.psychographics.interests.join(", ")}</div>
              <div><span className="text-muted-foreground">Lifestyle:</span> {icp.psychographics.lifestyle}</div>
              <div><span className="text-muted-foreground">Media:</span> {icp.psychographics.media_consumption.join(", ")}</div>
              <div><span className="text-muted-foreground">Traits:</span> {icp.psychographics.personality_traits.join(", ")}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pain Points & Desires</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Pain Points</p>
              <div className="flex flex-wrap gap-1">
                {icp.pain_points.map((p, i) => <Badge key={i} variant="destructive">{p}</Badge>)}
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Desires</p>
              <div className="flex flex-wrap gap-1">
                {icp.desires.map((d, i) => <Badge key={i} variant="secondary">{d}</Badge>)}
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Objections</p>
              <div className="flex flex-wrap gap-1">
                {icp.objections.map((o, i) => <Badge key={i} variant="outline">{o}</Badge>)}
              </div>
            </div>
            <p className="text-sm"><span className="text-muted-foreground">Language Style:</span> {icp.language_style}</p>
          </CardContent>
        </Card>

        <NotebookLMContext stepType="icp" projectId={projectId} />

        <PiragiContextPreview stepType="icp" projectId={projectId} />

        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">Confidence: {Math.round(data.confidence * 100)}%</p>
          <Button onClick={onApprove}>Approve & Continue</Button>
        </div>
      </div>
      }
    </div>
  );
}
