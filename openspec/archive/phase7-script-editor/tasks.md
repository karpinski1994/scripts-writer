## 1. Install Tiptap Dependencies

- [ ] 1.1 Install Tiptap packages: `npm install @tiptap/react @tiptap/starter-kit @tiptap/pm @tiptap/extension-highlight`
- [ ] 1.2 Verify: `npm ls @tiptap/react` shows installed

## 2. Editor Zustand Store

- [ ] 2.1 Create `frontend/src/stores/editor-store.ts` — Zustand store with `content`, `versionNumber`, `currentVersionId`, `isDirty`, `isSaving`, `debounceTimer`, and actions: `setContent` (sets dirty, schedules 500ms debounced save via `PATCH /scripts/{version_id}`), `setVersionNumber`, `setCurrentVersionId`, `setIsSaving`, `markClean`, `cancelPendingSave` (clears timer, sets isSaving false), `reset`. The debounced save in `setContent` SHALL: clear any existing timer, set a new 500ms timer that calls `api.patch('/api/v1/projects/scripts/' + currentVersionId, { content })`, set `isSaving = true` before the call, then `isSaving = false` and `isDirty = false` after success. On failure, keep `isDirty = true`.
- [ ] 2.2 Verify: `npm run build` passes

## 3. Structural Cue Highlighting Extension

- [ ] 3.1 Create `frontend/src/components/editor/structural-cue-extension.ts` — Tiptap Mark extension that: (1) defines three mark types via `addVariants` or separate marks: `brollCue` (amber bg), `textOverlayCue` (blue bg), `pauseCue` (purple bg); (2) uses `addInputRules` to match `[B-ROLL]`, `[TEXT OVERLAY]`, `[PAUSE]` patterns and apply the corresponding mark; (3) uses `addProseMirrorPlugins` with a decoration plugin that scans the document on load/change and applies inline decorations with the appropriate background color class; (4) marks are not exclusive (text can have multiple cues). CSS classes: `.cue-broll` (amber bg), `.cue-text-overlay` (blue bg), `.cue-pause` (purple bg).
- [ ] 3.2 Add structural cue CSS classes to `frontend/src/app/globals.css` — `.cue-broll { background-color: rgb(254 243 199); border-radius: 2px; padding: 0 2px; }` (amber-100), `.cue-text-overlay { background-color: rgb(219 234 254); border-radius: 2px; padding: 0 2px; }` (blue-100), `.cue-pause { background-color: rgb(243 232 255); border-radius: 2px; padding: 0 2px; }` (purple-100). Add dark mode variants using Tailwind dark: prefix colors.
- [ ] 3.3 Verify: `npm run build` passes

## 4. Editor Toolbar Component

- [ ] 4.1 Create `frontend/src/components/editor/toolbar.tsx` — React component receiving Tiptap `editor` instance as prop. Renders button group: Bold (toggleBold), Italic (toggleItalic), H1 (toggleHeading { level: 1 }), H2 (toggleHeading { level: 2 }), Bullet List, Ordered List, separator, Undo, Redo. Each button shows active state (darker bg) when the format is active at cursor. Uses Shadcn Button component with `variant="ghost"` and `size="icon-sm"`. Separator is a vertical divider `|`.
- [ ] 4.2 Verify: `npm run build` passes

## 5. Script Editor Component

- [ ] 5.1 Create `frontend/src/components/editor/script-editor.tsx` — Uses `useEditor` from `@tiptap/react` with `StarterKit`, `Highlight`, and the structural cue extensions. On `onUpdate`, calls `editorStore.setContent(editor.getText())`. Renders: `Toolbar`, the Tiptap `EditorContent`, and a status bar with word count (`editor.storage.characterCount.words()` or manual count) and save status indicator. Reads `isDirty`, `isSaving` from editor store. Shows "Unsaved" (amber), "Saving..." (blue), or "Saved" (green) indicator. Passes `editable={!isSaving}` to editor options.
- [ ] 5.2 Verify: `npm run build` passes

## 6. Version History Dropdown

- [ ] 6.1 Create `frontend/src/components/editor/version-dropdown.tsx` — Uses TanStack Query to fetch `GET /api/v1/projects/{project_id}/scripts`. Renders a Shadcn Select dropdown with options showing "v{version_number} — {created_at formatted as date}". On select: calls `editorStore.cancelPendingSave()`, then `editorStore.setCurrentVersionId(version.id)`, `editorStore.setVersionNumber(version.version_number)`, `editorStore.setContent(version.content)`, `editorStore.markClean()`.
- [ ] 6.2 Verify: `npm run build` passes

## 7. Writer Panel Component

- [ ] 7.1 Create `frontend/src/components/agents/writer-panel.tsx` — Props: `projectId`, `step` (PipelineStep), `onRun`, `onNavigateToEditor`. When step is completed: parse `output_data` JSON as `WriterAgentOutput`, show script preview (first 500 chars of `script.content`), show "Open in Editor" button (calls `onNavigateToEditor`), show "Regenerate" button (calls `onRun`). When step is running: show spinner with "Generating script..." or streaming text from `pipeline-store.streamingOutput["writer"]` via `StreamingText` component. When step is pending: show "Generate Script" button.
- [ ] 7.2 Verify: `npm run build` passes

## 8. Agent Panel Wrapper Update

- [ ] 8.1 Update `frontend/src/components/agents/agent-panel-wrapper.tsx` — Add `writer` case to the switch statement. When `activeStepType === "writer"`: parse `output_data` as `WriterAgentOutput`, render `WriterPanel` with `projectId`, `step`, `onRun` (same `runAgent` function), and `onNavigateToEditor` (calls `router.push('/projects/' + projectId + '/editor')`). Import `useRouter` from `next/navigation`.
- [ ] 8.2 Verify: `npm run build` passes

## 9. Dedicated Editor Page

- [ ] 9.1 Create `frontend/src/app/projects/[id]/editor/page.tsx` — "use client" page. Uses `useParams` to get project ID. Fetches project detail and script versions via TanStack Query. On mount: if versions exist, load latest version into editor store (`setCurrentVersionId`, `setVersionNumber`, `setContent`, `markClean`). Renders: header with back link to pipeline view + project name, version dropdown, script editor component. If no versions exist: show "No script versions yet. Generate a script from the pipeline first." with a link to `/projects/{id}`. On unmount: call `editorStore.reset()`.
- [ ] 9.2 Verify: `npm run build` passes

## 10. Full Stack Verification

- [ ] 10.1 Run `uv run pytest tests/ -q` — all backend tests pass (no backend changes expected, but verify no regressions)
- [ ] 10.2 Run `uv run ruff check app/` — backend lint clean
- [ ] 10.3 Run `npm run lint && npm run build` — frontend clean
