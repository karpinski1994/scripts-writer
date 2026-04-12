## Context

Phase 3 implemented the ICP agent, pipeline state machine (StepType, StepStatus, TRANSITIONS, DEPENDENCY_MAP), PipelineOrchestrator with `run_step()`, pipeline API endpoints, and ICP API endpoints. The orchestrator currently only handles ICP step type in `_build_agent_inputs()` and does not implement `_invalidate_downstream()`. The database has `pipeline_steps` and `script_versions` tables, but no code populates `script_versions` and there are no export endpoints.

The LLD defines 5 additional creative agents (Hook, Narrative, Retention, CTA, Writer), each with specific input/output models, plus the orchestrator logic for assembling upstream context and invalidating downstream steps.

## Goals / Non-Goals

**Goals:**
- All 5 creative agents (Hook, Narrative, Retention, CTA, Writer) generating structured output
- Orchestrator assembling correct upstream context for each step type
- Downstream step invalidation when re-running a completed step
- Script version persistence and API endpoints
- Export to .txt and .md with formatted output
- Unit tests for all agent prompt construction

**Non-Goals:**
- Analysis agents (FactCheck, Readability, Copyright, Policy — Phase 8)
- WebSocket streaming (Phase 6)
- Frontend pipeline UI (Phase 6)
- Script editor / Tiptap (Phase 7)
- Run-all endpoint (deferred)
- Branch project (Phase 9)

## Decisions

### 1. Each creative agent follows the same pattern as ICPAgent
**Choice:** Each agent extends `BaseAgent[InputT, OutputT]` with a Pydantic AI agent for structured output
**Alternative:** Use raw `ProviderFactory.execute_with_failover()` and parse responses manually
**Rationale:** Consistency with Phase 3. Pydantic AI handles structured output parsing, retries on validation errors, and model configuration. The BaseAgent provides cache integration and step tracking.

### 2. Hook agent returns 5+ suggestions, user selects one
**Choice:** `HookAgentOutput` contains `suggestions: list[HookSuggestion]` with `min_length=5`, user selects via `selected_option` on pipeline step
**Alternative:** Return a single best hook
**Rationale:** Users need choice. The LLD specifies "5+ ranked hook suggestions with effectiveness scores." Selection flows downstream via `selected_option`.

### 3. Narrative agent recommends one pattern but allows any selection
**Choice:** `NarrativeAgentOutput` has `recommended_index` and `is_recommended` flag on each pattern, but user can select any pattern
**Alternative:** Only return the recommended pattern
**Rationale:** The LLD specifies "4+ narrative patterns with fit scores, recommendation." Users should see options with a recommendation badge.

### 4. Retention agent allows multi-select
**Choice:** `selected_option` for retention step stores a list of techniques, not a single selection
**Alternative:** Force single selection
**Rationale:** The LLD specifies "technique checkboxes with placements, multi-select." Multiple retention techniques can be combined.

### 5. Writer agent assembles all upstream selections into a complete script
**Choice:** `WriterAgentInput` includes ICP, hook, narrative, retention techniques list, CTA, topic, format, and raw notes
**Alternative:** Writer only receives the script outline without full ICP
**Rationale:** The writer needs full context to generate a coherent script. The ICP shapes tone, the hook shapes the opening, the narrative shapes structure, retention shapes pacing, and the CTA shapes the close.

### 6. Downstream invalidation resets output_data and selected_option
**Choice:** When a completed step is re-run, all steps after it in STEP_ORDER are reset to PENDING with `output_data=None` and `selected_option=None`
**Alternative:** Only invalidate the immediately next step
**Rationale:** If ICP changes, all downstream outputs are potentially invalid. Cascade invalidation ensures consistency.

### 7. Export service writes to filesystem
**Choice:** `ExportService` writes files to `data/exports/` directory, returns file path for download
**Alternative:** Generate export in memory and return as response body
**Rationale:** Filesystem export allows caching, resuming downloads, and inspection. The LLD specifies `ExportService` with `export_txt()` and `export_md()` returning `Path`.

## Risks / Trade-offs

- **[Risk] LLM output quality for Writer agent** → Mitigation: The writer receives structured, curated inputs from all upstream steps. If output is poor, user can re-run or adjust upstream selections.

- **[Risk] Orchestrator context assembly complexity** → Mitigation: `_build_agent_inputs()` uses a `match` statement on `StepType`, each case is self-contained and testable. Unit tests verify each case.

- **[Trade-off] No streaming in Phase 4** → Agent execution is request-response. The Writer agent may take 10-30 seconds but the API call blocks until complete. WebSocket streaming is Phase 6.

- **[Trade-off] Export to filesystem, not S3** → For a local/dev tool, filesystem is sufficient. Cloud storage can be added later without changing the service interface.
