## Why

The `draft` field (user's refined content from the Subject step) is the most important source of truth for all creative agents, yet it is only passed to the HookAgent — and even there it's treated as auxiliary. All other creative agents (Narrative, Retention, CTA, Writer) receive no draft at all, relying solely on ICP, hook, and other selections as their primary inputs. This results in generic outputs that ignore the actual content the user wrote. Additionally, global document reference paths for narrative and retention agents point to a non-existent `documents/playbooks/` directory, so reference materials are never loaded.

## What Changes

- Add `draft` field to `NarrativeAgentInput`, `RetentionAgentInput`, `CTAAgentInput`, and `WriterAgentInput` schemas
- Rewrite SYSTEM_PROMPT in Hook, Narrative, Retention, CTA, and Writer agents to establish draft as PRIMARY source of truth and all other data as auxiliary
- Restructure `build_prompt()` in all 5 creative agents to position draft FIRST with emphasis labels (`=== PRIMARY SOURCE ===`)
- Pass `project.draft` from orchestrator to Narrative, Retention, CTA, and Writer agents
- Move `documents/narrative_patterns/` to `documents/playbooks/narrative_patterns/` and `documents/retention_tactics/` to `documents/playbooks/retention_tactics/` so orchestrator's `playbooks_base` path resolves correctly
- Update orchestrator to read ALL files from global playbooks directories (not just first file)

## Capabilities

### New Capabilities
- `draft-primary-source`: Treats the draft/content as the primary input for all creative agents (Hook, Narrative, Retention, CTA, Writer), with ICP and other selections as auxiliary shaping context

### Modified Capabilities
- None

## Impact

- **Backend schemas**: `backend/app/schemas/agents.py` — 4 input models gain `draft` field
- **Backend agents**: 5 agent files — SYSTEM_PROMPT and `build_prompt()` restructured
- **Backend orchestrator**: `backend/app/pipeline/orchestrator.py` — passes `draft` to 4 more agents, fixes playbook paths, reads all playbook files
- **Filesystem**: Move `documents/narrative_patterns/` → `documents/playbooks/narrative_patterns/`, `documents/retention_tactics/` → `documents/playbooks/retention_tactics/`
- **Tests**: `backend/tests/unit/test_agents.py` — optional draft-specific test
