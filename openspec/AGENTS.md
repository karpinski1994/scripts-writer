# Scripts Writer — Agent Rules

## Project Overview

Scripts Writer is an agentic AI pipeline for generating video scripts and marketing content. It has a FastAPI + SQLAlchemy async backend and a Next.js 14 App Router frontend.

## Key Conventions

- **Backend:** Python 3.11+, FastAPI, async SQLAlchemy, Pydantic 2.x, `uv` for package management, `ruff` for linting
- **Frontend:** Next.js 14 App Router, TypeScript, Shadcn/UI, Tailwind CSS, Zustand for state, TanStack Query for data fetching
- **Testing:** `pytest` (backend), `npm run lint && npm run build` (frontend)
- **Specs:** OpenSpec specs live in `openspec/specs/` — each capability has a `spec.md` with Purpose + Requirements + Scenarios
- **Dev plan:** `docs/09-development-plan.md` is the single source of truth for progress; always update it when completing work
- **Database:** SQLite via aiosqlite, Alembic migrations, 5 tables (Project, ICPProfile, PipelineStep, ScriptVersion, AnalysisResult)
- **LLM providers:** Modal (GLM-5.1) → Groq (Llama 3.3 70B) → Gemini (2.0 Flash) → Ollama (Llama 3.2) failover chain

## Before Writing Code

1. Read the relevant spec in `openspec/specs/` for the capability you're modifying
2. Check `docs/09-development-plan.md` for current progress and what's next
3. Follow existing patterns in the codebase — don't introduce new libraries without checking what's already used
4. Run `uv run ruff check app/` (backend) and `npm run lint` (frontend) before committing

## Common Pitfalls

- Don't confuse `backend/main.py` (uv init placeholder) with `backend/app/main.py` (the actual FastAPI app)
- WebSocket logic is in `hooks/use-websocket.ts`, not `lib/ws.ts`
- Agent types are in `types/agents.ts`; ICP-specific types also have `types/icp.ts`
- `backend/app/ws/connection.py` exports a singleton `connection_manager`; the class itself is in `handlers.py`
