---
Documentation Update List
Here's everything in the docs that contradicts the actual code, organized by document:
---
Doc 04 — Software Requirements Specification
1. SRS-F01 Target Format enum values — Says VSL/YouTube/Tutorial/Facebook/LinkedIn/Blog. Backend CHECK constraint uses "Short-form Video"/"Long-form Video"/"VSL"/"Blog Post"/"LinkedIn Post"/"Facebook Post". Frontend uses "VSL"/"YouTube"/"Tutorial"/"Facebook"/"LinkedIn"/"Blog". Three different enumerations exist — docs match neither.
2. External Interface: Modal model name — Says "GLM-5.1". Code uses zai-org/GLM-5.1-FP8.
3. Python version — Says "Python 3.11+". Code uses Python 3.13.
4. Pydantic AI dependency — Listed as a core dependency. Code does not use Pydantic AI at all — agents use raw factory.execute_with_failover() with manual JSON parsing.
5. Streaming — Says "LLM streaming via WebSocket". Code has no streaming — WebSocket only broadcasts agent_start, agent_complete, agent_failed. No agent_progress/streaming_token events.
---
Doc 05 — Technical Requirements Document
6. Target Format CHECK constraint — Says VSL/YouTube/Tutorial/Facebook/LinkedIn/Blog. Actual DB constraint: "Short-form Video"/"Long-form Video"/"VSL"/"Blog Post"/"LinkedIn Post"/"Facebook Post".
7. ICP source CHECK constraint — Says generated/uploaded/notebooklm. Actual: generated/uploaded/piragi.
8. Pipeline step_type CHECK constraint — Lists 10 values (icp/hook/narrative/retention/cta/writer/factcheck/readability/copyright/policy). Code has 12 step types including subject and analysis. No CHECK constraint on step_type in the actual model.
9. Projects table missing columns — Missing draft (Text, NOT NULL), cta_purpose (String 100), notebooklm_notebook_id (String 100).
10. ICP demographics JSON schema — Says {age_range, gender, location, occupation[], income}. Actual: {age_range, gender, income_level, education, location, occupation} (no arrays, different field names).
11. ICP psychographics JSON schema — Says {values[], interests[], attitudes[], lifestyle[]}. Actual: {values[], interests[], lifestyle, media_consumption[], personality_traits[]} (no attitudes, added media_consumption and personality_traits).
12. API route prefix: /analyze/ vs /analysis/ — Docs say POST .../analyze/{agent_type} and POST .../analyze/all. Actual: POST .../analysis/{agent_type}. No /all endpoint exists (removed).
13. POST .../pipeline/run-all — Listed in API endpoints. Does not exist in code.
14. POST .../piragi/* routes — Docs say /piragi/documents, /piragi/connect, etc. Actual routes use /rag/documents, /rag/connect, /rag/query, /rag/upload.
15. POST .../export/clipboard — Listed. Does not exist. Frontend handles clipboard copy client-side.
16. POST .../icp/generate only — Missing GET .../icp endpoint that exists in code.
17. Missing API endpoints not in docs:
    - POST /api/v1/projects/{id}/subject (SubjectUpdateRequest)
    - POST /api/v1/projects/{id}/branch (BranchRequest)
    - POST /api/v1/projects/{id}/pipeline/cancel
    - POST /api/v1/projects/{id}/pipeline/reset-errors
    - POST /api/v1/projects/{id}/rag/upload (file upload)
    - POST /api/v1/projects/{id}/hooks/upload (file upload)
    - Full NotebookLM API: GET .../notebooklm/notebooks, POST/DELETE .../notebooklm/connect, POST .../notebooklm/query
18. LLM Provider priority order — Says Modal(0)->Groq(1)->Gemini(2)->Ollama(3). Actual: Gemini(1)->Groq(2)->Modal(3)->Ollama(4).
19. Logging — Says logs to stdout + ./logs/app.log + ./logs/agents.log + ./logs/llm.log. Actual: only ./logs/app.log + console stream. No separate agent/LLM log files.
20. Gemini SDK — Says google-generativeai SDK. Actual: uses google.genai.Client from the newer google-genai package.
21. ProjectCreateRequest schema — Says includes name, topic, target_format, content_goal, raw_notes. Actual: only {name}.
22. AppSettings — Missing gemini_model and notebooklm_storage_path fields that exist in code.
---
Doc 06 — Technical Design Document
23. Backend package structure — Lists api/router.py. Doesn't exist. Missing api/hooks.py and api/rag.py that exist. Lists services/rag_service.py — actual is services/analysis_service.py + services/piragi_service.py + services/notebooklm_service.py + services/export_service.py.
24. Frontend package structure — Lists components/pipeline/step-card.tsx — doesn't exist. Lists agents/agent-output-panel.tsx — actual is agents/agent-panel-wrapper.tsx. Missing components/piragi/ directory. Missing components/agents/writer-panel.tsx, components/agents/subject-panel.tsx. Lists lib/ws.ts — doesn't exist.
25. BaseAgent class design — Says _build_agent() returns pydantic_ai.Agent and execute() uses Pydantic AI. Actual: _build_agent() exists but is unused. Agents use factory.execute_with_failover() with manual JSON parsing. Pydantic AI is not used.
26. ICPAgentOutput — Says includes suggestions[]. Actual: no suggestions field, just icp and confidence.
27. HookSuggestion — Says {rank, text, rationale, effectiveness_score}. Actual: {hook_type, text, reasoning}.
28. NarrativePattern — Says {name, description, fit_score, is_recommended, application_notes}. Actual: {pattern_name, description, structure: string[]}.
29. NarrativeAgentOutput — Says includes recommended_index. Actual: no recommended_index.
30. RetentionTechnique — Says {name, description, placement, fit_for_format[]}. Actual: {technique_name, description, placement_hint}.
31. CTASuggestion — Says {cta_type, suggested_wording, rationale, placement_options[]}. Actual: {cta_type, text, reasoning}.
32. ScriptDraft — Says {content, format, structural_cues[], word_count}. Actual: {title, content, word_count, notes}.
33. FactCheckAgentOutput — Says {findings[], claims_identified, claims_flagged}. Actual: {findings, confidence}.
34. ReadabilityAgentInput — Says includes target_grade (default 8). Actual: includes script_content, target_format. No target_grade.
35. ReadabilityAgentOutput — Says includes complex_sentence_count. Actual: {findings, flesch_kincaid_score, gunning_fog_score, confidence}. No complex_sentence_count.
36. CopyrightAgentOutput — Says includes risk_level. Actual: {findings, confidence}. No risk_level.
37. PolicyAgentInput — Says includes target_platforms[]. Actual: includes script_content, topic, target_format. No target_platforms.
38. PolicyAgentOutput — Says includes platforms_checked[]. Actual: {findings, confidence}. No platforms_checked.
39. Finding.severity — Says low/medium/high. Actual: low/medium/high/critical.
40. PipelineOrchestrator STEP_ORDER — Says 10 steps [ICP, HOOK, NARRATIVE, RETENTION, CTA, WRITER, FACTCHECK, READABILITY, COPYRIGHT, POLICY]. Actual: 12 steps including subject and analysis.
41. DEPENDENCY_MAP — Says HOOK:[ICP], NARRATIVE:[ICP,HOOK], RETENTION:[ICP,NARRATIVE], CTA:[ICP,HOOK,NARRATIVE], WRITER:[ICP,HOOK,NARRATIVE,RETENTION,CTA]. Actual: hook:[icp,subject], narrative:[icp,subject,hook], retention:[icp,subject,narrative], cta:[icp,subject,narrative(retention for video)], writer:[icp,subject,narrative,retention,cta]. Every step after ICP depends on subject.
42. run_analysis_parallel() — Still documented. Exists in code but is not called by any API endpoint (the /analysis/all route was removed).
43. Script version format — Docs don't mention that code always saves format as "VSL" regardless of actual target_format.
44. WebSocket events — Docs say agent_progress (streaming_token) and agent_complete (output). Actual events: agent_start, agent_complete, agent_failed. No streaming tokens.
45. API endpoint: POST .../analyze/all — Documented. Removed from code.
---
Doc 07 — High-Level Design
46. Architecture mentions Pydantic AI — Should be updated to reflect raw LLM calls with manual JSON parsing.
47. Module Dependency Graph — Missing Subject panel, Piragi store, NotebookLM service modules.
48. Data Flow: "parallel analysis" — Still describes asyncio.gather of 4 agents. This function exists but is unreachable via API. Analysis agents are now run individually.
49. WebSocket Streaming — Still describes streaming tokens. Not implemented.
---
Doc 08 — Low-Level Design
50. Create Project Dialog — Says full form with name, topic, target_format, content_goal, raw_notes. Actual: simple dialog with only name field.
51. Subject Panel — Not documented at all. Exists as a major component with Fast Track upload, format selector, topic/draft/goal fields.
52. Writer Panel — Not documented. Exists with Generate Script button, streaming output display, preview, and navigation buttons.
53. Agent Panel Wrapper — Not documented. Exists as the central routing component that swaps panels based on active step.
54. Hook Panel — Says "Ranked hook list with effectiveness stars". Actual: simple list with hook_type, text, reasoning. No ranking, no effectiveness stars.
55. Narrative Panel — Says "recommendation badge". Actual: has template quick-pick options (AIDA, PAS).
56. Retention Panel — Says "checkboxes with placements". Actual: multi-select with template options (Curiosity Gap, Teasers).
57. CTA Panel — Says "type radio (Subscribe, Buy, Click), suggested wording, placement radio". Actual: has CTA Purpose input, no placement radio.
58. Analysis Panel — Says "dismiss/apply buttons". Actual: only "Dismiss" button (no "Apply"). Says "Analyze All button". Removed.
59. Settings Page — Says "provider priority order (drag-drop)". Actual: no drag-drop. Simple form with enable/disable toggles and API key inputs.
60. Piragi components — Not documented: piragi-connect-panel.tsx, piragi-context-preview.tsx, step-document-dropzone.tsx.
61. Branch Dialog — Not documented in low-level design.
62. Export Panel — Not documented in low-level design.
63. PiragiStore — Not documented in Zustand stores section.
64. Frontend TargetFormat type — Says same as backend. Actual frontend type: "VSL" | "YouTube" | "Tutorial" | "Facebook" | "LinkedIn" | "Blog" — different from backend.
65. Agent Stream Hook — Says agent_progress -> appendStreamingToken. Actual: no agent_progress handling, only agent_start/agent_complete/agent_failed.
66. ICP Psychographics — Same discrepancy as Doc 05 (#11 above).
67. ICP Demographics — Same discrepancy as Doc 05 (#10 above).
68. Agent I/O Models — Same discrepancies as Doc 06 (#26-38 above).
69. Testing sections — Reference T-API-07: analyze all test case. Endpoint removed.
---
Doc 09 — Development Plan
70. Phase 3 Step Types — Lists 10 pipeline step types. Missing subject and analysis.
71. Phase 9 — Says "analysis panel with 'Analyze All' button". Button was removed.
72. Current Status — Says "12 pipeline steps" implicitly (10 listed). Actually 12 with subject and analysis.
73. Phase 8b remaining tasks — Tasks 8b.10 and 8b.11 still unchecked but phase marked as substantially complete.
---
Cross-cutting issues (affect multiple docs)
74. Frontend/Backend TargetFormat mismatch — Frontend uses "VSL"/"YouTube"/"Tutorial"/"Facebook"/"LinkedIn"/"Blog", backend uses "Short-form Video"/"Long-form Video"/"VSL"/"Blog Post"/"LinkedIn Post"/"Facebook Post". Docs match neither.
75. "Pydantic AI" throughout — Referenced in Docs 04, 05, 06, 07, 08 as a core technology. Not used in code.
76. "Streaming" throughout — Referenced in Docs 04, 05, 07, 08 as implemented. Not implemented.
77. NotebookLM integration — Barely mentioned in early docs (as "Google LM Notes"). Full API exists in code (/notebooklm/* routes, service, frontend store, UI components). Not documented in Docs 05/06/08 API sections.
78. Subject step — A major step in the pipeline (form-based, with Fast Track upload, format selector). Not mentioned in any doc.
79. RAG routes renamed — /piragi/* in docs → /rag/* in code.