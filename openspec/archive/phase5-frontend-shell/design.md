## Context

The frontend was initialized in Phase 0 with Next.js 16 (App Router), Shadcn/UI (base-nova style), Tailwind CSS 4, Zustand, TanStack Query, React Hook Form + Zod, and Lucide React. The current state is the default `create-next-app` boilerplate — a single page with Next.js branding. Only the `Button` Shadcn/UI component has been installed.

The backend is fully functional with project CRUD, pipeline, ICP, agents, scripts, export, and settings endpoints. All return JSON at `/api/v1/*`. CORS is configured to allow `localhost:3000`.

## Goals / Non-Goals

**Goals:**
- API client connecting frontend to backend
- TypeScript types matching backend schemas
- Dashboard with project list and create-project flow
- Project detail page with metadata display
- Settings page with LLM provider configuration
- Sidebar navigation between Dashboard and Settings
- TanStack Query for data fetching, Zustand for client-side UI state

**Non-Goals:**
- Pipeline view and agent panels (Phase 6)
- Script editor (Phase 7)
- Analysis panels (Phase 8)
- WebSocket streaming (Phase 6)
- Export UI (Phase 9)
- Responsive mobile layout (stretch goal, not blocking)
- Authentication (single-user app, no auth)

## Decisions

### 1. API client wraps fetch with typed methods
**Choice:** Create `api.ts` with `api.get()`, `api.post()`, `api.patch()`, `api.delete()` wrapping the native `fetch` API, base URL from `NEXT_PUBLIC_API_URL` env var (default `http://localhost:8000`)
**Alternative:** Use `axios` or `ky`
**Rationale:** No extra dependency needed. Next.js polyfills fetch. The wrapper handles JSON parsing, error responses, and base URL. Matches LLD.

### 2. Shadcn/UI base-nova style with `@base-ui/react` primitives
**Choice:** Use the existing Shadcn/UI setup (base-nova style, `@base-ui/react` primitives). Install additional Shadcn/UI components via `npx shadcn@latest add` as needed.
**Alternative:** Switch to Shadcn/UI default (Radix) style
**Rationale:** The project already uses base-nova style with `@base-ui/react`. Consistency matters. Don't mix component systems.

### 3. TanStack Query for server state, Zustand for client UI state
**Choice:** Use TanStack Query for all API data fetching (projects, settings, pipeline). Use Zustand only for client-side UI state (active project ID in sidebar, form state).
**Alternative:** Zustand for everything
**Rationale:** TanStack Query handles caching, refetching, stale-while-revalidate, and loading/error states. It's the right tool for server state. Zustand is simpler for pure client state. Matches TRD and HLD.

### 4. App Router with `use client` for interactive components
**Choice:** Use Next.js App Router. Server Components for layout and static shell. `"use client"` for interactive components (forms, dialogs, data-fetching pages).
**Alternative:** Pages Router
**Rationale:** App Router is already configured. Server Components reduce client JS for the layout shell. Interactive pages need `"use client"` for hooks.

### 5. Sidebar navigation using Shadcn/UI Sidebar component
**Choice:** Use Shadcn/UI `sidebar` component for navigation between Dashboard and Settings pages
**Alternative:** Simple nav bar at the top
**Rationale:** The LLD specifies a sidebar. It scales better for adding Pipeline and Editor navigation in later phases.

### 6. Forms use React Hook Form + Zod
**Choice:** Create-project dialog uses React Hook Form with `zodResolver` for validation matching backend `ProjectCreateRequest` schema
**Alternative:** Controlled components with manual validation
**Rationale:** Already in dependencies. Matches TRD and LLD. Zod schema can mirror backend validation.

### 7. Settings page fetches and updates via `/api/v1/settings/llm`
**Choice:** Settings page loads provider config via `GET /settings/llm`, updates via `PATCH /settings/llm`, tests connectivity via `GET /settings/llm/status`
**Alternative:** Use `.env` file directly
**Rationale:** The backend already has these endpoints. The UI makes it user-friendly.

## Risks / Trade-offs

- **[Risk] Next.js 16 breaking changes** → Mitigation: The AGENTS.md warns about this. Read `node_modules/next/dist/docs/` before writing code. Test with `npm run build` early.

- **[Risk] Shadcn/UI base-nova component availability** → Mitigation: Some components may not have base-nova variants. Fall back to building with `@base-ui/react` primitives directly if needed.

- **[Trade-off] No SSR data fetching in Phase 5** → Pages fetch data client-side with TanStack Query. SSR fetching would require server-side API calls and adds complexity. Can add later for SEO/perf.

- **[Trade-off] No optimistic updates** → Create/delete project waits for server response before updating the list. Optimistic updates add complexity; not needed for single-user tool in v1.
