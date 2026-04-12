## Purpose

Updates to the existing project-crud capability to include the settings API router in the aggregated API router.

## MODIFIED Requirements

### Requirement: Aggregated API router
The system SHALL provide an aggregated router that mounts all API sub-routers under the `/api/v1` prefix, including the project router and the settings router.

#### Scenario: All project endpoints accessible via aggregated router
- **WHEN** the aggregated router is mounted in the FastAPI app
- **THEN** all project endpoints are accessible at `/api/v1/projects`

#### Scenario: Settings endpoints accessible via aggregated router
- **WHEN** the aggregated router is mounted in the FastAPI app
- **THEN** all settings endpoints are accessible at `/api/v1/settings/llm`
