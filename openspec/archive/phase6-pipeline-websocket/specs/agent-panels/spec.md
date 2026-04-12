## Purpose

Defines the five agent panels (ICP, Hook, Narrative, Retention, CTA) with their selection flows, and the TypeScript types for agent output schemas.

## ADDED Requirements

### Requirement: Agent output TypeScript types
The system SHALL define TypeScript interfaces in `frontend/src/types/agents.ts` matching backend agent output schemas: `HookSuggestion` (rank, text, rationale, effectiveness_score), `HookAgentOutput` (suggestions), `NarrativePattern` (name, description, fit_score, is_recommended, application_notes), `NarrativeAgentOutput` (patterns, recommended_index), `RetentionTechnique` (name, description, placement, fit_for_format), `RetentionAgentOutput` (techniques), `CTASuggestion` (cta_type, suggested_wording, rationale, placement_options), `CTAAgentOutput` (suggestions), `ScriptDraft` (content, format, structural_cues, word_count), `WriterAgentOutput` (script), `ICPAgentOutput` (icp: ICPProfile, confidence, suggestions).

#### Scenario: Types match backend outputs
- **WHEN** an agent output is parsed from `output_data` JSON
- **THEN** it can be assigned to the corresponding TypeScript interface without type errors

### Requirement: ICP panel with review, edit, approve
The system SHALL provide `icp-panel.tsx` that displays the ICP profile fields (demographics, psychographics, pain points, desires, objections, language_style) in a read-only view. An edit toggle SHALL switch fields to editable inputs. "Re-run ICP Agent" SHALL call `POST /pipeline/run/icp`. "Approve & Continue" SHALL call `PATCH /pipeline/{step_id}` with `selected_option: { approved: true, ...icp_data }` and navigate to the Hook step.

#### Scenario: View generated ICP
- **WHEN** the ICP step is completed and selected as active
- **THEN** the ICP profile fields are displayed in read-only mode

#### Scenario: Approve ICP and continue
- **WHEN** "Approve & Continue" is clicked
- **THEN** `PATCH /pipeline/{step_id}` is called with selected_option, and activeStepType changes to "hook"

#### Scenario: Re-run ICP
- **WHEN** "Re-run ICP Agent" is clicked
- **THEN** `POST /pipeline/run/icp` is called and the step status becomes running

### Requirement: Hook panel with selection and custom hook
The system SHALL provide `hook-panel.tsx` that displays 5+ ranked hook suggestions as radio options. Each option shows rank, text, rationale, and effectiveness score. A "Custom Hook" text input SHALL allow entering a custom hook instead. "Continue with Hook" SHALL call `PATCH /pipeline/{step_id}` with the selected or custom hook as `selected_option`.

#### Scenario: Select a suggested hook
- **WHEN** a hook suggestion radio is selected and "Continue" is clicked
- **THEN** `PATCH /pipeline/{step_id}` is called with `selected_option: { rank, text, rationale, effectiveness_score }`

#### Scenario: Enter custom hook
- **WHEN** custom hook text is entered
- **THEN** the radio selection is cleared and the custom hook will be used on Continue

### Requirement: Narrative panel with pattern selection
The system SHALL provide `narrative-panel.tsx` that displays narrative patterns as radio options with name, description, fit score, and recommendation badge (`is_recommended`). "Continue" SHALL save the selected pattern.

#### Scenario: Select recommended pattern
- **WHEN** the recommended pattern is shown with a badge
- **THEN** it is pre-selected and "Continue" saves it as selected_option

### Requirement: Retention panel with multi-select
The system SHALL provide `retention-panel.tsx` that displays retention techniques as checkboxes (multi-select). Each technique shows name, description, and placement info. "Continue with N techniques" SHALL save the selected techniques as `selected_option: { techniques: [...] }`.

#### Scenario: Select multiple techniques
- **WHEN** 2 techniques are checked and "Continue" is clicked
- **THEN** `PATCH /pipeline/{step_id}` is called with `selected_option: { techniques: [...] }`

### Requirement: CTA panel with type selection and customization
The system SHALL provide `cta-panel.tsx` that displays CTA suggestions grouped by type. Each suggestion shows type, suggested wording, and placement options. "Customize" input allows editing the wording. "Continue" SHALL save the selected/customized CTA.

#### Scenario: Select CTA and customize wording
- **WHEN** a CTA type is selected, wording is customized, and "Continue" is clicked
- **THEN** `PATCH /pipeline/{step_id}` is called with `selected_option: { cta_type, cta_text, placement }`

### Requirement: Agent panel shows "Run Agent" button for pending steps
The system SHALL show a "Run {Step Name} Agent" button for steps that are pending with met dependencies. For steps with unmet dependencies, the button SHALL be disabled with a tooltip explaining what's needed.

#### Scenario: Run agent for pending step
- **WHEN** the Hook step is pending and ICP is completed
- **THEN** "Run Hook Agent" button is enabled and clicking it calls `POST /pipeline/run/hook`

#### Scenario: Button disabled for unmet dependency
- **WHEN** the Hook step is pending but ICP is not completed
- **THEN** "Run Hook Agent" button is disabled with tooltip "Requires: ICP"
