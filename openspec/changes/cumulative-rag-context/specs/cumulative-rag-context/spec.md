## Purpose

Defines cumulative RAG context for the Scripts Writer pipeline - where each step progressively includes more documents than the previous step. Step 1 (ICP) uses only ICP documents + notes, Step 2 (Hook) uses ICP + Hook documents + notes, Step 3+ (Narrative/Retention/CTA) use cumulative documents from dependencies plus developer-provided hardcoded templates.

## ADDED Requirements

### Requirement: STEP_DEPENDENCIES configuration
The system SHALL provide `STEP_DEPENDENCIES` in `rag/config.py` that maps each pipeline step to its document dependencies:

- `ICP → [ICP]` - ICP step queries only ICP category
- `HOOK → [ICP, HOOK]` - Hook step queries ICP + Hook categories
- `NARRATIVE → [ICP, HOOK]` - Narrative step queries ICP + Hook categories
- `RETENTION → [ICP, HOOK]` - Retention step queries ICP + Hook categories
- `CTA → [ICP, HOOK]` - CTA step queries ICP + Hook categories
- `WRITER → [ICP, HOOK, NARRATIVE, RETENTION, CTA]` - Writer step queries all categories

#### Scenario: ICP step gets ICP context only
- **WHEN** `get_step_context(project_id, StepType.ICP)` is called
- **THEN** only `documents/icp` is queried

#### Scenario: Hook step gets cumulative ICP + Hook context
- **WHEN** `get_step_context(project_id, StepType.HOOK)` is called
- **THEN** both `documents/icp` AND `documents/hooks` are queried, results combined

#### Scenario: Narrative step gets dev-provided narrative patterns
- **WHEN** `get_step_context(project_id, StepType.NARRATIVE)` is called
- **THEN** documents from `icp`, `hooks`, AND `narrative_patterns` are queried and combined

### Requirement: DEV_PROVIDED_CATEGORIES configuration
The system SHALL provide `DEV_PROVIDED_CATEGORIES` in `rag/config.py` that maps certain steps to hardcoded template categories:

- `NARRATIVE → ["narrative_patterns"]` - Templates: AIDA, HERO'S Journey, PAS
- `RETENTION → ["retention_tactics"]` - Templates: Curiosity Gap, Teasers

#### Scenario: Narrative step includes AIDA template
- **WHEN** `get_step_context(project_id, StepType.NARRATIVE)` is called
- **THEN** `documents/narrative_patterns/aida.txt` is queried and included in context

### Requirement: Cumulative get_step_context()
The system SHALL update `PiragiService.get_step_context()` to iterate over `STEP_DEPENDENCIES`, querying each dependency category and combining results into a single context string.

#### Scenario: Cumulative context returned for Hook step
- **WHEN** `get_step_context(project_id, StepType.HOOK)` is called with documents in both ICP and Hook categories
- **THEN** chunks from both categories are combined with `"\n\n"` separator

#### Scenario: Empty result when no documents
- **WHEN** `get_step_context(project_id, StepType.HOOK)` is called but no documents uploaded
- **THEN** `None` is returned (no error, no context)

### Requirement: Dev-provided template documents
The system SHALL provide editable .txt template files in `documents/narrative_patterns/` and `documents/retention_tactics/`:

- `documents/narrative_patterns/aida.txt` - AIDA narrative pattern
- `documents/narrative_patterns/heroes_journey.txt` - HERO's Journey narrative pattern
- `documents/narrative_patterns/pas.txt` - PAS narrative pattern
- `documents/retention_tactics/curiosity_gap.txt` - Curiosity Gap retention tactic
- `documents/retention_tactics/teasers.txt` - Teasers retention tactic

#### Scenario: Templates available to RAG
- **WHEN** `PiragiManager.query("narrative_patterns", "AIDA", top_k=3)` is called
- **THEN** content from `aida.txt` is returned as a chunk

### Requirement: Frontend step-based document upload
The system SHALL display document upload dropzone only on the pending step panel (ICP and Hook steps). Narrative/Retention/CTA panels SHALL display agent-generated results first, then fixed template selection options instead of dropzones.

#### Scenario: Dropzone shown for pending ICP step
- **WHEN** the current pending step is ICP
- **THEN** a document dropzone is shown in the ICP panel

#### Scenario: Dropzone hidden for pending Narrative step
- **WHEN** the current pending step is Narrative
- **THEN** agent results are shown first, then template selection options (AIDA, PAS) below

### Requirement: Agent results display
The system SHALL display agent-generated results in each panel before template selection options.

#### Scenario: Agent results shown for Narrative step
- **WHEN** Narrative step has completed with results
- **THEN** generated patterns are displayed in an "Agent Results" card with confidence scores

#### Scenario: Agent results shown for Retention step
- **WHEN** Retention step has completed with results
- **THEN** generated techniques are displayed in an "Agent Results" card

### Requirement: Template selection with explanations
Each template option SHALL include a "why_best" explanation describing when to use it.

#### Scenario: User selects AIDA template
- **WHEN** user selects "AIDA" in Narrative panel
- **THEN** the template is used for generation with explanation "Best for awareness stages"

#### Scenario: Template option shows why_best
- **WHEN** user views Narrative template options
- **THEN** AIDA shows "Best for awareness stages where you need to grab attention"
- **AND** PAS shows "Best for prospects who already know they have a problem"