## Why

Phase 3 built the ICP agent, pipeline state machine, and orchestrator — the backbone for agent execution. But only one agent (ICP) works, and there's no way to progress through the full creative pipeline. The app can generate an ICP profile, but can't turn it into hooks, narratives, retention strategies, CTAs, or a finished script. Phase 4 completes the creative pipeline so a user can go from raw notes to an exported script via the API.

## What Changes

- Add `HookAgent` that generates 5+ ranked hook suggestions from ICP + topic
- Add `NarrativeAgent` that suggests 4+ narrative patterns with fit scores and recommendation
- Add `RetentionAgent` that suggests retention techniques with placement guidance
- Add `CTAAgent` that suggests call-to-action options with wording + placement
- Add `WriterAgent` that generates a complete script draft incorporating all upstream selections
- Extend `PipelineOrchestrator._build_agent_inputs()` to assemble context for Hook, Narrative, Retention, CTA, and Writer (pulling from previous steps' `selected_option`)
- Implement `PipelineOrchestrator._invalidate_downstream()` to reset downstream steps when a completed step is re-run
- Add script schemas (`ScriptVersionResponse`, `ScriptUpdateRequest`) and API endpoints
- Add `ExportService` with txt and md export, and export API endpoint
- Add unit tests for all creative agents' prompt construction

## Capabilities

### New Capabilities
- `creative-agents`: Hook, Narrative, Retention, CTA, and Writer agents with Pydantic AI structured output, plus script versioning and export
- `pipeline-orchestration`: Extended orchestrator with upstream context assembly for all creative steps and downstream invalidation on re-run

### Modified Capabilities
- `pipeline-management`: Orchestrator now handles all 6 creative step types (ICP + Hook + Narrative + Retention + CTA + Writer)

## Impact

- **New files**: `app/agents/hook_agent.py`, `app/agents/narrative_agent.py`, `app/agents/retention_agent.py`, `app/agents/cta_agent.py`, `app/agents/writer_agent.py`, `app/schemas/script.py`, `app/services/export_service.py`, `app/api/scripts.py`, `app/api/export.py`, `tests/unit/test_agents.py`
- **Modified files**: `app/pipeline/orchestrator.py` (extend `_build_agent_inputs`, add `_invalidate_downstream`), `app/api/router.py` (add scripts + export routers)
- **New API surface**: 4 endpoints under `/api/v1/scripts/`, 1 endpoint under `/api/v1/projects/{id}/export`
