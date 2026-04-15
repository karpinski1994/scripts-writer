## 1. Filesystem Preparation

- [x] 1.1 Create `documents/playbooks/` directory
- [x] 1.2 Move `documents/narrative_patterns/` to `documents/playbooks/narrative_patterns/`
- [x] 1.3 Move `documents/retention_tactics/` to `documents/playbooks/retention_tactics/`
- [x] 1.4 Move `documents/hooks/` to `documents/playbooks/hooks/`
- [ ] 1.5 Verify no other code references the old paths

## 2. Schema Changes

- [x] 2.1 Add `draft: str | None = None` to `NarrativeAgentInput` in `backend/app/schemas/agents.py`
- [x] 2.2 Add `draft: str | None = None` to `RetentionAgentInput` in `backend/app/schemas/agents.py`
- [x] 2.3 Add `draft: str | None = None` to `CTAAgentInput` in `backend/app/schemas/agents.py`
- [x] 2.4 Add `draft: str | None = None` to `WriterAgentInput` in `backend/app/schemas/agents.py` (alongside existing `raw_notes`)

## 3. Agent Prompt Updates

- [ ] 3.1 Rewrite HookAgent SYSTEM_PROMPT to establish draft as primary source
- [ ] 3.2 Restructure HookAgent `build_prompt()` to position draft first with emphasis label
- [ ] 3.3 Rewrite NarrativeAgent SYSTEM_PROMPT to establish draft as primary source
- [ ] 3.4 Add draft to NarrativeAgent `build_prompt()` as primary with emphasis label
- [ ] 3.5 Rewrite RetentionAgent SYSTEM_PROMPT to establish draft as primary source
- [ ] 3.6 Add draft to RetentionAgent `build_prompt()` as primary with emphasis label
- [ ] 3.7 Rewrite CTAAgent SYSTEM_PROMPT to establish draft as primary source
- [ ] 3.8 Add draft to CTAAgent `build_prompt()` as primary with emphasis label
- [ ] 3.9 Rewrite WriterAgent SYSTEM_PROMPT to establish draft as primary source
- [ ] 3.10 Add draft to WriterAgent `build_prompt()` as primary, demote raw_notes to supplementary

## 4. Orchestrator Updates

- [ ] 4.1 Pass `draft=project.draft` to NarrativeAgentInput in orchestrator
- [ ] 4.2 Pass `draft=project.draft` to RetentionAgentInput in orchestrator
- [ ] 4.3 Pass `draft=project.draft` to CTAAgentInput in orchestrator
- [ ] 4.4 Pass `draft=project.draft` to WriterAgentInput in orchestrator
- [ ] 4.5 Update orchestrator `playbooks_base` path to resolve correctly after folder moves
- [ ] 4.6 Update hook playbook path to use `playbooks_base / "hooks"` instead of hardcoded global path
- [ ] 4.7 Update narrative playbook loading to read ALL files (not just `[:1]`)
- [ ] 4.8 Update retention playbook loading to read ALL files (not just `[:1]`)

## 5. Testing & Verification

- [ ] 5.1 Run `uv run ruff check app/` on backend
- [ ] 5.2 Run `uv run pytest` on backend tests
- [ ] 5.3 Verify playbook files are accessible at new paths
- [ ] 5.4 Test a full pipeline run to confirm draft is passed to all agents
