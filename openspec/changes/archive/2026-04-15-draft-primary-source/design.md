## Context

The Scripts Writer pipeline has 5 creative agents: Hook, Narrative, Retention, CTA, and Writer. Currently only the Hook agent receives the `draft` field (user's refined content from the Subject step), and it's treated as auxiliary. The other 4 agents rely solely on ICP, selected hook, narrative pattern, etc. — but never see the actual content the user wrote. This produces generic outputs disconnected from the user's real message.

Additionally, the orchestrator's `playbooks_base` path (`documents/playbooks/`) doesn't exist. The actual reference files are at `documents/hooks/`, `documents/narrative_patterns/`, and `documents/retention_tactics/`. Only the Hook agent was recently fixed to read from the correct path.

## Goals / Non-Goals

**Goals:**
- Establish `draft` as the PRIMARY source of truth for all 5 creative agents (except ICP, which runs before the draft exists)
- Communicate the priority hierarchy to LLMs via both SYSTEM_PROMPT and prompt structure
- Fix global playbook paths so all agents can reference example files
- Read ALL playbook files (not just the first one) to give agents richer context

**Non-Goals:**
- Changes to ICP agent (it runs before draft exists)
- Changes to analysis agents (fact-check, readability, copyright, policy)
- Removing `raw_notes` from WriterAgent (it's supplementary, keep both)
- Token budget management for longer drafts

## Decisions

1. **Draft-first prompt structure with emphasis labels**
   - Use `=== PRIMARY SOURCE (Draft/Content) ===` headers in prompts
   - Label auxiliary data explicitly: `(auxiliary — shapes HOW, not WHAT)`
   - Alternative considered: Just putting draft first without labels → rejected because LLMs weight early content similarly; explicit labels create stronger priority signal

2. **Keep `raw_notes` alongside `draft` in WriterAgent**
   - `raw_notes` = original user input (shorter, from project creation)
   - `draft` = refined content from Subject step (longer, more detailed)
   - Both provide value: raw_notes captures initial intent, draft captures refined direction

3. **Move filesystem folders to match `playbooks_base` path**
   - Move `documents/narrative_patterns/` → `documents/playbooks/narrative_patterns/`
   - Move `documents/retention_tactics/` → `documents/playbooks/retention_tactics/`
   - Keep `documents/hooks/` as-is (already working, different path pattern — read via direct global path)
   - Alternative considered: Change orchestrator paths to match existing folders → rejected because `playbooks_base` is a cleaner organizational pattern for future growth

4. **Read ALL playbook files, not just `[:1]`**
   - Currently agents only read the first file found in playbook directories
   - There are 3 narrative pattern files (aida, pas, heroes_journey) and 2 retention tactic files (teasers, curiosity_gap)
   - Reading all files gives agents richer reference material

## Risks / Trade-offs

- **Risk**: Longer prompts due to draft + all playbook files → higher token usage
  - **Mitigation**: Accept for now; monitor token counts and add truncation if needed in future

- **Risk**: Moving filesystem folders could break other references
  - **Mitigation**: The `documents/` folder is only read by the orchestrator (backend) — no frontend references. Search codebase for any other references before moving.

- **Risk**: Over-emphasizing draft might cause agents to ignore ICP/hooks
  - **Mitigation**: The prompt labels say "auxiliary" not "ignore" — ICP still shapes HOW, draft shapes WHAT
