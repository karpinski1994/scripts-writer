## Why

Phases 0–7 built the complete creative pipeline. But agent outputs are generic — based only on raw notes and the LLM's training data. Users often have their own research: competitor analyses, audience surveys, market research documents. Phase 8 adds Piragi RAG integration so agents can reference these documents, producing outputs tailored to the user's specific domain knowledge.

## What Changes

- Install `piragi` dependency in backend
- Add `app/integrations/piragi.py` — Piragi client wrapping Piragi local API
- Add `app/schemas/piragi.py` — request/response schemas
- Add `app/services/piragi_service.py` — DB persistence and service layer
- Add `app/api/piragi.py` — 4 endpoints (documents, connect, disconnect, query)
- Add `piragi_document_paths` column to projects table via Alembic
- Update `icp_profiles.source` CHECK constraint to include 'piragi'
- Update agent input schemas to include `piragi_context` field
- Update `PipelineOrchestrator._build_agent_inputs()` to resolve RAG context
- Add `frontend/src/types/piragi.ts` — TypeScript types
- Add `frontend/src/stores/piragi-store.ts` — Zustand store
- Add RAG context sections to agent panels (ICP, Hook, Narrative, Retention, CTA)
- Add Piragi connection UI to project detail page

## Capabilities

### New Capabilities
- `piragi-backend`: Piragi client, service, API endpoints, DB schema
- `piragi-frontend`: Connection UI, context preview, query modal

### Modified Capabilities
- `pipeline-management`: Orchestrator now resolves Piragi context per step
- `creative-agents`: Agent inputs accept `piragi_context`, prompts include reference material
- `project-crud`: Projects now store `piragi_document_paths`