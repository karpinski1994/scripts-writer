## ADDED Requirements

### Requirement: Draft as primary source in creative agents
All creative agents (Hook, Narrative, Retention, CTA, Writer) SHALL treat the `draft` field as the PRIMARY source of truth for content generation. ICP, selected hook, narrative pattern, and other pipeline selections are auxiliary context that shapes HOW the content is structured, not WHAT it is about.

#### Scenario: Agent receives draft content
- **WHEN** a creative agent is invoked and `project.draft` is not empty
- **THEN** the draft SHALL be positioned FIRST in the prompt with a `=== PRIMARY SOURCE (Draft/Content) ===` emphasis label
- **AND** auxiliary data (ICP, hook, etc.) SHALL be labeled as `(auxiliary)` in the prompt

#### Scenario: Agent receives no draft content
- **WHEN** a creative agent is invoked and `project.draft` is empty or None
- **THEN** the agent SHALL proceed with other available inputs (ICP, topic, format) without error
- **AND** no PRIMARY SOURCE section SHALL appear in the prompt

### Requirement: Draft field in agent input schemas
NarrativeAgentInput, RetentionAgentInput, CTAAgentInput, and WriterAgentInput SHALL include an optional `draft: str | None = None` field.

#### Scenario: Draft passed to narrative agent
- **WHEN** the orchestrator builds NarrativeAgentInput
- **THEN** it SHALL include `draft=project.draft`

#### Scenario: Draft passed to retention agent
- **WHEN** the orchestrator builds RetentionAgentInput
- **THEN** it SHALL include `draft=project.draft`

#### Scenario: Draft passed to CTA agent
- **WHEN** the orchestrator builds CTAAgentInput
- **THEN** it SHALL include `draft=project.draft`

#### Scenario: Draft passed to writer agent
- **WHEN** the orchestrator builds WriterAgentInput
- **THEN** it SHALL include `draft=project.draft` alongside the existing `raw_notes` field

### Requirement: Global playbook paths resolve correctly
The orchestrator SHALL read playbook reference files from the correct filesystem paths, and SHALL read ALL files in each playbook directory (not just the first).

#### Scenario: Narrative playbook files loaded
- **WHEN** the orchestrator builds narrative agent input
- **THEN** it SHALL read all `.txt`, `.md`, `.json` files from `documents/playbooks/narrative_patterns/`

#### Scenario: Retention playbook files loaded
- **WHEN** the orchestrator builds retention agent input
- **THEN** it SHALL read all `.txt`, `.md`, `.json` files from `documents/playbooks/retention_tactics/`

### Requirement: System prompts establish draft priority
Each creative agent's SYSTEM_PROMPT SHALL explicitly state that draft/content is the PRIMARY source of truth and all other data is auxiliary.

#### Scenario: Hook agent system prompt
- **WHEN** the HookAgent system prompt is read
- **THEN** it SHALL contain the phrase "PRIMARY source of truth" referring to draft/content
- **AND** it SHALL state that other data is "auxiliary context"
