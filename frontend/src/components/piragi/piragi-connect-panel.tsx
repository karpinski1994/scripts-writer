"use client";

import { useState, useRef } from "react";
import { usePiragiStore } from "@/stores/piragi-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FileText, Upload, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

const CATEGORIES = [
  { value: "icp", label: "ICP & Buyer Personas" },
  { value: "hooks", label: "Hooks & Openers" },
  { value: "narratives", label: "Narratives & Stories" },
  { value: "retention", label: "Retention Techniques" },
  { value: "cta", label: "Calls to Action" },
  { value: "policies", label: "Platform Policies" },
  { value: "fact_checks", label: "Facts & References" },
] as const;

interface PiragiConnectPanelProps {
  projectId: string;
}

export function PiragiConnectPanel({ projectId }: PiragiConnectPanelProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("icp");
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { isUploading, uploadDocument, fetchCategories } = usePiragiStore();

  const handleCategoryChange = (value: string | null) => {
    if (value) setSelectedCategory(value);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadStatus("idle");
    const result = await uploadDocument(projectId, selectedCategory, file);
    if (result) {
      setUploadStatus("success");
      await fetchCategories(projectId);
    } else {
      setUploadStatus("error");
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Upload Documents
        </CardTitle>
        <CardDescription>
          Upload .txt or .md files to include in RAG context
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Select value={selectedCategory} onValueChange={handleCategoryChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((cat) => (
                  <SelectItem key={cat.value} value={cat.value}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4 mr-2" />
              )}
              Choose File
            </Button>
          </div>
          {uploadStatus === "success" && (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <CheckCircle2 className="h-4 w-4" />
              File uploaded and indexed
            </div>
          )}
          {uploadStatus === "error" && (
            <div className="flex items-center gap-2 text-sm text-red-600">
              <AlertCircle className="h-4 w-4" />
              Upload failed. Make sure piragi is installed.
            </div>
          )}
          <div className="text-xs text-muted-foreground">
            <p className="font-medium mb-1">Supported categories:</p>
            <ul className="grid grid-cols-2 gap-1">
              {CATEGORIES.map((cat) => (
                <li key={cat.value}>• {cat.label}</li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}