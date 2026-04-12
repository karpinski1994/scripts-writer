"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams } from "next/navigation"
import Link from "next/link"
import { api, ApiError } from "@/lib/api"
import type { ProjectDetail } from "@/types/project"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, Loader2 } from "lucide-react"

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>()
  const id = params.id

  const {
    data: project,
    isLoading,
    error,
  } = useQuery<ProjectDetail>({
    queryKey: ["project", id],
    queryFn: () => api.get<ProjectDetail>(`/api/v1/projects/${id}`),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error && error instanceof ApiError && error.status === 404) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24">
        <p className="text-lg text-muted-foreground">Project not found</p>
        <Button variant="outline" render={<Link href="/" />}>
          <ArrowLeft />
          Back to Dashboard
        </Button>
      </div>
    )
  }

  if (!project) return null

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" render={<Link href="/" />}>
        <ArrowLeft />
        Back
      </Button>

      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">{project.name}</h1>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">{project.target_format}</Badge>
          {project.content_goal && (
            <Badge variant="outline">{project.content_goal}</Badge>
          )}
          <Badge variant="outline">{project.status}</Badge>
        </div>
      </div>

      <Separator />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Topic</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{project.topic}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Created: {formatDate(project.created_at)}</p>
            <p>Updated: {formatDate(project.updated_at)}</p>
            <p>Current Step: {project.current_step}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Notes</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap rounded-lg bg-muted p-4 text-sm">
            {project.raw_notes}
          </pre>
        </CardContent>
      </Card>
    </div>
  )
}
