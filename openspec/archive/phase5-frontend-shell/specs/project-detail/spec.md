## Purpose

Defines the project detail page showing project metadata, raw notes, and navigation.

## ADDED Requirements

### Requirement: Project detail page
The system SHALL provide a page at `/projects/[id]` that fetches `GET /api/v1/projects/{id}` and displays: project name (heading), topic, target_format badge, content_goal badge (if set), status badge, raw_notes in a readable format, and created_at/updated_at timestamps. A back button or breadcrumb SHALL navigate to the dashboard. If the project is not found, a 404 message SHALL be shown.

#### Scenario: View project detail
- **WHEN** navigating to `/projects/{id}` and the project exists
- **THEN** the project name, topic, format, goal, status, and raw notes are displayed

#### Scenario: Project not found
- **WHEN** navigating to `/projects/{id}` and the project does not exist
- **THEN** a "Project not found" message is displayed

#### Scenario: Navigate back to dashboard
- **WHEN** the back button is clicked on the project detail page
- **THEN** the browser navigates to `/` (dashboard)
