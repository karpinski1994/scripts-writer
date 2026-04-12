## 1. Analysis Schemas

- [ ] 1.1 Create `backend/app/schemas/analysis.py` — `Finding` (type, severity, text, suggestion, confidence), `FactCheckAgentInput/Output`, `ReadabilityAgentInput/Output` (+ flesch_kincaid_score, gunning_fog_score), `CopyrightAgentInput/Output`, `PolicyAgentInput/Output`, `AnalysisResultResponse`
- [ ] 1.2 Verify: `uv run python -c "from app.schemas.analysis import Finding, FactCheckAgentInput, ReadabilityAgentOutput; print('ok')"`

## 2. Analysis Agents

- [ ] 2.1 Create `backend/app/agents/factcheck_agent.py` — `FactCheckAgent(BaseAgent)` with system prompt for factual claim identification, confidence levels, and suggestions
- [ ] 2.2 Create `backend/app/agents/readability_agent.py` — `ReadabilityAgent(BaseAgent)` with algorithmic Flesch-Kincaid + Gunning Fog score computation in `execute()`, LLM for simplification suggestions on complex sentences
- [ ] 2.3 Create `backend/app/agents/copyright_agent.py` — `CopyrightAgent(BaseAgent)` with system prompt for copyright/trademark flagging, advisory warnings
- [ ] 2.4 Create `backend/app/agents/policy_agent.py` — `PolicyAgent(BaseAgent)` with system prompt for platform policy checking (YouTube, Facebook, LinkedIn based on target_format)
- [ ] 2.5 Verify: `uv run python -c "from app.agents.factcheck_agent import FactCheckAgent; from app.agents.readability_agent import ReadabilityAgent; from app.agents.copyright_agent import CopyrightAgent; from app.agents.policy_agent import PolicyAgent; print('ok')"`

## 3. Orchestrator Extensions

- [ ] 3.1 Update `backend/app/pipeline/orchestrator.py` — add `_build_agent_inputs()` cases for StepType.FACTCHECK, READABILITY, COPYRIGHT, POLICY that fetch the latest script version content. Add `run_analysis_parallel(project_id)` method using `asyncio.gather` with `return_exceptions=True`.
- [ ] 3.2 Verify: `uv run python -c "from app.pipeline.orchestrator import PipelineOrchestrator; print('ok')"`

## 4. Analysis Service & API

- [ ] 4.1 Create `backend/app/services/analysis_service.py` — `AnalysisService` with `save_result()` (upsert: delete existing + insert new), `get_results(project_id)`, `get_result_by_type(project_id, agent_type)`. `save_result()` serializes findings as JSON, sets overall_score for readability.
- [ ] 4.2 Create `backend/app/api/analysis.py` — `POST /projects/{id}/analyze/{agent_type}`, `POST /projects/{id}/analyze/all`, `GET /projects/{id}/analysis`. Validate Writer step is completed before allowing analysis (409 if not).
- [ ] 4.3 Update `backend/app/api/router.py` — include analysis router
- [ ] 4.4 Verify: `uv run python -c "from app.api.router import router; print('ok')"`

## 5. Backend Tests

- [ ] 5.1 Create `backend/tests/unit/test_analysis_agents.py` — test prompt construction for all 4 agents, test readability score computation (known text → expected FK/GF scores), test AnalysisService upsert behavior
- [ ] 5.2 Verify: `uv run pytest tests/unit/test_analysis_agents.py -v` passes

## 6. Frontend Types & Analysis Panel

- [ ] 6.1 Create `frontend/src/types/analysis.ts` — `Finding`, `AnalysisResult`, `AgentType` types matching backend schemas
- [ ] 6.2 Create `frontend/src/components/agents/analysis-panel.tsx` — tabbed panel (Fact Check, Readability, Copyright, Policy), finding cards with severity badges, confidence, suggestion, dismiss/apply buttons, "Analyze All" button, readability score gauges on Readability tab, loading state per tab
- [ ] 6.3 Update `frontend/src/components/agents/agent-panel-wrapper.tsx` — handle analysis step types (factcheck, readability, copyright, policy) by rendering the analysis panel with the appropriate tab active
- [ ] 6.4 Update `frontend/src/components/pipeline/pipeline-view.tsx` — make analysis step cards clickable when Writer is completed
- [ ] 6.5 Verify: `npm run build` passes, `npm run lint` passes

## 7. Full Stack Verification

- [ ] 7.1 Run `uv run pytest tests/ -v` — all backend tests pass
- [ ] 7.2 Run `uv run ruff check app/` — lint clean
- [ ] 7.3 Run `npm run lint && npm run build` — frontend clean
