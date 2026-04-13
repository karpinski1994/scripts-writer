"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { PipelineStep } from "@/types/pipeline";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Loader2, GitBranch } from "lucide-react";

const STEP_LABELS: Record<string, string> = {
  icp: "ICP Profile",
  hook: "Hook",
  narrative: "Narrative",
  retention: "Retention",
  cta: "CTA",
  writer: "Writer",
  factcheck: "Fact Check",
  readability: "Readability",
  copyright: "Copyright",
  policy: "Policy",
};

interface BranchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  steps: PipelineStep[];
  projectName: string;
}

export function BranchDialog({
  open,
  onOpenChange,
  projectId,
  steps,
  projectName,
}: BranchDialogProps) {
  const router = useRouter();
  const [name, setName] = useState(`${projectName} (branch)`);
  const [branchFromStep, setBranchFromStep] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const completedSteps = steps.filter((s) => s.status === "completed");

  const handleSubmit = async () => {
    if (!branchFromStep || !name.trim()) return;
    setSubmitting(true);
    try {
      const result = await api.post<{ id: string }>(`/api/v1/projects/${projectId}/branch`, {
        branch_from_step: branchFromStep,
        name: name.trim(),
      });
      toast.success("Project branched successfully");
      onOpenChange(false);
      router.push(`/projects/${result.id}`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to branch project";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitBranch className="size-5" />
            Branch Project
          </DialogTitle>
          <DialogDescription>
            Create a new project that copies all steps up to and including the selected step.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="branch-name">New Project Name</Label>
            <Input
              id="branch-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label>Branch From Step</Label>
            <Select value={branchFromStep} onValueChange={(v) => v && setBranchFromStep(v)}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select step to branch from" />
              </SelectTrigger>
              <SelectContent>
                {completedSteps.map((s) => (
                  <SelectItem key={s.step_type} value={s.step_type}>
                    {STEP_LABELS[s.step_type] || s.step_type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!branchFromStep || !name.trim() || submitting}>
            {submitting && <Loader2 className="animate-spin" />}
            Branch
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
