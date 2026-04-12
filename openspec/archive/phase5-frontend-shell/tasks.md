## 1. Shadcn/UI Components & Dependencies

- [ ] 1.1 Install required Shadcn/UI components: `npx shadcn@latest add dialog input label select textarea badge card separator sidebar sheet tooltip sonner` (in `frontend/`)
- [ ] 1.2 Create `.env.local` in `frontend/` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] 1.3 Verify: `npm run build` passes

## 2. API Client & TypeScript Types

- [ ] 2.1 Create `frontend/src/lib/api.ts` — typed API client with `api.get<T>(path)`, `api.post<T>(path, body)`, `api.patch<T>(path, body)`, `api.delete(path)`. Base URL from `process.env.NEXT_PUBLIC_API_URL` defaulting to `http://localhost:8000`. Parse JSON, throw on non-2xx with status code.
- [ ] 2.2 Create `frontend/src/types/project.ts` — `Project`, `ProjectSummary` (id, name, target_format, status, updated_at), `ProjectDetail` (+ topic, content_goal, raw_notes, current_step, created_at), `TargetFormat` union type, `ContentGoal` union type, `ProjectCreateInput` (name, topic, target_format, content_goal?, raw_notes). Match backend `ProjectSummaryResponse`, `ProjectDetailResponse`, `ProjectCreateRequest`.
- [ ] 2.3 Create `frontend/src/types/pipeline.ts` — `PipelineStep` (id, step_type, step_order, status, output_data?, selected_option?, duration_ms?, error_message?), `Pipeline` (project_id, current_step, steps). Match backend `PipelineStepResponse`, `PipelineResponse`.
- [ ] 2.4 Create `frontend/src/types/icp.ts` — `ICPProfile`, `ICPDemographics`, `ICPPsychographics`, `ICPProfileResponse`, `ICPUpdateRequest`. Match backend schemas.
- [ ] 2.5 Create `frontend/src/types/script.ts` — `ScriptVersion` (id, project_id, version_number, content, format, hook_text?, narrative_pattern?, cta_text?, created_at), `ScriptUpdateRequest` (content). Match backend schemas.
- [ ] 2.6 Create `frontend/src/types/settings.ts` — `ProviderConfig` (name, api_key_masked, base_url, enabled, model), `LLMSettings` (providers), `ProviderStatus` (name, reachable), `LLMStatus` (providers). Match backend `ProviderConfigResponse`, `LLMSettingsResponse`, `ProviderStatusResponse`, `LLMStatusResponse`.
- [ ] 2.7 Verify: `npm run build` passes with no type errors

## 3. Zustand Stores

- [ ] 3.1 Create `frontend/src/stores/project-store.ts` — Zustand store with `activeProjectId: string | null`, `setActiveProject(id: string | null)`, `reset()`.
- [ ] 3.2 Create `frontend/src/stores/settings-store.ts` — Zustand store with `pendingApiKeys: Record<string, string>`, `pendingEnabled: Record<string, boolean>`, `setApiKey(provider, key)`, `setEnabled(provider, enabled)`, `resetPending()`. Used for local edits before Save.
- [ ] 3.3 Verify: stores import and initialize without error

## 4. Root Layout with Providers & Sidebar

- [ ] 4.1 Update `frontend/src/app/layout.tsx` — wrap children in `QueryClientProvider` from TanStack Query, add `SidebarProvider` + `Sidebar` + `SidebarContent` with nav items: Dashboard (link to `/`, icon: LayoutDashboard), Settings (link to `/settings`, icon: Settings), `SidebarTrigger` for mobile toggle. Add `Toaster` from sonner. Update metadata title to "Scripts Writer".
- [ ] 4.2 Verify: layout renders with sidebar, Dashboard and Settings nav items visible

## 5. Dashboard Page

- [ ] 5.1 Replace `frontend/src/app/page.tsx` — `"use client"` component. Use `useQuery` from TanStack Query to fetch `GET /api/v1/projects`. Show loading spinner while fetching. Render project cards (name, format badge, status badge, relative updated_at). Add "New Project" button opening create dialog. Empty state when no projects: "Create your first project" CTA. Click card → `router.push(/projects/{id})`.
- [ ] 5.2 Create `frontend/src/components/dashboard/create-project-dialog.tsx` — dialog with React Hook Form + Zod resolver. Fields: name (text, required, max 100), topic (text, required, max 200), target_format (select: VSL/YouTube/Tutorial/Facebook/LinkedIn/Blog, required), content_goal (select: Sell/Educate/Entertain/Build Authority, optional), raw_notes (textarea, required, max 10000). On submit: `POST /api/v1/projects`, invalidate TanStack Query projects key, close dialog. Show toast on error.
- [ ] 5.3 Verify: open browser at localhost:3000, see dashboard (empty or with projects), create project dialog works, new project appears in list

## 6. Project Detail Page

- [ ] 6.1 Create `frontend/src/app/projects/[id]/page.tsx` — `"use client"` component. Use `useQuery` to fetch `GET /api/v1/projects/{id}`. Display: project name (h1), topic, target_format badge, content_goal badge, status badge, raw_notes in a styled block, created_at/updated_at. Back button linking to `/`. Handle 404 with "Project not found" message. Loading state while fetching.
- [ ] 6.2 Verify: click project card from dashboard → navigate to detail page → see project data

## 7. Settings Page

- [ ] 7.1 Create `frontend/src/app/settings/page.tsx` — `"use client"` component. Use `useQuery` to fetch `GET /api/v1/settings/llm`. Render each provider in a card: name, API key input (masked, type=password, pre-filled with masked value from `api_key_masked`), base URL (read-only text), enabled toggle, model name. Use `settings-store` for pending edits. "Test Connection" button calls `GET /api/v1/settings/llm/status` and shows green check / red X per provider. "Save" button calls `PATCH /api/v1/settings/llm` with pending changes, shows success toast, resets pending store, invalidates settings query.
- [ ] 7.2 Verify: navigate to Settings, see provider config, test connection shows status, update API key + save shows toast

## 8. Build & Lint Verification

- [ ] 8.1 Run `npm run lint` — passes
- [ ] 8.2 Run `npm run build` — passes with no type errors
- [ ] 8.3 Verify: `npm run dev` starts, dashboard loads at localhost:3000, can create project, navigate to detail, navigate to settings
