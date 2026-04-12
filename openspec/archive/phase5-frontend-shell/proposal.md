## Why

Phases 0–4 built the complete backend: project CRUD, LLM adapter, all creative agents, pipeline orchestration, script versioning, and export. But none of this is usable from a browser — the frontend is still the default Next.js boilerplate page. Phase 5 connects the frontend to the backend so a user can create projects, see them in a dashboard, navigate to project details, and configure LLM providers — all from the browser.

## What Changes

- Add typed API client (`api.ts`) wrapping fetch with base URL from `NEXT_PUBLIC_API_URL`
- Add TypeScript interfaces matching all backend response schemas (Project, PipelineStep, ICPProfile, ScriptVersion, LLMConfig, etc.)
- Add Zustand stores for project list/active project and LLM settings
- Replace the default layout with a root layout containing TanStack Query provider and sidebar navigation (Dashboard, Settings)
- Replace the default home page with a Dashboard showing project cards (name, format badge, status badge, updated_at), "New Project" button, and empty state
- Add a create-project dialog with Zod-validated form (name, topic, target_format, content_goal, raw_notes)
- Add a project detail page at `/projects/[id]` showing metadata and raw notes
- Add a settings page at `/settings` with LLM provider config (API key inputs masked, enable/disable, test connection, save)

## Capabilities

### New Capabilities
- `dashboard`: Project list view with cards, create-project dialog, empty state, navigation to project detail
- `project-detail`: Project detail page showing metadata, raw notes, and navigation back to dashboard
- `settings`: LLM provider configuration page with API key management, provider toggles, and connectivity testing

### Modified Capabilities
- (none — this is the first frontend work)

## Impact

- **New files**: `src/lib/api.ts`, `src/types/project.ts`, `src/types/pipeline.ts`, `src/types/icp.ts`, `src/types/script.ts`, `src/types/settings.ts`, `src/stores/project-store.ts`, `src/stores/settings-store.ts`, `src/components/dashboard/create-project-dialog.tsx`, `src/app/projects/[id]/page.tsx`, `src/app/settings/page.tsx`
- **Modified files**: `src/app/layout.tsx` (add providers + sidebar), `src/app/page.tsx` (replace with dashboard)
- **New Shadcn/UI components needed**: `dialog`, `input`, `label`, `select`, `textarea`, `badge`, `card`, `separator`, `sidebar`, `sheet`, `tooltip`, `sonner` (toast)
