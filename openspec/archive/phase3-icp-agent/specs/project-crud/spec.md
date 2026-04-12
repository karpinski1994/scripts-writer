## Purpose

Updates to the existing project-crud capability to support auto-creation of pipeline steps and inclusion of pipeline/ICP routers.

## MODIFIED Requirements

### Requirement: Aggregated API router
The system SHALL provide an aggregated router that mounts all API sub-routers under the `/api/v1` prefix, including the project router, settings router, pipeline router, and ICP router.

#### Scenario: Pipeline endpoints accessible via aggregated router
- **WHEN** the aggregated router is mounted in the FastAPI app
- **THEN** pipeline endpoints are accessible at `/api/v1/projects/{id}/pipeline`

#### Scenario: ICP endpoints accessible via aggregated router
- **WHEN** the aggregated router is mounted in the FastAPI app
- **THEN** ICP endpoints are accessible at `/api/v1/projects/{id}/icp`

### Requirement: ProjectService auto-creates pipeline steps
The system SHALL create 10 `pipeline_steps` rows when a new project is created, with step_types `icp`, `hook`, `narrative`, `retention`, `cta`, `writer`, `factcheck`, `readability`, `copyright`, `policy`, all with `status=pending` and sequential `step_order` from 0 to 9.

#### Scenario: Project creation creates 10 pipeline steps
- **WHEN** a new project is created via `ProjectService.create()`
- **THEN** 10 `pipeline_steps` rows are created for that project, each with the correct step_type, step_order, and status=pending
