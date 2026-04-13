"use client"

import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { api } from "@/lib/api"
import type { ProjectSummary } from "@/types/project"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { CreateProjectDialog } from "@/components/dashboard/create-project-dialog"

function formatRelativeTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 30) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export default function DashboardPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)

  const { data: projects, isLoading } = useQuery<ProjectSummary[]>({
    queryKey: ["projects"],
    queryFn: () => api.get<ProjectSummary[]>("/api/v1/projects"),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus />
          New Project
        </Button>
      </div>

      <CreateProjectDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onCreated={() => {
          queryClient.invalidateQueries({ queryKey: ["projects"] })
        }}
      />

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-5 w-3/4" />
              </CardHeader>
              <CardContent className="flex items-center gap-2">
                <Skeleton className="h-5 w-16" />
                <Skeleton className="h-5 w-16" />
                <Skeleton className="ml-auto h-4 w-12" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && projects?.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-4 py-24">
          <p className="text-muted-foreground">No projects yet.</p>
          <Button onClick={() => setDialogOpen(true)}>
            <Plus />
            Create your first script
          </Button>
        </div>
      )}

      {!isLoading && projects && projects.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Card
              key={project.id}
              className="cursor-pointer transition-shadow hover:shadow-md"
              onClick={() => router.push(`/projects/${project.id}`)}
            >
              <CardHeader>
                <CardTitle className="truncate">{project.name}</CardTitle>
              </CardHeader>
              <CardContent className="flex items-center gap-2">
                <Badge variant="secondary">{project.target_format}</Badge>
                <Badge variant="outline">{project.status}</Badge>
                <span className="ml-auto text-xs text-muted-foreground">
                  {formatRelativeTime(project.updated_at)}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
