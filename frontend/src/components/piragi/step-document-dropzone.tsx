"use client";

import { useState, useRef, type DragEvent, type ChangeEvent } from "react";
import { Upload, FileText, Loader2, X, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface StepDocumentDropzoneProps {
  projectId: string;
  stepType: string;
  className?: string;
}

const STEP_HINTS: Record<string, { title: string; info: string }> = {
  icp: {
    title: "Ideal Customer Profile",
    info: "Upload documents with demographic data, pain points, desires, or buyer persona research. If not uploaded, describe your ICP in the text area below.",
  },
  subject: {
    title: "Subject Notes",
    info: "Upload a .txt or .md file with your subject notes, or type them manually in the notes field below.",
  },
  hook: {
    title: "Hook Formulas",
    info: "Upload high-performing hooks, viral opener examples, or transcript analysis. If not uploaded, use your intuition and best practices.",
  },
  narrative: {
    title: "Narrative Patterns",
    info: "Upload storytelling frameworks, story templates, or narrative structure examples.",
  },
  retention: {
    title: "Retention Techniques",
    info: "Upload engagement tactics, retention strategies, or viewer retention research.",
  },
  cta: {
    title: "Call to Action",
    info: "Upload CTA examples, conversion phrases, urgency tactics, or offer templates.",
  },
};

export function StepDocumentDropzone({
  projectId,
  stepType,
  className,
}: StepDocumentDropzoneProps) {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [showHint, setShowHint] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const fileArray = Array.from(files);

    for (const file of fileArray) {
      try {
        const formData = new FormData();
        formData.append("file", file);

        let endpoint = `${baseUrl}/api/v1/projects/${projectId}/rag/upload?step_type=${stepType}`;
        if (stepType === "hook") {
          endpoint = `${baseUrl}/api/v1/projects/${projectId}/hooks/upload`;
        } else if (stepType === "icp") {
          endpoint = `${baseUrl}/api/v1/projects/${projectId}/icp/upload`;
        }

        const res = await fetch(endpoint, {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          setUploadedFiles((prev) => [...prev, file.name]);
        } else {
          const errText = await res.text();
          console.error("Upload failed:", res.status, errText);
        }
      } catch (err) {
        console.error("Upload failed:", err);
      }
    }
    setIsUploading(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);
    uploadFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    uploadFiles(e.target.files);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const hint = STEP_HINTS[stepType] || STEP_HINTS.icp;

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">{hint.title}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowHint(!showHint)}
          className="h-6 px-2"
        >
          <Info className="h-3 w-3" />
        </Button>
      </div>

      {showHint && (
        <div className="rounded-md bg-muted p-3 text-xs text-muted-foreground">
          {hint.info}
        </div>
      )}

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          "cursor-pointer rounded-lg border-2 border-dashed p-4 transition-colors",
          isDragActive
            ? "border-primary bg-accent/50"
            : "border-border hover:border-muted-foreground"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
        <div className="flex flex-col items-center gap-2 text-center">
          {isUploading ? (
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          ) : (
            <Upload className="h-6 w-6 text-muted-foreground" />
          )}
          <p className="text-sm text-muted-foreground">
            {isDragActive
              ? "Drop files here..."
              : "Drag & drop .txt or .md files, or click to browse"}
          </p>
        </div>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {uploadedFiles.map((filename) => (
            <div
              key={filename}
              className="flex items-center gap-1 rounded-full bg-secondary px-3 py-1 text-xs"
            >
              <FileText className="h-3 w-3" />
              <span>{filename}</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setUploadedFiles((prev) =>
                    prev.filter((f) => f !== filename)
                  );
                }}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}