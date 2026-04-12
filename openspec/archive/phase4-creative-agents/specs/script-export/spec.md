## Purpose

Defines the script versioning schemas, export service, and export API for the Scripts Writer backend.

## ADDED Requirements

### Requirement: Script version schemas
The system SHALL define `ScriptVersionResponse` (id, project_id, version_number, content, format, hook_text, narrative_pattern, cta_text, created_at) and `ScriptUpdateRequest` (content: str). Schemas SHALL match the LLD `script_versions` table.

#### Scenario: Script version response validates
- **WHEN** a `ScriptVersionResponse` is constructed with valid fields
- **THEN** it validates without error

### Requirement: Export service generates files
The system SHALL provide `ExportService(db, export_dir)` with `export_txt(project_id, version_id) -> Path` and `export_md(project_id, version_id) -> Path`. Markdown export SHALL include a metadata header (project name, format, topic, hook, narrative, CTA) before the script content. Text export SHALL contain raw script content only. Files SHALL be saved to the configured `export_dir`.

#### Scenario: Export markdown with metadata header
- **WHEN** `export_md(project_id, version_id)` is called
- **THEN** a .md file is created starting with `# {project_name}`, followed by format, topic, hook, narrative, CTA metadata, then a separator, then the script content

#### Scenario: Export plain text
- **WHEN** `export_txt(project_id, version_id)` is called
- **THEN** a .txt file is created with raw script content only

### Requirement: Export API endpoint
The system SHALL expose `GET /api/v1/projects/{id}/export?format=txt|md` that returns the latest script version as a file download. If no script version exists, return 404.

#### Scenario: Export with no script version
- **WHEN** `GET /api/v1/projects/{id}/export?format=md` is called and no script version exists
- **THEN** a 404 response is returned

#### Scenario: Export downloads file
- **WHEN** `GET /api/v1/projects/{id}/export?format=md` is called and a script version exists
- **THEN** a file download response is returned with `Content-Disposition: attachment; filename="{slug}-v{version}.md"`
