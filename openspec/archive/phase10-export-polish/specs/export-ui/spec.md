## Purpose

Defines the export panel UI, re-run confirmation, branch project, and ICP upload features.

## ADDED Requirements

### Requirement: Export panel component
The system SHALL provide an export panel accessible from the pipeline view when a script version exists. It SHALL show: format selector (txt, md), "Download" button that calls `GET /projects/{id}/export?format={fmt}` and triggers browser download, "Copy to Clipboard" button that copies the latest script version content to the clipboard and shows a success toast.

#### Scenario: Download as markdown
- **WHEN** "Download" is clicked with format "md"
- **THEN** a .md file is downloaded from the backend export endpoint

#### Scenario: Copy to clipboard
- **WHEN** "Copy to Clipboard" is clicked
- **THEN** the script content is copied to the clipboard and a toast says "Copied to clipboard"

### Requirement: Re-run confirmation dialog
When the user clicks "Re-run" on a completed pipeline step, a dialog SHALL appear showing: "Re-running {step name} will reset the following steps: {list of downstream step names}. This cannot be undone." With "Cancel" and "Re-run" buttons. Only "Re-run" triggers the API call.

#### Scenario: Re-run ICP shows all downstream
- **WHEN** "Re-run" is clicked on ICP (completed)
- **THEN** the dialog shows "Re-running ICP will reset: Hook, Narrative, Retention, CTA, Writer, FactCheck, Readability, Copyright, Policy"

#### Scenario: Cancel closes dialog
- **WHEN** "Cancel" is clicked
- **THEN** the dialog closes and no action is taken

### Requirement: Branch project
The system SHALL provide a "Branch" button on the pipeline view. Clicking it opens a dialog with an input for the new project name and a dropdown to select which step to branch from. On confirm, `POST /api/v1/projects/{id}/branch` is called with `{branch_from_step: "narrative", name: "New Project Name"}`. The new project appears in the dashboard with all steps up to and including the selected step completed.

#### Scenario: Branch from Narrative step
- **WHEN** the user branches from Narrative with name "V2 - Different Hook"
- **THEN** a new project is created with ICP+Hook+Narrative steps completed (with same output_data and selected_option), and remaining steps pending

#### Scenario: Branch project appears in dashboard
- **WHEN** branching succeeds
- **THEN** the dashboard shows the new project and a toast says "Branch created"

### Requirement: Branch project backend endpoint
The system SHALL expose `POST /api/v1/projects/{id}/branch` that accepts `{branch_from_step: str, name: str}`. It creates a new project with the same metadata (topic, format, goal, raw_notes), copies all pipeline steps up to and including `branch_from_step` with their output_data and selected_option, and creates pending steps for all remaining steps.

#### Scenario: Branch creates project with copied steps
- **WHEN** `POST /projects/{id}/branch` with `{branch_from_step: "hook", name: "Alt Hook"}`
- **THEN** a new project is created with ICP and Hook steps completed (same data), and Narrative+ steps pending

### Requirement: ICP file upload UI
The ICP panel SHALL show an "Upload ICP" button that opens a file picker accepting .json and .txt files. On file select, the content is parsed and submitted via `POST /api/v1/projects/{id}/icp/upload`.

#### Scenario: Upload .json ICP file
- **WHEN** a .json file with ICP data is uploaded
- **THEN** the ICP profile is created/updated with source="uploaded" and the ICP panel shows the data

#### Scenario: Upload .txt file
- **WHEN** a .txt file with raw notes is uploaded
- **THEN** the content is stored as raw notes and the user is prompted to run the ICP agent
