"use client"

import { useState, useRef, useEffect, type DragEvent, type ChangeEvent } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod/v4"
import { zodResolver } from "@hookform/resolvers/zod"
import { api, ApiError } from "@/lib/api"
import { useQueryClient } from "@tanstack/react-query"
import type { TargetFormat, ContentGoal } from "@/types/project"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { toast } from "sonner"
import { Loader2, Upload, FileText, X } from "lucide-react"
import { cn } from "@/lib/utils"

const TARGET_FORMATS: TargetFormat[] = ["VSL", "YouTube", "Tutorial", "Facebook", "LinkedIn", "Blog"]
const CONTENT_GOALS: ContentGoal[] = ["Sell", "Educate", "Entertain", "Build Authority"]

const schema = z.object({
  topic: z.string().min(1, "Topic is required").max(200),
  target_format: z.enum(TARGET_FORMATS),
  content_goal: z.enum(CONTENT_GOALS).optional(),
  raw_notes: z.string().max(10000),
})

type FormValues = z.infer<typeof schema>

interface SubjectPanelProps {
  projectId: string
}

export function SubjectPanel({ projectId }: SubjectPanelProps) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDragActive, setIsDragActive] = useState(false)
  
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      topic: "",
      target_format: undefined,
      content_goal: undefined,
      raw_notes: "",
    },
  })

  const rawNotes = watch("raw_notes")

  const uploadFile = async (file: File) => {
    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append("file", file)
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const res = await fetch(`${baseUrl}/api/v1/projects/${projectId}/rag/upload?step_type=subject`, {
        method: "POST",
        body: formData,
      })
      
      if (res.ok) {
        const content = await file.text()
        setValue("raw_notes", content, { shouldValidate: true })
        setUploadedFilename(file.name)
        toast.success(`Loaded content from ${file.name}`)
      } else {
        throw new Error("Upload failed")
      }
    } catch (err) {
      toast.error("Failed to upload file")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragActive(false)
    const file = e.dataTransfer.files[0]
    if (file && (file.name.endsWith(".txt") || file.name.endsWith(".md"))) {
      uploadFile(file)
    }
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragActive(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragActive(false)
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadFile(file)
    }
  }

  const clearFile = () => {
    setUploadedFilename(null)
    setValue("raw_notes", "", { shouldValidate: true })
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const onSubmit = async (data: FormValues) => {
    try {
      await api.post(`/api/v1/projects/${projectId}/subject`, {
        topic: data.topic,
        target_format: data.target_format,
        content_goal: data.content_goal ?? null,
        raw_notes: data.raw_notes || "",
      })
      queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] })
      toast.success("Subject saved!")
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to save subject"
      toast.error(msg)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Subject</CardTitle>
        <CardDescription>
          Define the topic, format, and goals for your script. Upload a file with your notes or type them below.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="topic">Topic</Label>
            <Input id="topic" {...register("topic")} placeholder="What is the video/post about?" />
            {errors.topic && (
              <p className="text-xs text-destructive">{errors.topic.message}</p>
            )}
          </div>

          <div className="grid gap-2">
            <Label>Target Format</Label>
            <Select
              onValueChange={(v) =>
                setValue("target_format", v as TargetFormat, {
                  shouldValidate: true,
                })
              }
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select format" />
              </SelectTrigger>
              <SelectContent>
                {TARGET_FORMATS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.target_format && (
              <p className="text-xs text-destructive">
                {errors.target_format.message}
              </p>
            )}
          </div>

          <div className="grid gap-2">
            <Label>Content Goal</Label>
            <Select
              onValueChange={(v) =>
                setValue("content_goal", v as ContentGoal, {
                  shouldValidate: true,
                })
              }
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select goal (optional)" />
              </SelectTrigger>
              <SelectContent>
                {CONTENT_GOALS.map((g) => (
                  <SelectItem key={g} value={g}>
                    {g}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Notes File</Label>
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
                    ? "Drop file here..."
                    : "Drag & drop .txt or .md file, or click to browse"}
                </p>
              </div>
            </div>

            {uploadedFilename && (
              <div className="flex items-center gap-2 rounded-full bg-secondary px-3 py-1 text-xs w-fit">
                <FileText className="h-3 w-3" />
                <span>{uploadedFilename}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    clearFile()
                  }}
                  className="ml-1 hover:text-destructive"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            )}
          </div>

          <div className="grid gap-2">
            <Label htmlFor="raw_notes">Notes</Label>
            <Textarea 
              id="raw_notes" 
              {...register("raw_notes")} 
              rows={5}
              placeholder="Describe your content, key points, angles, or paste content from your file..."
              value={rawNotes}
              onChange={(e) => setValue("raw_notes", e.target.value)}
            />
            {errors.raw_notes && (
              <p className="text-xs text-destructive">
                {errors.raw_notes.message}
              </p>
            )}
          </div>

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting && <Loader2 className="animate-spin" />}
            Continue
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}