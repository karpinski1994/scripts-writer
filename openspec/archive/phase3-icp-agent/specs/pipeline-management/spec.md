## Purpose

Defines the pipeline state machine, orchestrator, step execution with dependency validation, and pipeline API endpoints for the Scripts Writer backend.

## ADDED Requirements

### Requirement: Pipeline step types and statuses
The system SHALL define `StepType` enum with values: `icp`, `hook`, `narrative`, `retention`, `cta`, `writer`, `factcheck`, `readability`, `copyright`, `policy`. The system SHALL define `StepStatus` enum with values: `pending`, `running`, `completed`, `failed`. Step ordering SHALL be: icp(0) → hook(1) → narrative(2) → retention(3) → cta(4) → writer(5) → factcheck(6) → readability(7) → copyright(8) → policy(9).

#### Scenario: StepType enum contains all 10 values
- **WHEN** `StepType` enum is inspected
- **THEN** it contains exactly `icp`, `hook`, `narrative`, `retention`, `cta`, `writer`, `factcheck`, `readability`, `copyright`, `policy`

#### Scenario: StepStatus enum contains 4 values
- **WHEN** `StepStatus` enum is inspected
- **THEN** it contains exactly `pending`, `running`, `completed`, `failed`

### Requirement: Pipeline state transitions
The system SHALL define valid state transitions: `pending → running`, `running → completed`, `running → failed`, `failed → running` (retry). Invalid transitions SHALL raise `InvalidStateTransitionError`.

#### Scenario: Valid transition pending to running
- **WHEN** `can_transition(pending, running)` is called
- **THEN** `True` is returned

#### Scenario: Invalid transition pending to completed
- **WHEN** `can_transition(pending, completed)` is called
- **THEN** `False` is returned

### Requirement: Pipeline dependency validation
The system SHALL define `DEPENDENCY_MAP` specifying which steps must be completed before a given step can run: `hook` requires `icp`, `narrative` requires `hook`, `retention` requires `narrative`, `cta` requires `retention`, `writer` requires `cta`, analysis steps require `writer`. `icp` has no dependencies.

#### Scenario: Hook requires ICP to be completed
- **WHEN** `validate_step_ready(project_id, StepType.HOOK)` is called and ICP step is not completed
- **THEN** `DependencyNotMetError` is raised

#### Scenario: ICP has no dependencies
- **WHEN** `validate_step_ready(project_id, StepType.ICP)` is called
- **THEN** no error is raised

### Requirement: Pipeline orchestrator
The system SHALL provide a `PipelineOrchestrator` class that accepts an `AsyncSession`, with `run_step(project_id, step_type)` that: validates dependencies, transitions step to running, builds agent inputs, executes the agent, saves output to `pipeline_steps.output_data`, transitions step to completed, records duration and provider. On failure, transitions step to failed and stores error message.

#### Scenario: Run ICP step successfully
- **WHEN** `run_step(project_id, StepType.ICP)` is called
- **THEN** the ICP step status becomes `completed` and `output_data` contains the generated ICP profile

#### Scenario: Run step with unmet dependency
- **WHEN** `run_step(project_id, StepType.HOOK)` is called and ICP step is not completed
- **THEN** `DependencyNotMetError` is raised and step status remains `pending`

#### Scenario: Run step when LLM fails
- **WHEN** `run_step(project_id, StepType.ICP)` is called and all LLM providers fail
- **THEN** step status becomes `failed` and `error_message` is populated

### Requirement: Pipeline API endpoints
The system SHALL expose 3 endpoints: `GET /api/v1/projects/{id}/pipeline` (list all steps), `POST /api/v1/projects/{id}/pipeline/run/{step_type}` (run a specific step), `PATCH /api/v1/projects/{id}/pipeline/{step_id}` (update step, e.g., set selected_option).

#### Scenario: Get pipeline returns all steps
- **WHEN** `GET /api/v1/projects/{id}/pipeline` is called
- **THEN** a list of 10 pipeline step responses is returned with correct step_type, step_order, and status

#### Scenario: Run ICP step via API
- **WHEN** `POST /api/v1/projects/{id}/pipeline/run/icp` is called
- **THEN** the response status is 200 with the completed step data including output_data

#### Scenario: Update step with selected option
- **WHEN** `PATCH /api/v1/projects/{id}/pipeline/{step_id}` is called with `selected_option` in the body
- **THEN** the step's `selected_option` is updated and downstream steps are invalidated if step was already completed
