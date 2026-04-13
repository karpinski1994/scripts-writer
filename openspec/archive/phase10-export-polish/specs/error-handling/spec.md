## Purpose

Defines error handling UI, loading states, and empty states for a polished user experience.

## ADDED Requirements

### Requirement: Toast notifications for API errors
The system SHALL show a toast notification (using sonner) when any API call fails. The toast SHALL show: error title ("Error"), brief message from the API response or "Something went wrong", and auto-dismiss after 5 seconds. The `api.ts` client SHALL call `toast.error()` on non-2xx responses.

#### Scenario: Agent execution failure shows toast
- **WHEN** an agent execution API call fails
- **THEN** a toast appears with "Error: Failed to run agent" and the error detail

#### Scenario: Network error shows toast
- **WHEN** the backend is unreachable
- **THEN** a toast appears with "Error: Unable to connect to server"

### Requirement: Error boundary component
The system SHALL provide an `ErrorBoundary` React component wrapping the pipeline area. On render errors, it SHALL show a fallback UI: "Something went wrong" message with a "Reload" button that resets the component state.

#### Scenario: Render error shows fallback
- **WHEN** a React component throws during rendering
- **THEN** the error boundary shows "Something went wrong" with a "Reload" button instead of a blank page

### Requirement: Loading skeletons for project list
The dashboard project list SHALL show skeleton cards (animated placeholder rectangles) while projects are being fetched, instead of a blank screen or spinner.

#### Scenario: Dashboard shows skeletons while loading
- **WHEN** the dashboard is fetching projects
- **THEN** skeleton cards matching the project card layout are shown

### Requirement: Empty states
The dashboard SHALL show an empty state when no projects exist: centered "Create your first script" heading with a "New Project" CTA button. The pipeline view SHALL show "Run ICP Agent to get started" when all steps are pending and no step is active.

#### Scenario: Empty dashboard
- **WHEN** the dashboard loads and no projects exist
- **THEN** "Create your first script" heading and "New Project" button are shown

#### Scenario: Empty pipeline
- **WHEN** the pipeline view loads with all steps pending
- **THEN** a prompt "Run ICP Agent to get started" is shown in the main content area
