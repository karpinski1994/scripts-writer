## Purpose

Defines structured logging configuration for the backend using structlog.

## ADDED Requirements

### Requirement: Structlog JSON logging configuration
The system SHALL configure `structlog` at application startup in `app/main.py` with: JSON output to stdout, console renderer in development (pretty format), file handler writing to `./logs/app.log` with rotation (10MB max, 5 backups). All log entries SHALL include: timestamp, level, logger name, event message, and any extra context.

#### Scenario: Log entry is valid JSON
- **WHEN** a log entry is written
- **THEN** it is a valid JSON object with timestamp, level, event, and context fields

#### Scenario: Agent execution logged
- **WHEN** an agent completes execution
- **THEN** a log entry includes: agent_name, step_type, project_id, duration_ms, provider, status (completed/failed)

### Requirement: Structlog dependency
The system SHALL add `structlog` to backend dependencies.

#### Scenario: structlog imports correctly
- **WHEN** `import structlog` is called
- **THEN** no import error occurs
