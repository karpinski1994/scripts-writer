## Why

Phase 0 requires two runnable servers — backend and frontend. The backend is initialized, but the frontend doesn't exist yet. Steps 0.4–0.6 and 0.10 of the development plan are incomplete. Without the frontend, there is no dev loop for UI work and Phase 5+ cannot begin.

## What Changes

- Initialize `frontend/` with Next.js 14+ (App Router, TypeScript, Tailwind CSS, ESLint, `src/` directory)
- Install frontend dependencies: `@tanstack/react-query`, `zustand`, `react-hook-form`, `@hookform/resolvers`, `zod`, `react-markdown`, `lucide-react`
- Initialize Shadcn/UI (New York style, Zinc theme, CSS variables)
- Configure `eslint` + `prettier` in `frontend/`

## Capabilities

### New Capabilities
- `frontend-foundation`: Next.js frontend project with App Router, TypeScript, Tailwind CSS, Shadcn/UI component library, state management dependencies, and linter/formatter configuration

### Modified Capabilities
<!-- No existing capabilities modified -->
