## Purpose

Defines the NotebookLM API client, service, API endpoints, and database changes for connecting Google NotebookLM notebooks to projects.

## ADDED Requirements

### Requirement: NotebookLM API client
The system SHALL provide `app/integrations/notebooklm.py` with a `NotebookLMClient` class that authenticates with Google Cloud using a service account key and calls the Discovery Engine API. Methods: `list_notebooks()` → `list[NotebookSummary]`, `query_notebook(notebook_id, query)` → `str`. The client SHALL use `google-auth` for credentials and `httpx.AsyncClient` for HTTP. Failed API calls SHALL raise `NotebookLMAPIError` with the HTTP status code and message.

#### Scenario: List notebooks successfully
- **WHEN** `list_notebooks()` is called with valid credentials
- **THEN** a list of `NotebookSummary` objects (id, title) is returned from the Discovery Engine API

#### Scenario: Query notebook for insights
- **WHEN** `query_notebook("notebook-123", "What audience insights are relevant for an ICP profile about Python?")` is called
- **THEN** a string with the notebook's synthesized answer is returned

#### Scenario: API error handled gracefully
- **WHEN** the Discovery Engine API returns a 403 or 5xx error
- **THEN** a `NotebookLMAPIError` is raised with the status code and error message

### Requirement: NotebookLM service
The system SHALL provide `app/services/notebooklm_service.py` with `NotebookLMService` that wraps the client with DB session handling. Methods: `list_notebooks(project_id)`, `connect_notebook(project_id, notebook_id)`, `disconnect_notebook(project_id)`, `query_notebook(project_id, query)`, `get_step_context(project_id, step_type)`. `connect_notebook` SHALL persist `notebook_id` on the project's `notebooklm_notebook_id` column. `disconnect_notebook` SHALL set it to `None`. `get_step_context` SHALL generate a step-specific query (e.g., "What audience insights are relevant for an ICP profile about {topic}?" for ICP step) and call `query_notebook`.

#### Scenario: Connect notebook to project
- **WHEN** `connect_notebook("proj-1", "notebook-123")` is called
- **THEN** the project's `notebooklm_notebook_id` is set to `"notebook-123"` and saved to DB

#### Scenario: Disconnect notebook from project
- **WHEN** `disconnect_notebook("proj-1")` is called
- **THEN** the project's `notebooklm_notebook_id` is set to `None` and saved to DB

#### Scenario: Get step context generates appropriate query
- **WHEN** `get_step_context("proj-1", StepType.ICP)` is called with topic "Python course"
- **THEN** the client is called with a query like "What audience insights are relevant for defining an Ideal Customer Profile about Python course?"

#### Scenario: Get step context returns None when no notebook connected
- **WHEN** `get_step_context("proj-1", StepType.HOOK)` is called and no notebook is connected
- **THEN** `None` is returned without making an API call

### Requirement: NotebookLM API endpoints
The system SHALL expose 4 endpoints: `GET /api/v1/projects/{id}/notebooklm/notebooks` (list user's notebooks), `POST /api/v1/projects/{id}/notebooklm/connect` (connect notebook to project), `DELETE /api/v1/projects/{id}/notebooklm/connect` (disconnect), `POST /api/v1/projects/{id}/notebooklm/query` (query connected notebook).

#### Scenario: List notebooks
- **WHEN** `GET /api/v1/projects/{id}/notebooklm/notebooks` is called
- **THEN** a list of `NotebookSummary` objects is returned

#### Scenario: Connect notebook
- **WHEN** `POST /api/v1/projects/{id}/notebooklm/connect` is called with `{"notebook_id": "abc"}`
- **THEN** the notebook is connected and `{"project_id": "...", "notebook_id": "abc", "connected": true}` is returned

#### Scenario: Disconnect notebook
- **WHEN** `DELETE /api/v1/projects/{id}/notebooklm/connect` is called
- **THEN** the notebook is disconnected and 204 is returned

#### Scenario: Query notebook
- **WHEN** `POST /api/v1/projects/{id}/notebooklm/query` is called with `{"query": "audience insights"}`
- **THEN** the query result string is returned

### Requirement: Database migration for NotebookLM
The system SHALL add a `notebooklm_notebook_id` column (VARCHAR(100), nullable) to the `projects` table and update the `icp_profiles.source` CHECK constraint to include `'notebooklm'`.

#### Scenario: Migration applies cleanly
- **WHEN** `alembic upgrade head` is run
- **THEN** the `projects` table has a `notebooklm_notebook_id` column and `icp_profiles.source` accepts `'notebooklm'`

### Requirement: AppSettings includes Google Cloud configuration
The system SHALL add `google_cloud_project: str`, `google_cloud_location: str = "us"`, and `google_application_credentials: str = ""` to `AppSettings` in `app/config.py`.

#### Scenario: Settings loaded from environment
- **WHEN** `GOOGLE_CLOUD_PROJECT=my-project` and `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` are set in `.env`
- **THEN** `AppSettings.google_cloud_project` is `"my-project"` and `google_application_credentials` is the key path
