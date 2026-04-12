"use client"

import { useQuery, useQueryClient } from "@tanstack/react-query"
import { api, ApiError } from "@/lib/api"
import type { LLMSettings, LLMStatus } from "@/types/settings"
import { useSettingsStore } from "@/stores/settings-store"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { Loader2, CheckCircle2, XCircle } from "lucide-react"
import { useState } from "react"

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const { pendingApiKeys, pendingEnabled, setApiKey, setEnabled, resetPending } =
    useSettingsStore()
  const [saving, setSaving] = useState(false)

  const { data: settings, isLoading } = useQuery<LLMSettings>({
    queryKey: ["settings"],
    queryFn: () => api.get<LLMSettings>("/api/v1/settings/llm"),
  })

  const [statusResult, setStatusResult] = useState<LLMStatus | null>(null)
  const [testing, setTesting] = useState(false)

  const testConnection = async () => {
    setTesting(true)
    try {
      const status = await api.get<LLMStatus>("/api/v1/settings/llm/status")
      setStatusResult(status)
    } catch {
      toast.error("Failed to test connections")
    } finally {
      setTesting(false)
    }
  }

  const save = async () => {
    setSaving(true)
    try {
      const providers: Record<string, { api_key?: string; enabled?: boolean }> =
        {}
      for (const [name, key] of Object.entries(pendingApiKeys)) {
        if (!providers[name]) providers[name] = {}
        providers[name].api_key = key
      }
      for (const [name, enabled] of Object.entries(pendingEnabled)) {
        if (!providers[name]) providers[name] = {}
        providers[name].enabled = enabled
      }
      await api.patch("/api/v1/settings/llm", providers)
      toast.success("Settings saved")
      resetPending()
      queryClient.invalidateQueries({ queryKey: ["settings"] })
    } catch (err) {
      const msg =
        err instanceof ApiError ? err.message : "Failed to save settings"
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={testConnection} disabled={testing}>
            {testing && <Loader2 className="animate-spin" />}
            Test Connection
          </Button>
          <Button onClick={save} disabled={saving}>
            {saving && <Loader2 className="animate-spin" />}
            Save
          </Button>
        </div>
      </div>

      {statusResult && (
        <Card>
          <CardHeader>
            <CardTitle>Connection Status</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            {statusResult.providers.map((p) => (
              <div key={p.name} className="flex items-center gap-1.5">
                {p.reachable ? (
                  <CheckCircle2 className="size-4 text-green-600" />
                ) : (
                  <XCircle className="size-4 text-red-500" />
                )}
                <span className="text-sm font-medium">{p.name}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {settings?.providers.map((provider) => {
          const pendingKey = pendingApiKeys[provider.name]
          const isEnabled =
            provider.name in pendingEnabled
              ? pendingEnabled[provider.name]
              : provider.enabled

          return (
            <Card key={provider.name}>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <CardTitle>{provider.name}</CardTitle>
                  <Badge variant={isEnabled ? "default" : "outline"}>
                    {isEnabled ? "Enabled" : "Disabled"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-2">
                <div className="grid gap-2">
                  <Label htmlFor={`key-${provider.name}`}>API Key</Label>
                  <Input
                    id={`key-${provider.name}`}
                    type="password"
                    placeholder={provider.api_key_masked || "Enter API key"}
                    value={pendingKey ?? ""}
                    onChange={(e) => setApiKey(provider.name, e.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>Base URL</Label>
                  <Input value={provider.base_url} readOnly className="bg-muted" />
                </div>
                <div className="grid gap-2">
                  <Label>Model</Label>
                  <Input value={provider.model} readOnly className="bg-muted" />
                </div>
                <div className="flex items-end gap-2">
                  <Label htmlFor={`enabled-${provider.name}`}>Enabled</Label>
                  <input
                    id={`enabled-${provider.name}`}
                    type="checkbox"
                    checked={isEnabled}
                    onChange={(e) =>
                      setEnabled(provider.name, e.target.checked)
                    }
                    className="size-4 rounded border-input"
                  />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
