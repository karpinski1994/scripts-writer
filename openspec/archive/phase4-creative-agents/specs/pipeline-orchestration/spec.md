## Purpose

Defines the extension of the pipeline orchestrator to handle all creative step types (Hook, Narrative, Retention, CTA, Writer) with upstream context assembly and downstream step invalidation.

## ADDED Requirements

### Requirement: Orchestrator assembles upstream context for all creative steps
The system SHALL extend `PipelineOrchestrator._build_agent_inputs()` to handle `StepType.HOOK`, `StepType.NARRATIVE`, `StepType.RETENTION`, `StepType.CTA`, and `StepType.WRITER`. Each case SHALL read the `selected_option` from upstream completed steps and construct the appropriate agent input model.

#### Scenario: Hook agent input includes ICP from upstream
- **WHEN** `run_step(project_id, StepType.HOOK)` is called
- **THEN** the HookAgentInput contains the ICP profile from the completed ICP step's `selected_option` (or `output_data` if no selection)

#### Scenario: Narrative agent input includes ICP and selected hook
- **WHEN** `run_step(project_id, StepType.NARRATIVE)` is called
- **THEN** the NarrativeAgentInput contains the ICP profile and `selected_hook` from the Hook step's `selected_option`

#### Scenario: Retention agent input includes ICP, hook, and narrative
- **WHEN** `run_step(project_id, StepType.RETENTION)` is called
- **THEN** the RetentionAgentInput contains ICP, selected hook, and selected narrative from upstream steps

#### Scenario: CTA agent input includes ICP, hook, and narrative
- **WHEN** `run_step(project_id, StepType.CTA)` is called
- **THEN** the CTAAgentInput contains ICP, selected hook, and selected narrative

#### Scenario: Writer agent input includes all upstream selections
- **WHEN** `run_step(project_id, StepType.WRITER)` is called
- **THEN** the WriterAgentInput contains ICP, selected hook, selected narrative, selected retention techniques, selected CTA, topic, format, and raw notes

### Requirement: Downstream step invalidation on re-run
The system SHALL implement `PipelineOrchestrator._invalidate_downstream(project_id, from_step)` that resets all steps after `from_step` in STEP_ORDER to `status=PENDING`, clears `output_data`, and clears `selected_option`. This SHALL be called before re-running a completed step.

#### Scenario: Re-running ICP invalidates all downstream steps
- **WHEN** `run_step(project_id, StepType.ICP)` is called and the ICP step is already COMPLETED
- **THEN** all steps with step_order > 0 are reset to PENDING with output_data=None and selected_option=None

#### Scenario: Re-running Hook invalidates Narrative through Writer
- **WHEN** `run_step(project_id, StepType.HOOK)` is called and the Hook step is already COMPLETED
- **THEN** Narrative, Retention, CTA, and Writer steps are reset to PENDING; ICP step remains COMPLETED

#### Scenario: Re-running Writer does not invalidate any steps
- **WHEN** `run_step(project_id, StepType.WRITER)` is called and the Writer step is already COMPLETED
- **THEN** no steps are invalidated (Writer is the last creative step)

### Requirement: Pipeline step update invalidates downstream
The system SHALL extend the PATCH pipeline step endpoint to call `_invalidate_downstream()` when a completed step's `selected_option` is updated, because changing a selection means downstream outputs are stale.

#### Scenario: Changing hook selection invalidates downstream
- **WHEN** `PATCH /api/v1/projects/{id}/pipeline/{step_id}` is called with a new `selected_option` for a completed Hook step
- **THEN** Narrative, Retention, CTA, and Writer steps are reset to PENDING
