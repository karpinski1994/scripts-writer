## Why

Phases 0–8 built the complete creative pipeline with NotebookLM enrichment. Users can go from raw notes to a polished script draft. But there's no quality assurance — no fact-checking, readability scoring, copyright flagging, or policy compliance checking. Users must manually verify their scripts. Phase 9 adds 4 analysis agents that run after the Writer step, plus a frontend tabbed panel to review findings.

## What Changes

- Add `FactCheckAgent`, `ReadabilityAgent`, `CopyrightAgent`, `PolicyAgent` following the `BaseAgent` pattern
- Add analysis agent input/output schemas (`FactCheckAgentInput/Output`, etc.)
- Extend `PipelineOrchestrator` with `run_analysis_parallel()` using `asyncio.gather` for 4 agents
- Add `app/schemas/analysis.py` — `AnalysisResultResponse`, `FindingResponse`
- Add `app/services/analysis_service.py` — aggregation and persistence
- Add `app/api/analysis.py` — `POST /analyze/{agent_type}`, `POST /analyze/all`, `GET /analysis`
- Add `frontend/src/types/analysis.ts` — TypeScript types for analysis results
- Add `frontend/src/components/agents/analysis-panel.tsx` — tabbed panel with findings cards
- Update pipeline-view to show Analysis row as interactive after Writer completes

## Capabilities

### New Capabilities
- `analysis-backend`: 4 analysis agents, parallel execution, persistence, API endpoints
- `analysis-frontend`: Tabbed analysis panel with severity badges, confidence, suggestions, dismiss/apply

### Modified Capabilities
- `pipeline-management`: Orchestrator now handles analysis step types (factcheck, readability, copyright, policy)
