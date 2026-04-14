"use client"

import { useForm } from "react-hook-form"
import { z } from "zod/v4"
import { zodResolver } from "@hookform/resolvers/zod"
import { api, ApiError } from "@/lib/api"
import { useRouter } from "next/navigation"
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
import { Loader2 } from "lucide-react"

const TARGET_FORMATS: TargetFormat[] = ["VSL", "YouTube", "Tutorial", "Facebook", "LinkedIn", "Blog"]
const CONTENT_GOALS: ContentGoal[] = ["Sell", "Educate", "Entertain", "Build Authority"]

const schema = z.object({
  topic: z.string().min(1, "Topic is required").max(200),
  target_format: z.enum(TARGET_FORMATS),
  content_goal: z.enum(CONTENT_GOALS).optional(),
  raw_notes: z.string().min(1, "Notes are required").max(10000),
})

type FormValues = z.infer<typeof schema>

interface SubjectPanelProps {
  projectId: string
}

export function SubjectPanel({ projectId }: SubjectPanelProps) {
  const router = useRouter()
  const queryClient = useQueryClient()
  
  const {
    register,
    handleSubmit,
    setValue,
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

  const onSubmit = async (data: FormValues) => {
    try {
      await api.post(`/api/v1/projects/${projectId}/subject`, {
        topic: data.topic,
        target_format: data.target_format,
        content_goal: data.content_goal ?? null,
        raw_notes: data.raw_notes,
      })
      queryClient.invalidateQueries({ queryKey: ["pipeline", projectId] })
      toast.success("Subject saved!")
    } catch (err) {
      const msg =
        err instanceof ApiError ? err.message : "Failed to save subject"
      toast.error(msg)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Subject</CardTitle>
        <CardDescription>
          Define the topic, format, and goals for your script.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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

          <div className="grid gap-2">
            <Label htmlFor="raw_notes">Notes</Label>
            <Textarea id="raw_notes" {...register("raw_notes")} rows={5} />
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