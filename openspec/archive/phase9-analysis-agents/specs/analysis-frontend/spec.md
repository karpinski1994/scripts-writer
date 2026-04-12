## Purpose

Defines the frontend analysis panel, TypeScript types, and integration with the pipeline view.

## ADDED Requirements

### Requirement: Analysis TypeScript types
The system SHALL define `frontend/src/types/analysis.ts` with: `Finding` (type, severity, text, suggestion, confidence), `AnalysisResult` (id, project_id, script_version_id, agent_type, findings: Finding[], overall_score: number | null, created_at), `AgentType` union type.

#### Scenario: Types match backend responses
- **WHEN** analysis results are fetched from `GET /analysis`
- **THEN** the response data can be assigned to `AnalysisResult[]` without type errors

### Requirement: Analysis panel with tabbed interface
The system SHALL provide `analysis-panel.tsx` with 4 tabs: Fact Check, Readability, Copyright, Policy. Each tab shows a list of finding cards. Each card displays: severity badge (color-coded: high=red, medium=yellow, low=green), quoted text, confidence level, suggestion text, "Dismiss" button, and "Apply Suggestion" button (for findings with suggestions). The Readability tab additionally shows overall score gauges (Flesch-Kincaid, Gunning Fog) at the top. An "Analyze All" button at the top runs all 4 agents. Running analysis shows a loading spinner per tab.

#### Scenario: View fact check findings
- **WHEN** the Fact Check tab is active and findings exist
- **THEN** finding cards show severity badge, quoted claim, confidence, and suggestion

#### Scenario: Analyze All button runs all agents
- **WHEN** "Analyze All" is clicked
- **THEN** `POST /analyze/all` is called, all tabs show loading, then populate with results

#### Scenario: Dismiss a finding
- **WHEN** "Dismiss" is clicked on a finding card
- **THEN** the card is visually struck through or hidden (local UI state only, not persisted)

#### Scenario: Apply a suggestion
- **WHEN** "Apply Suggestion" is clicked on a finding with a suggestion
- **THEN** a toast confirms "Suggestion copied — paste in script editor to apply"

### Requirement: Analysis steps clickable in pipeline view after Writer completes
When the Writer step is completed, the 4 analysis step cards in the pipeline view's Analysis row SHALL become clickable (instead of locked). Clicking an analysis step SHALL show the analysis panel with that tab active.

#### Scenario: Analysis steps unlocked after Writer
- **WHEN** the Writer step is completed
- **THEN** the FactCheck, Readability, Copyright, and Policy step cards are clickable

#### Scenario: Analysis steps locked before Writer
- **WHEN** the Writer step is not completed
- **THEN** analysis step cards are grayed out with tooltip "Requires: Writer"

### Requirement: Agent panel wrapper handles analysis steps
The `agent-panel-wrapper.tsx` SHALL render the analysis panel when an analysis step type (factcheck, readability, copyright, policy) is the active step. The panel SHALL show the analysis results if they exist, or a "Run Analysis" button if not.

#### Scenario: View analysis results for active step
- **WHEN** the active step is "factcheck" and results exist
- **THEN** the analysis panel is shown with the Fact Check tab active

#### Scenario: Run individual analysis
- **WHEN** the active step is "readability" and no results exist
- **THEN** a "Run Readability Analysis" button is shown, clicking it calls `POST /analyze/readability`
