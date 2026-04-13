"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Copy, Check } from "lucide-react";
import { toast } from "sonner";

interface ExportPanelProps {
  projectId: string;
}

export function ExportPanel({ projectId }: ExportPanelProps) {
  const [format, setFormat] = useState<"txt" | "md">("txt");
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const exportUrl = `${baseUrl}/api/v1/projects/${projectId}/export?format=${format}`;

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await fetch(exportUrl);
      if (!res.ok) {
        throw new Error("Export failed");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `script.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to export script");
    } finally {
      setDownloading(false);
    }
  };

  const handleCopy = async () => {
    try {
      const res = await fetch(exportUrl);
      if (!res.ok) {
        throw new Error("Copy failed");
      }
      const text = await res.text();
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy script");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Export Script</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3">
          <Select
            value={format}
            onValueChange={(v) => setFormat(v as "txt" | "md")}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="txt">Plain Text (.txt)</SelectItem>
              <SelectItem value="md">Markdown (.md)</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleDownload} disabled={downloading}>
            <Download />
            {downloading ? "Downloading..." : "Download"}
          </Button>
          <Button variant="outline" onClick={handleCopy}>
            {copied ? <Check /> : <Copy />}
            {copied ? "Copied!" : "Copy"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
