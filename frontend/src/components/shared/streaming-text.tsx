"use client";

import { cn } from "@/lib/utils";

interface StreamingTextProps {
  text: string;
  isActive?: boolean;
  className?: string;
}

export function StreamingText({ text, isActive = false, className }: StreamingTextProps) {
  return (
    <span className={cn("whitespace-pre-wrap", className)}>
      {text}
      {isActive && <span className="inline-block w-0.5 animate-pulse bg-foreground align-text-bottom" />}
    </span>
  );
}
