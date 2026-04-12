## Purpose

Defines the pipeline view component, step sidebar, project detail page replacement, and pipeline Zustand store.

## ADDED Requirements

### Requirement: Pipeline Zustand store
The system SHALL provide `pipeline-store.ts` with: `activeStepType: string | null`, `steps: PipelineStep[]`, `streamingOutput: Record<string, string>`, `isRunning: boolean`, `setActiveStep(stepType)`, `setSteps(steps)`, `setStepOutput(stepType, output)`, `appendStreamingToken(stepType, token)`, `clearStreaming(stepType)`, `setIsRunning(running)`, `reset()`.

#### Scenario: Store initializes with null active step
- **WHEN** the store is created
- **THEN** `activeStepType` is `null`, `steps` is `[]`, `streamingOutput` is `{}`, `isRunning` is `false`

#### Scenario: Set active step
- **WHEN** `setActiveStep("hook")` is called
- **THEN** `activeStepType` is `"hook"`

### Requirement: Pipeline view component
The system SHALL provide `pipeline-view.tsx` that renders all 10 pipeline steps as horizontal cards. Each card SHALL show: step type name, status indicator (✓ completed, ● running with spinner, ○ pending, ✗ failed), and a brief label. Steps SHALL be grouped into two rows: Creative (ICP→Hook→Narrative→Retention→CTA→Writer) and Analysis (FactCheck→Readability→Copyright→Policy). Clicking a step card SHALL set it as the active step in the pipeline store.

#### Scenario: Pipeline view renders step statuses
- **WHEN** the pipeline view renders with step data
- **THEN** completed steps show ✓, running steps show ● with spinner, pending steps show ○, failed steps show ✗

#### Scenario: Click step card to activate
- **WHEN** a step card is clicked
- **THEN** `setActiveStep(step_type)` is called and the agent panel for that step is shown

### Requirement: Step sidebar component
The system SHALL provide `step-sidebar.tsx` that renders a vertical list of steps with status icons. The current active step SHALL be highlighted. Completed steps SHALL be clickable for re-navigation. Pending steps with unmet dependencies SHALL be grayed out with a tooltip explaining the dependency. Running steps SHALL show a spinner.

#### Scenario: Active step highlighted
- **WHEN** `activeStepType` is "hook"
- **THEN** the Hook step in the sidebar is visually highlighted

#### Scenario: Locked step shows tooltip
- **WHEN** a pending step has unmet dependencies (e.g., Narrative before Hook is completed)
- **THEN** the step is grayed out and hovering shows a tooltip like "Requires: ICP, Hook"

### Requirement: Project detail page replaced with pipeline view
The system SHALL replace the existing project detail page at `/projects/[id]` with a pipeline-centric view that fetches `GET /api/v1/projects/{id}/pipeline` and renders: step-sidebar on the left, pipeline-view at the top, and the active step's agent panel in the main content area.

#### Scenario: Project detail shows pipeline
- **WHEN** navigating to `/projects/{id}`
- **THEN** the pipeline view, step sidebar, and active agent panel are rendered

#### Scenario: No active step shows prompt
- **WHEN** `activeStepType` is null and ICP is pending
- **THEN** a "Run ICP Agent to get started" prompt is shown
