## Purpose

Defines the dashboard page, project list, create-project dialog, and project navigation.

## ADDED Requirements

### Requirement: Typed API client
The system SHALL provide `api.ts` with `api.get<T>(path)`, `api.post<T>(path, body)`, `api.patch<T>(path, body)`, `api.delete(path)` methods wrapping `fetch`. Base URL SHALL come from `NEXT_PUBLIC_API_URL` environment variable defaulting to `http://localhost:8000`. All methods SHALL parse JSON responses and throw on non-2xx status codes.

#### Scenario: API client calls backend
- **WHEN** `api.get('/api/v1/projects')` is called with the backend running
- **THEN** a typed array of `ProjectSummary` objects is returned

#### Scenario: API client handles errors
- **WHEN** `api.get('/api/v1/projects/nonexistent')` is called
- **THEN** an error is thrown with the response status code

### Requirement: TypeScript interfaces matching backend schemas
The system SHALL define TypeScript interfaces in `src/types/` matching backend response schemas: `Project`, `ProjectSummary` (matching `ProjectSummaryResponse`), `ProjectDetail` (matching `ProjectDetailResponse`), `TargetFormat`, `ContentGoal`, `ProjectCreateInput` (matching `ProjectCreateRequest`).

#### Scenario: Types match backend responses
- **WHEN** a project is fetched from the backend
- **THEN** the response data can be assigned to a `ProjectSummary` typed variable without type errors

### Requirement: Dashboard page shows project list
The system SHALL replace the default Next.js home page with a Dashboard that fetches `GET /api/v1/projects` and renders project cards. Each card SHALL show: project name, `target_format` as a badge, `status` as a badge, and `updated_at` formatted as relative time. A "New Project" button SHALL open the create dialog. When no projects exist, an empty state with a "Create your first project" CTA SHALL be shown.

#### Scenario: Dashboard displays projects
- **WHEN** the dashboard loads and projects exist in the backend
- **THEN** project cards are rendered showing name, format badge, status badge, and relative time

#### Scenario: Dashboard shows empty state
- **WHEN** the dashboard loads and no projects exist
- **THEN** an empty state message with "Create your first project" button is shown

#### Scenario: Click project card navigates to detail
- **WHEN** a project card is clicked
- **THEN** the browser navigates to `/projects/{id}`

### Requirement: Create-project dialog
The system SHALL provide a create-project dialog with a form containing: name (text, required, max 100), topic (text, required, max 200), target_format (select: VSL, YouTube, Tutorial, Facebook, LinkedIn, Blog, required), content_goal (select: Sell, Educate, Entertain, Build Authority, optional), raw_notes (textarea, required, max 10000). Form SHALL be validated with Zod matching backend `ProjectCreateRequest`. On submit, `POST /api/v1/projects` is called and the project list is refreshed.

#### Scenario: Create project successfully
- **WHEN** the form is filled with valid data and submitted
- **THEN** `POST /api/v1/projects` is called, the dialog closes, and the new project appears in the dashboard list

#### Scenario: Validation error on empty name
- **WHEN** the form is submitted with an empty name
- **THEN** a validation error is shown on the name field

### Requirement: Zustand project store
The system SHALL provide `project-store.ts` with Zustand managing `activeProjectId` state for sidebar highlighting. Project data fetching is handled by TanStack Query, not Zustand.

#### Scenario: Store initializes with null active project
- **WHEN** the app loads
- **THEN** `activeProjectId` is `null`
