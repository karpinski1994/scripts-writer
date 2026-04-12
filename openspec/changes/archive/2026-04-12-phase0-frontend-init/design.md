## Context

The backend is running at `localhost:8000` with `/health` endpoint. The frontend directory does not exist yet. The dev plan (`docs/09-development-plan.md`) specifies Next.js 14+ with App Router, Shadcn/UI, Tailwind CSS, Zustand, TanStack Query, React Hook Form + Zod, and Tiptap (for Phase 7).

The frontend must run at `localhost:3000` and be able to make API calls to the backend. CORS is already configured on the backend to allow `http://localhost:3000`.

## Goals / Non-Goals

**Goals:**
- Runnable Next.js frontend at `localhost:3000` with a blank page
- All frontend dependencies installed for Phases 5–8
- Shadcn/UI initialized and functional
- ESLint + Prettier configured and passing

**Non-Goals:**
- Any UI components or pages beyond the default Next.js page
- API client or data fetching (Phase 5)
- State management setup (Phase 5)
- WebSocket integration (Phase 6)
- Tiptap editor installation (Phase 7)

## Decisions

### 1. Next.js 14+ with App Router
**Choice:** Use Next.js 14+ with App Router (`src/app/` directory) and TypeScript.
**Alternative:** Pages Router, Remix, Vite + React
**Rationale:** App Router is the modern Next.js standard. The LLD specifies `src/app/` layout structure. Server components and streaming support will be useful for the pipeline UI.

### 2. Shadcn/UI with New York style and Zinc theme
**Choice:** Initialize Shadcn/UI with New York style, Zinc color theme, and CSS variables.
**Alternative:** Material UI, Chakra UI, custom components, Default style
**Rationale:** Shadcn/UI provides accessible, composable components that integrate with Tailwind. New York style is denser (good for data-heavy UI). Zinc theme is neutral and professional. The dev plan explicitly specifies Shadcn/UI.

### 3. pnpm over npm
**Choice:** Use `npm` for package management (consistent with `create-next-app` defaults).
**Alternative:** pnpm, yarn
**Rationale:** `create-next-app` scaffolds with npm by default. Switching to pnpm later is trivial. No need to add a package manager constraint at this stage.

### 4. ESLint + Prettier together
**Choice:** Use ESLint for linting and Prettier for formatting as separate tools, with `eslint-config-prettier` to disable conflicting rules.
**Alternative:** ESLint only with formatting rules, Biome
**Rationale:** Standard React/Next.js setup. Prettier handles formatting consistently. `eslint-config-prettier` turns off ESLint formatting rules that conflict with Prettier.

## Risks / Trade-offs

- **[Risk] Shadcn/UI CLI may prompt for config interactively** → Mitigation: Use `--yes` or `--defaults` flags if available. If interactive, answer with the values specified in the dev plan (New York, Zinc, CSS variables).

- **[Risk] Next.js 15 may be latest and have breaking changes vs docs written for Next.js 14** → Mitigation: Pin to `create-next-app@14` if needed, or accept Next.js 15 if it's backward-compatible with App Router.

- **[Trade-off] Installing all deps now vs just-in-time** → Some deps (Tiptap, react-markdown) won't be used until Phase 7. Installing them now avoids context-switching later and ensures the `package.json` is stable.
