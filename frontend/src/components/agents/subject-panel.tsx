"use client"

import { useState, useRef, useEffect, type DragEvent, type ChangeEvent } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod/v4"
import { zodResolver } from "@hookform/resolvers/zod"
import { api, ApiError } from "@/lib/api"
import { useQuery, useQueryClient } from "@tanstack/react-query"
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
import { toast } from "sonner"
import { Loader2, Upload, FileText, X, CheckCircle2, Video, FileText as FileTextIcon, MessageCircle, Globe } from "lucide-react"
import { cn } from "@/lib/utils"
import { usePipelineStore } from "@/stores/pipeline-store"
import type { ProjectDetail } from "@/types/project"

const CONTENT_FORMATS = [
  { id: "short_video", label: "Short-form Video", sublabel: "TikTok/Reels", icon: Video, hasRetention: true },
  { id: "long_video", label: "Long-form Video", sublabel: "YouTube", icon: Globe, hasRetention: true },
  { id: "vsl", label: "VSL", sublabel: "Video Sales Letter", icon: FileTextIcon, hasRetention: true },
  { id: "blog", label: "Blog Post", sublabel: "Article", icon: FileTextIcon, hasRetention: false },
  { id: "linkedin", label: "LinkedIn Post", sublabel: "Professional", icon: MessageCircle, hasRetention: false },
  { id: "facebook", label: "Facebook Post", sublabel: "Social", icon: MessageCircle, hasRetention: false },
] as const

const TARGET_FORMAT_TO_ID: Record<string, string> = {
  "Short-form Video": "short_video",
  "Long-form Video": "long_video",
  "VSL": "vsl",
  "Blog Post": "blog",
  "LinkedIn Post": "linkedin",
  "Facebook Post": "facebook",
}

const ALLOWED_TYPES = [".txt", ".pdf", ".docx", ".md"]

const schema = z.object({
  content_format: z.enum(CONTENT_FORMATS.map(f => f.id) as [string, ...string[]]),
  topic: z.string().max(500),
  draft: z.string().max(10000),
  main_goal: z.string().max(200),
})

type FormValues = z.infer<typeof schema>

interface SubjectPanelProps {
  projectId: string
}

export function SubjectPanel({ projectId }: SubjectPanelProps) {
  const queryClient = useQueryClient()
  const setActiveStepType = usePipelineStore((s) => s.setActiveStepType)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadedFilename, setUploadedFilename] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDragActive, setIsDragActive] = useState(false)
  const [hasFile, setHasFile] = useState(false)
  const [hasInitialized, setHasInitialized] = useState(false)

  const { data: project, isLoading: projectLoading } = useQuery<ProjectDetail>({
    queryKey: ["project", projectId],
    queryFn: () => api.get(`/api/v1/projects/${projectId}`),
    enabled: !!projectId,
  })

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      content_format: undefined,
      topic: "",
      draft: "",
      main_goal: "",
    },
  })

  const watchedContentFormat = watch("content_format")
  const watchedTopic = watch("topic")

  useEffect(() => {
    if (project && !hasInitialized) {
      const existingFormatId = project.target_format ? TARGET_FORMAT_TO_ID[project.target_format] : null
      if (existingFormatId) {
        setHasInitialized(true)
        setValue("content_format", existingFormatId as typeof CONTENT_FORMATS[number]["id"], { shouldValidate: false })
        if (project.topic) {
          setValue("topic", project.topic, { shouldValidate: false })
        }
        if (project.draft) {
          setValue("draft", project.draft, { shouldValidate: false })
        }
        if (project.content_goal) {
          setValue("main_goal", project.content_goal, { shouldValidate: false })
        }
      }
    }
  }, [project, hasInitialized, setValue])

  const uploadFile = async (file: File) => {
    const ext = "." + file.name.split(".").pop()?.toLowerCase()
    console.log("[SUBJECT-PANEL] File upload started:", { fileName: file.name, ext })
    
    if (!ALLOWED_TYPES.includes(ext)) {
      console.warn("[SUBJECT-PANEL] Invalid file type:", ext)
      toast.error("Invalid file type. Use .txt, .pdf, .docx, or .md")
      return
    }

    setIsUploading(true)
    try {
      console.log("[SUBJECT-PANEL] Preparing FormData for upload")
      const formData = new FormData()
      formData.append("file", file)
      
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const uploadUrl = `${baseUrl}/api/v1/projects/${projectId}/rag/upload?step_type=subject`
      console.log("[SUBJECT-PANEL] Uploading file to:", uploadUrl)
      
      const res = await fetch(uploadUrl, {
        method: "POST",
        body: formData,
      })
      console.log("[SUBJECT-PANEL] Upload response status:", res.status)
      
      if (res.ok) {
        const content = await file.text()
        console.log("[SUBJECT-PANEL] File content length:", content.length)
        const topicMatch = content.slice(0, 500).replace(/\n/g, " ").trim()
        console.log("[SUBJECT-PANEL] Setting topic from file:", topicMatch.slice(0, 50) + "...")
        setValue("topic", topicMatch, { shouldValidate: true })
        setUploadedFilename(file.name)
        setHasFile(true)
        console.log("[SUBJECT-PANEL] File upload successful")
        toast.success("Brief uploaded! Manual fields are now optional.")
      } else {
        console.error("[SUBJECT-PANEL] Upload failed with status:", res.status)
        throw new Error("Upload failed")
      }
    } catch (err) {
      console.error("[SUBJECT-PANEL] File upload error:", err)
      toast.error("Failed to upload file")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragActive(false)
    const file = e.dataTransfer.files[0]
    if (file) {
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
    setHasFile(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const onSubmit = async (data: FormValues) => {
    const formatLabel = CONTENT_FORMATS.find(f => f.id === data.content_format)?.label || data.content_format
    
    console.log("[SUBJECT-PANEL] Submitting subject data:", {
      topic: data.topic,
      draft: data.draft,
      target_format: formatLabel,
      content_goal: data.main_goal,
      raw_notes: watchedTopic?.slice(0, 100) + "...",
    })
    
    try {
      console.log("[SUBJECT-PANEL] Sending POST to /api/v1/projects/{projectId}/subject")
      await api.post(`/api/v1/projects/${projectId}/subject`, {
        topic: data.topic || "",
        target_format: formatLabel,
        content_goal: data.main_goal || null,
        raw_notes: watchedTopic || "",
        draft: data.draft || "",
      })
      console.log("[SUBJECT-PANEL] Subject saved successfully, invalidating pipeline queries")
      queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] })
      queryClient.invalidateQueries({ queryKey: ["project", projectId] })
      toast.success("Subject saved!")
      
      setActiveStepType("hook")
    } catch (err) {
      console.error("[SUBJECT-PANEL] Failed to save subject:", err)
      const msg = err instanceof ApiError ? err.message : "Failed to save subject"
      toast.error(msg)
    }
  }

  if (projectLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Subject</CardTitle>
        <CardDescription>
          Define what your content is about. Upload a brief file or fill in manually.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-2">
            <Label className="text-base font-medium">The Fast Track</Label>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                "cursor-pointer rounded-xl border-2 border-dashed p-8 transition-all",
                isDragActive
                  ? "border-primary bg-primary/5"
                  : hasFile
                    ? "border-green-500 bg-green-500/5"
                    : "border-border hover:border-muted-foreground hover:bg-muted/50"
              )}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={ALLOWED_TYPES.join(",")}
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="flex flex-col items-center gap-3 text-center">
                {isUploading ? (
                  <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
                ) : hasFile ? (
                  <>
                    <CheckCircle2 className="h-10 w-10 text-green-500" />
                    <div>
                      <p className="font-medium text-green-700">Brief uploaded!</p>
                      <p className="text-sm text-muted-foreground">Manual fields are now optional</p>
                    </div>
                  </>
                ) : (
                  <>
                    <Upload className="h-10 w-10 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Drop your brief here</p>
                      <p className="text-sm text-muted-foreground">.txt, .pdf, .docx, .md</p>
                    </div>
                  </>
                )}
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

          <div className="space-y-3">
            <Label className="text-base font-medium">
              Content Format <span className="text-destructive">*</span>
            </Label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {CONTENT_FORMATS.map((format) => {
                const Icon = format.icon
                const isSelected = watchedContentFormat === format.id
                return (
                  <button
                    key={format.id}
                    type="button"
                    onClick={() => setValue("content_format", format.id, { shouldValidate: true })}
                    className={cn(
                      "flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-all",
                      isSelected
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-muted-foreground hover:bg-muted/50"
                    )}
                  >
                    <Icon className={cn("h-6 w-6", isSelected ? "text-primary" : "text-muted-foreground")} />
                    <div className="text-center">
                      <p className={cn("text-sm font-medium", isSelected && "text-primary")}>{format.label}</p>
                      <p className="text-xs text-muted-foreground">{format.sublabel}</p>
                    </div>
                  </button>
                )
              })}
            </div>
            {errors.content_format && (
              <p className="text-xs text-destructive">{errors.content_format.message}</p>
            )}
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-base font-medium">
                Topic / Core Premise
                {!hasFile && <span className="text-destructive"> *</span>}
              </Label>
              <Textarea
                {...register("topic")}
                placeholder="e.g., 5 reasons why email marketing isn't dead in 2024..."
                rows={3}
                className={cn(!hasFile && errors.topic && "border-destructive")}
              />
              {!hasFile && errors.topic && (
                <p className="text-xs text-destructive">{errors.topic.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-base font-medium">
                Draft
                {!hasFile && <span className="text-destructive"> *</span>}
              </Label>
              <Textarea
                {...register("draft")}
                placeholder="Paste your draft, notes, or rough ideas here..."
                rows={5}
                className={cn(!hasFile && errors.draft && "border-destructive")}
              />
              {!hasFile && errors.draft && (
                <p className="text-xs text-destructive">{errors.draft.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-base font-medium">
                Main Goal
                {!hasFile && <span className="text-destructive"> *</span>}
              </Label>
              <Input
                {...register("main_goal")}
                placeholder="e.g., Encourage readers to contact us for a free consultation"
                className={cn(!hasFile && errors.main_goal && "border-destructive")}
              />
              {!hasFile && errors.main_goal && (
                <p className="text-xs text-destructive">{errors.main_goal.message}</p>
              )}
            </div>
          </div>

          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting && <Loader2 className="animate-spin mr-2" />}
            Continue
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
