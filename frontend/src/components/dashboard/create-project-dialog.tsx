"use client"

import { useForm } from "react-hook-form"
import { z } from "zod/v4"
import { zodResolver } from "@hookform/resolvers/zod"
import { api, ApiError } from "@/lib/api"
import type { ProjectCreateInput } from "@/types/project"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
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
import { Loader2 } from "lucide-react"

const TARGET_FORMATS = ["VSL", "YouTube", "Tutorial", "Facebook", "LinkedIn", "Blog"] as const
const CONTENT_GOALS = ["Sell", "Educate", "Entertain", "Build Authority"] as const

const schema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  topic: z.string().min(1, "Topic is required").max(200),
  target_format: z.enum(TARGET_FORMATS),
  content_goal: z.enum(CONTENT_GOALS).optional(),
  raw_notes: z.string().min(1, "Notes are required").max(10000),
})

type FormValues = z.infer<typeof schema>

interface CreateProjectDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: () => void
}

export function CreateProjectDialog({
  open,
  onOpenChange,
  onCreated,
}: CreateProjectDialogProps) {
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      topic: "",
      target_format: undefined,
      content_goal: undefined,
      raw_notes: "",
    },
  })

  const onSubmit = async (data: FormValues) => {
    try {
      const input: ProjectCreateInput = {
        name: data.name,
        topic: data.topic,
        target_format: data.target_format,
        content_goal: data.content_goal ?? null,
        raw_notes: data.raw_notes,
      }
      await api.post("/api/v1/projects", input)
      reset()
      onOpenChange(false)
      onCreated()
    } catch (err) {
      const msg =
        err instanceof ApiError ? err.message : "Failed to create project"
      toast.error(msg)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => { onOpenChange(o); if (!o) reset() }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New Project</DialogTitle>
          <DialogDescription>
            Create a new script writing project.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="name">Name</Label>
            <Input id="name" {...register("name")} />
            {errors.name && (
              <p className="text-xs text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="grid gap-2">
            <Label htmlFor="topic">Topic</Label>
            <Input id="topic" {...register("topic")} />
            {errors.topic && (
              <p className="text-xs text-destructive">{errors.topic.message}</p>
            )}
          </div>

          <div className="grid gap-2">
            <Label>Target Format</Label>
            <Select
              onValueChange={(v) =>
                setValue("target_format", v as FormValues["target_format"], {
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
                setValue("content_goal", v as FormValues["content_goal"], {
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

          <div className="grid gap-2">
            <Label htmlFor="raw_notes">Notes</Label>
            <Textarea id="raw_notes" {...register("raw_notes")} rows={5} />
            {errors.raw_notes && (
              <p className="text-xs text-destructive">
                {errors.raw_notes.message}
              </p>
            )}
          </div>

          <DialogFooter open={open} onOpenChange={onOpenChange}>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="animate-spin" />}
              Create
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
