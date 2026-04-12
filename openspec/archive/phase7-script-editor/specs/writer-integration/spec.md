## Purpose

Defines the Writer agent panel integration into the pipeline view, the "Generate Script" flow, streaming output handling, and navigation to the dedicated editor.

## ADDED Requirements

### Requirement: Writer panel in pipeline view
The system SHALL provide `writer-panel.tsx` that renders when `activeStepType === "writer"` in the `AgentPanelWrapper`. When the writer step is pending with met dependencies, the panel SHALL show a "Generate Script" button that calls `POST /api/v1/projects/{project_id}/pipeline/run/writer`. When the writer step is running, the panel SHALL show a loading spinner with "Generating script..." text. When the writer step is completed, the panel SHALL show a preview of the generated script (first 500 characters of `ScriptDraft.content`) and two action buttons: "Open in Editor" (navigates to `/projects/{project_id}/editor`) and "Regenerate" (re-runs the writer agent).

#### Scenario: Generate script from pipeline
- **WHEN** the writer step is pending and all dependencies are completed
- **THEN** a "Generate Script" button is shown

#### Scenario: Click generate script
- **WHEN** the "Generate Script" button is clicked
- **THEN** `POST /api/v1/projects/{project_id}/pipeline/run/writer` is called, and the panel shows a loading state

#### Scenario: Writer agent completes
- **WHEN** the writer agent completes successfully
- **THEN** a script preview is shown with "Open in Editor" and "Regenerate" buttons

#### Scenario: Open in editor
- **WHEN** "Open in Editor" is clicked
- **THEN** the user is navigated to `/projects/{project_id}/editor`

#### Scenario: Regenerate script
- **WHEN** "Regenerate" is clicked
- **THEN** `POST /api/v1/projects/{project_id}/pipeline/run/writer` is called again

### Requirement: Writer panel in AgentPanelWrapper
The system SHALL update `agent-panel-wrapper.tsx` to handle the `writer` step type in its switch statement. When `activeStepType === "writer"`, it SHALL render `WriterPanel` with `projectId`, the writer step data, and callback functions for running the agent and navigating to the editor.

#### Scenario: Writer step shows Writer panel
- **WHEN** `activeStepType` is `"writer"` and the writer step is completed
- **THEN** the `WriterPanel` component is rendered with the script preview and action buttons

### Requirement: Script generation creates a script version
The system SHALL ensure that running the writer agent via `POST /pipeline/run/writer` also creates a `ScriptVersion` record (the existing `POST /scripts/generate` endpoint already does this). After the writer agent completes, the pipeline query SHALL be invalidated and the script versions query SHALL be invalidated so the editor page and version dropdown reflect the new version.

#### Scenario: Writer generates script version
- **WHEN** the writer agent completes successfully
- **THEN** a new `ScriptVersion` is created and available via `GET /scripts`

### Requirement: Writer panel uses streaming output from pipeline store
When the writer step is running, the Writer panel SHALL display streaming output from `pipeline-store.streamingOutput["writer"]` using the existing `StreamingText` component, if available. When the step completes, the full output SHALL replace the streaming text.

#### Scenario: Streaming during writer execution
- **WHEN** the writer agent is running and `streamingOutput["writer"]` is non-empty
- **THEN** the streaming text is displayed in the Writer panel

#### Scenario: Full output after completion
- **WHEN** the writer step transitions from running to completed
- **THEN** the streaming text is replaced with the script preview
