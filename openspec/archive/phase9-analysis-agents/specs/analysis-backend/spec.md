## Purpose

Defines the 4 analysis agents, their input/output schemas, parallel execution, persistence, and API endpoints.

## ADDED Requirements

### Requirement: Analysis agent input/output schemas
The system SHALL define in `app/schemas/analysis.py`: `Finding` (type: str, severity: str, text: str, suggestion: str, confidence: str), `FactCheckAgentInput` (script_content, topic), `FactCheckAgentOutput` (findings: list[Finding]), `ReadabilityAgentInput` (script_content), `ReadabilityAgentOutput` (findings: list[Finding], flesch_kincaid_score: float, gunning_fog_score: float), `CopyrightAgentInput` (script_content, topic), `CopyrightAgentOutput` (findings: list[Finding]), `PolicyAgentInput` (script_content, target_format), `PolicyAgentOutput` (findings: list[Finding]), `AnalysisResultResponse` (id, project_id, script_version_id, agent_type, findings: list[Finding], overall_score: float | None, created_at).

#### Scenario: Finding schema validates
- **WHEN** `Finding(type="factual_claim", severity="medium", text="...", suggestion="...", confidence="low")` is constructed
- **THEN** validation passes

### Requirement: FactCheckAgent identifies factual claims
The system SHALL provide `FactCheckAgent(BaseAgent[FactCheckAgentInput, FactCheckAgentOutput])` that analyzes script content for factual claims, flags unverifiable/questionable ones, and provides confidence levels (high/medium/low) and suggestions.

#### Scenario: FactCheck agent returns findings
- **WHEN** `FactCheckAgent.execute(input)` is called with a script containing factual claims
- **THEN** findings are returned with type="factual_claim", severity, text (quoted claim), suggestion, and confidence

### Requirement: ReadabilityAgent computes scores and flags complex sentences
The system SHALL provide `ReadabilityAgent(BaseAgent[ReadabilityAgentInput, ReadabilityAgentOutput])` that computes Flesch-Kincaid and Gunning Fog scores algorithmically, flags sentences exceeding a complexity threshold, and provides LLM-generated simplification suggestions.

#### Scenario: Readability agent returns scores and findings
- **WHEN** `ReadabilityAgent.execute(input)` is called
- **THEN** `flesch_kincaid_score` and `gunning_fog_score` are returned as floats, and complex sentences are flagged with suggestions

### Requirement: CopyrightAgent flags potential issues
The system SHALL provide `CopyrightAgent(BaseAgent[CopyrightAgentInput, CopyrightAgentOutput])` that flags text segments resembling copyrighted material and trademarked terms used without context.

#### Scenario: Copyright agent returns warnings
- **WHEN** `CopyrightAgent.execute(input)` is called
- **THEN** findings include type="copyright_warning" or "trademark_usage" with advisory severity

### Requirement: PolicyAgent checks platform policies
The system SHALL provide `PolicyAgent(BaseAgent[PolicyAgentInput, PolicyAgentOutput])` that checks script content against platform-specific policies (YouTube, Facebook, LinkedIn) based on the target_format.

#### Scenario: Policy agent checks relevant platform
- **WHEN** `PolicyAgent.execute(input)` is called with target_format="YouTube"
- **THEN** findings check against YouTube community guidelines

### Requirement: Orchestrator parallel analysis execution
The system SHALL extend `PipelineOrchestrator` with `run_analysis_parallel(project_id)` that runs all 4 analysis agents concurrently using `asyncio.gather(*tasks, return_exceptions=True)`. Each analysis step is set to RUNNING, the appropriate agent is executed, and on completion the result is saved to the `analysis_results` table (replacing any existing result for the same project + script_version + agent_type). Failed agents SHALL be marked as FAILED but shall not prevent other agents from completing.

#### Scenario: All 4 agents run in parallel
- **WHEN** `run_analysis_parallel(project_id)` is called
- **THEN** all 4 analysis pipeline steps are set to RUNNING, agents execute concurrently, and results are saved

#### Scenario: One agent fails, others succeed
- **WHEN** the FactCheck agent fails but others succeed
- **THEN** FactCheck step is marked FAILED, other steps are marked COMPLETED, and 3 analysis results are saved

### Requirement: Analysis API endpoints
The system SHALL expose: `POST /api/v1/projects/{id}/analyze/{agent_type}` (run single analysis), `POST /api/v1/projects/{id}/analyze/all` (run all in parallel), `GET /api/v1/projects/{id}/analysis` (get all analysis results). The `agent_type` path parameter SHALL accept: factcheck, readability, copyright, policy.

#### Scenario: Run single analysis
- **WHEN** `POST /api/v1/projects/{id}/analyze/factcheck` is called after Writer completes
- **THEN** the FactCheck agent runs and results are saved and returned

#### Scenario: Run all analysis
- **WHEN** `POST /api/v1/projects/{id}/analyze/all` is called
- **THEN** all 4 agents run in parallel and results are returned

#### Scenario: Get analysis results
- **WHEN** `GET /api/v1/projects/{id}/analysis` is called
- **THEN** all saved analysis results for the project are returned

#### Scenario: Analyze before Writer completes
- **WHEN** `POST /api/v1/projects/{id}/analyze/all` is called when Writer is not completed
- **THEN** a 409 error is returned with message "Writer step must be completed before analysis"

### Requirement: Analysis service persistence
The system SHALL provide `AnalysisService` that saves analysis results to the `analysis_results` table. Before inserting, it SHALL delete any existing row with the same `project_id + script_version_id + agent_type` (upsert pattern). The `findings` SHALL be serialized as JSON string. The `overall_score` SHALL be populated for readability (Flesch-Kincaid score) and null for others.

#### Scenario: Re-analysis replaces previous results
- **WHEN** analysis is run twice for the same project + script version + agent type
- **THEN** only the latest result is stored (previous is deleted)
