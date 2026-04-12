## Purpose

Defines the frontend types, Zustand store, NotebookLM context sections in agent panels, and project connection UI.

## ADDED Requirements

### Requirement: NotebookLM TypeScript types
The system SHALL define `frontend/src/types/notebooklm.ts` with: `NotebookSummary` (id, title), `ConnectNotebookRequest` (notebook_id), `ConnectNotebookResponse` (project_id, notebook_id, notebook_title, connected), `NotebookQueryRequest` (query), `NotebookQueryResponse` (answer), `ConnectedNotebook` (id, title).

#### Scenario: Types match backend responses
- **WHEN** a NotebookLM API response is parsed
- **THEN** it can be assigned to the corresponding TypeScript interface without errors

### Requirement: NotebookLM Zustand store
The system SHALL provide `frontend/src/stores/notebooklm-store.ts` with: `connectedNotebook: { id: string; title: string } | null`, `stepContexts: Record<string, string>`, `isQuerying: boolean`, `setConnectedNotebook(notebook)`, `setStepContext(stepType, context)`, `clearStepContext(stepType)`, `setIsQuerying(querying)`, `reset()`.

#### Scenario: Store initializes with null notebook
- **WHEN** the store is created
- **THEN** `connectedNotebook` is `null`, `stepContexts` is `{}`, `isQuerying` is `false`

#### Scenario: Set step context
- **WHEN** `setStepContext("hook", "Use curiosity gap...")` is called
- **THEN** `stepContexts["hook"]` is `"Use curiosity gap..."`

### Requirement: NotebookLM context section in agent panels
Each creative agent panel (ICP, Hook, Narrative, Retention, CTA) SHALL have a collapsible "NotebookLM Context" section that: shows the connected notebook name (or "No notebook connected" with link to project settings), has a "Query for {step} insights" button that calls `POST /notebooklm/query`, displays the returned context text in a preview area, and has an "Include in generation" checkbox (default: checked). When querying, a loading indicator SHALL be shown.

#### Scenario: Query insights for ICP step
- **WHEN** the user clicks "Query for ICP insights" in the ICP panel
- **THEN** `POST /notebooklm/query` is called with a step-appropriate query, the result is displayed, and `stepContexts["icp"]` is set in the store

#### Scenario: Include context checkbox unchecked
- **WHEN** the "Include in generation" checkbox is unchecked
- **THEN** the agent runs without NotebookLM context even if a notebook is connected

#### Scenario: No notebook connected
- **WHEN** no notebook is connected to the project
- **THEN** the section shows "No notebook connected" with a link to connect one, and the query button is disabled

### Requirement: NotebookLM connection UI in project page
The project detail page SHALL show a NotebookLM connection indicator: notebook name if connected, or "Connect NotebookLM" button if not. Clicking the button SHALL open a dialog listing the user's notebooks (from `GET /notebooklm/notebooks`) with a "Connect" button per notebook. A "Disconnect" option SHALL be available when connected.

#### Scenario: Connect notebook via dialog
- **WHEN** the user clicks "Connect NotebookLM" and selects a notebook
- **THEN** `POST /notebooklm/connect` is called, the dialog closes, and the notebook name is shown

#### Scenario: Disconnect notebook
- **WHEN** the user clicks "Disconnect" on a connected notebook
- **THEN** `DELETE /notebooklm/connect` is called and the notebook indicator shows "Connect NotebookLM"
