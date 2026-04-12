## Purpose

Defines how the orchestrator resolves NotebookLM context and injects it into creative agent prompts.

## ADDED Requirements

### Requirement: Agent input schemas include notebooklm_context
All creative agent input schemas (`ICPAgentInput`, `HookAgentInput`, `NarrativeAgentInput`, `RetentionAgentInput`, `CTAAgentInput`, `WriterAgentInput`) SHALL have a `notebooklm_context: str | None = None` field.

#### Scenario: Agent input with NotebookLM context
- **WHEN** `HookAgentInput(icp=..., topic="...", notebooklm_context="Research shows...")` is constructed
- **THEN** the field is set and included in the prompt

#### Scenario: Agent input without NotebookLM context
- **WHEN** `HookAgentInput(icp=..., topic="...")` is constructed without notebooklm_context
- **THEN** `notebooklm_context` is `None` and the agent works as before

### Requirement: Orchestrator resolves NotebookLM context for each creative step
`PipelineOrchestrator._build_agent_inputs()` SHALL, when a notebook is connected to the project (project.notebooklm_notebook_id is not None), call `NotebookLMService.get_step_context()` with the step type and include the result as `notebooklm_context` in the agent input. If the query fails or returns None, `notebooklm_context` SHALL be `None` and the agent SHALL proceed without it.

#### Scenario: ICP step gets NotebookLM context
- **WHEN** `run_step(project_id, StepType.ICP)` is called with a connected notebook
- **THEN** the ICP agent receives `notebooklm_context` with audience research insights

#### Scenario: Hook step gets NotebookLM context
- **WHEN** `run_step(project_id, StepType.HOOK)` is called with a connected notebook
- **THEN** the Hook agent receives `notebooklm_context` with hook-related insights from the notebook

#### Scenario: NotebookLM query fails gracefully
- **WHEN** `get_step_context()` raises a `NotebookLMAPIError`
- **THEN** `notebooklm_context` is set to `None`, a warning is logged, and the agent proceeds with raw notes only

### Requirement: Agent build_prompt includes notebooklm_context when present
Each creative agent's `build_prompt()` method SHALL include the `notebooklm_context` text in the prompt when it is not None, formatted as "Additional research context from NotebookLM:\n{notebooklm_context}". When None, the prompt SHALL be identical to the current behavior.

#### Scenario: ICP agent prompt with context
- **WHEN** `ICPAgent.build_prompt(input_with_context)` is called
- **THEN** the prompt contains "Additional research context from NotebookLM:" followed by the context text

#### Scenario: ICP agent prompt without context
- **WHEN** `ICPAgent.build_prompt(input_without_context)` is called
- **THEN** the prompt does not contain "NotebookLM" — identical to current behavior

### Requirement: Step-specific NotebookLM queries
`NotebookLMService.get_step_context()` SHALL generate different queries per step type:
- ICP: "What audience insights and demographic information are relevant for defining an Ideal Customer Profile about {topic} for a {format}?"
- Hook: "What attention-grabbing approaches, opening strategies, or hook techniques are mentioned for content about {topic}?"
- Narrative: "What narrative patterns, storytelling approaches, or structural frameworks are discussed for {topic} content?"
- Retention: "What techniques for keeping audiences engaged, pattern interrupts, or retention strategies are mentioned?"
- CTA: "What calls to action, conversion techniques, or action-driving strategies are discussed for {topic}?"
- Writer: "Summarize all key insights, arguments, evidence, and recommendations that should be incorporated into a {format} script about {topic}."

#### Scenario: Different queries per step
- **WHEN** `get_step_context(project_id, StepType.HOOK)` is called
- **THEN** the query to NotebookLM mentions "attention-grabbing approaches" and "hook techniques"
