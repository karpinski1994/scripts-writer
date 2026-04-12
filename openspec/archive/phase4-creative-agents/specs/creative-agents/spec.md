## Purpose

Defines the 5 creative agents (Hook, Narrative, Retention, CTA, Writer), their input/output schemas, prompt construction, and the script versioning and export APIs.

## ADDED Requirements

### Requirement: Hook Agent generates ranked suggestions
The system SHALL provide `HookAgent(BaseAgent[HookAgentInput, HookAgentOutput])` with a Pydantic AI agent configured for structured hook generation. `build_prompt()` SHALL include ICP summary, topic, target format, and content goal. Output SHALL contain at least 5 `HookSuggestion` objects, each with `rank`, `text`, `rationale`, and `effectiveness_score`.

#### Scenario: Build prompt contains ICP and topic
- **WHEN** `agent.build_prompt(HookAgentInput(icp=profile, topic="Python", target_format="VSL"))` is called
- **THEN** the returned prompt string contains the ICP audience summary and "Python"

#### Scenario: Hook agent returns 5+ suggestions
- **WHEN** `HookAgent.execute(valid_input)` is called with a working LLM provider
- **THEN** an `HookAgentOutput` is returned with at least 5 suggestions, each having rank >= 1

### Requirement: Narrative Agent suggests patterns with recommendation
The system SHALL provide `NarrativeAgent(BaseAgent[NarrativeAgentInput, NarrativeAgentOutput])` with a Pydantic AI agent. Output SHALL contain at least 4 `NarrativePattern` objects with `name`, `description`, `fit_score`, `is_recommended`, and `application_notes`. One pattern SHALL have `is_recommended=True`.

#### Scenario: Build prompt contains hook and ICP
- **WHEN** `agent.build_prompt(NarrativeAgentInput(icp=profile, selected_hook="Stop writing Python the hard way", topic="Python", target_format="VSL"))` is called
- **THEN** the returned prompt contains the hook text and ICP summary

#### Scenario: One pattern is recommended
- **WHEN** `NarrativeAgent.execute(valid_input)` is called
- **THEN** exactly one pattern has `is_recommended=True` and `recommended_index` points to it

### Requirement: Retention Agent suggests techniques with placements
The system SHALL provide `RetentionAgent(BaseAgent[RetentionAgentInput, RetentionAgentOutput])`. Output SHALL contain at least 3 `RetentionTechnique` objects with `name`, `description`, `placement`, and `fit_for_format`.

#### Scenario: Build prompt contains hook and narrative
- **WHEN** `agent.build_prompt(RetentionAgentInput(icp=profile, selected_hook="hook text", selected_narrative="AIDA", target_format="VSL"))` is called
- **THEN** the returned prompt contains the hook text, narrative pattern, and format

#### Scenario: Retention agent returns techniques with placement info
- **WHEN** `RetentionAgent.execute(valid_input)` is called
- **THEN** each technique has a non-empty `placement` string

### Requirement: CTA Agent suggests calls to action
The system SHALL provide `CTAAgent(BaseAgent[CTAAgentInput, CTAAgentOutput])`. Output SHALL contain at least 2 `CTASuggestion` objects with `cta_type`, `suggested_wording`, `rationale`, and `placement_options`.

#### Scenario: Build prompt contains ICP and content goal
- **WHEN** `agent.build_prompt(CTAAgentInput(icp=profile, selected_hook="hook", selected_narrative="AIDA", content_goal="Sell"))` is called
- **THEN** the returned prompt contains the content goal and ICP pain points

#### Scenario: CTA agent returns suggestions with wording
- **WHEN** `CTAAgent.execute(valid_input)` is called
- **THEN** each suggestion has a non-empty `suggested_wording` string

### Requirement: Writer Agent generates complete script draft
The system SHALL provide `WriterAgent(BaseAgent[WriterAgentInput, WriterAgentOutput])`. Input SHALL include ICP, selected hook, selected narrative, selected retention techniques, selected CTA, target format, topic, and raw notes. Output SHALL contain a `ScriptDraft` with `content`, `format`, `structural_cues`, and `word_count`.

#### Scenario: Build prompt contains all upstream selections
- **WHEN** `agent.build_prompt(WriterAgentInput(icp=profile, selected_hook="hook", selected_narrative="AIDA", selected_retention=[...], selected_cta="Enroll now", target_format="VSL", topic="Python", raw_notes="sell Python course"))` is called
- **THEN** the returned prompt contains the hook, narrative, CTA, and raw notes

#### Scenario: Writer agent returns script draft
- **WHEN** `WriterAgent.execute(valid_input)` is called with a working LLM provider
- **THEN** a `WriterAgentOutput` is returned with a non-empty `script.content` and `script.word_count > 0`

### Requirement: Agent input/output Pydantic schemas
The system SHALL define all agent input and output schemas in `app/schemas/agents.py`: `HookSuggestion`, `HookAgentInput`, `HookAgentOutput`, `NarrativePattern`, `NarrativeAgentInput`, `NarrativeAgentOutput`, `RetentionTechnique`, `RetentionAgentInput`, `RetentionAgentOutput`, `CTASuggestion`, `CTAAgentInput`, `CTAAgentOutput`, `ScriptDraft`, `WriterAgentInput`, `WriterAgentOutput`. Agent inputs that reference ICP SHALL use `ICPProfile` from `app.schemas.icp` (not redefined).

#### Scenario: Schemas validate correctly
- **WHEN** each input schema is constructed with valid data
- **THEN** validation passes without error

### Requirement: Script version API endpoints
The system SHALL expose 4 endpoints: `GET /api/v1/projects/{id}/scripts` (list versions), `GET /api/v1/scripts/{version_id}` (get version), `POST /api/v1/projects/{id}/scripts/generate` (generate new version from writer output), `PATCH /api/v1/scripts/{version_id}` (update script content).

#### Scenario: Generate script version
- **WHEN** `POST /api/v1/projects/{id}/scripts/generate` is called after Writer agent completes
- **THEN** a new `script_versions` row is created with content from the writer output and version_number incremented

#### Scenario: Update script content
- **WHEN** `PATCH /api/v1/scripts/{version_id}` is called with updated content
- **THEN** the script version's content is updated

### Requirement: Export API endpoint
The system SHALL expose `GET /api/v1/projects/{id}/export?format=txt|md` that downloads the latest script version as a file in the requested format.

#### Scenario: Export as markdown
- **WHEN** `GET /api/v1/projects/{id}/export?format=md` is called
- **THEN** a .md file is returned as a download with formatted content including metadata header

#### Scenario: Export as plain text
- **WHEN** `GET /api/v1/projects/{id}/export?format=txt` is called
- **THEN** a .txt file is returned as a download with raw script content
