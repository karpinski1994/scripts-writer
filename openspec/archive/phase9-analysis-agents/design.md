## Context

Phases 0–8 built the full creative pipeline with all 6 creative agents, NotebookLM integration, WebSocket events, and frontend agent panels. The `AnalysisResult` DB model already exists with fields: id, project_id, script_version_id, agent_type, findings (JSON text), overall_score, created_at. The CHECK constraint allows agent_type: 'factcheck', 'readability', 'copyright', 'policy'. The pipeline state machine already defines StepType.factcheck/readability/copyright/policy with dependencies on WRITER.

The orchestrator currently handles only creative step types in `_build_agent_inputs()`. Analysis steps have no agent implementations. The frontend pipeline-view shows an "Analysis" row with 4 step cards but they're always pending. There is no analysis API endpoint.

## Goals / Non-Goals

**Goals:**
- 4 analysis agents (FactCheck, Readability, Copyright, Policy) generating structured findings
- Parallel execution via `asyncio.gather`
- Analysis API endpoints (run individual, run all, get results)
- Frontend tabbed analysis panel with severity badges, confidence, suggestions
- Analysis results persisted to existing `analysis_results` table

**Non-Goals:**
- Re-run analysis with different parameters (deferred)
- Export analysis report (Phase 10)
- Analysis agent customization (deferred)
- NotebookLM context for analysis agents (deferred)
- Auto-apply suggestions to script (Phase 10)

## Decisions

### 1. Analysis agents follow the same BaseAgent pattern as creative agents
**Choice:** Each analysis agent extends `BaseAgent[InputT, OutputT]` with a Pydantic AI agent for structured output
**Rationale:** Consistency. Same cache, failover, and streaming infrastructure. The input is the script content + metadata; the output is structured findings.

### 2. Analysis agents receive script content from the latest ScriptVersion
**Choice:** `_build_agent_inputs()` for analysis steps fetches the latest `script_versions` row for the project and passes the content as input
**Rationale:** Analysis operates on the final script, not on raw notes. The latest version is the canonical content.

### 3. Parallel execution with `asyncio.gather`
**Choice:** `run_analysis_parallel()` runs all 4 agents concurrently using `asyncio.gather(*tasks, return_exceptions=True)`. Results are collected even if some fail.
**Rationale:** Analysis agents are independent — no dependencies between them. Running in parallel reduces total wait time from ~4x to ~1x. `return_exceptions=True` ensures one failure doesn't cancel the others.

### 4. Analysis results replace previous results for the same agent_type + script_version
**Choice:** Before saving new analysis results, delete any existing rows with the same `project_id + script_version_id + agent_type`
**Rationale:** The UNIQUE constraint on (project_id, script_version_id, agent_type) would otherwise cause insert failures on re-run. Re-analysis replaces previous findings.

### 5. Analysis panel is a separate route/section, not embedded in agent panels
**Choice:** The analysis panel renders when the user clicks an "Analyze" button or when an analysis step is selected in the pipeline view. It shows as a tabbed panel replacing the creative agent panel area.
**Rationale:** Analysis is post-Writer — it's a different phase of the pipeline. Mixing it with creative panels would be confusing.

### 6. Readability agent computes scores algorithmically + LLM suggestions
**Choice:** The Readability agent computes Flesch-Kincaid and Gunning Fog scores algorithmically (no LLM needed for scores), then uses LLM to generate simplification suggestions for flagged sentences
**Rationale:** Score computation is deterministic math — no need for LLM variability. LLM is used only for generating helpful suggestions for complex sentences.

## Risks / Trade-offs

- **[Risk] LLM hallucinations in fact-checking** → Mitigation: Findings are advisory, not authoritative. UI shows confidence levels and "advisory only" disclaimer. User has final say.

- **[Trade-off] No incremental analysis** → Re-running analysis replaces all previous findings. Incremental (append-only) would complicate the UI and DB schema. Users can re-run to get fresh analysis.

- **[Trade-off] Readability scores are English-only** → The Flesch-Kincaid and Gunning Fog formulas are designed for English. Non-English scripts will get unreliable scores. This is acceptable for v1.
