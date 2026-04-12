## Purpose

Defines the Tiptap-based rich script editor, editor Zustand store, structural cue highlighting, debounced auto-save, word count, and version history switching.

## ADDED Requirements

### Requirement: Editor Zustand store
The system SHALL provide `editor-store.ts` with: `content: string`, `versionNumber: number`, `currentVersionId: string | null`, `isDirty: boolean`, `isSaving: boolean`, `debounceTimer: ReturnType<typeof setTimeout> | null`, `setContent(content: string)`, `setVersionNumber(n: number)`, `setCurrentVersionId(id: string | null)`, `setIsSaving(saving: boolean)`, `markClean()`, `cancelPendingSave()`, `reset()`. `setContent` SHALL set `isDirty = true` and schedule a debounced save (500ms). `markClean` SHALL set `isDirty = false`. `cancelPendingSave` SHALL clear the debounce timer and set `isSaving = false`.

#### Scenario: Store initializes with empty state
- **WHEN** the store is created
- **THEN** `content` is `""`, `versionNumber` is `1`, `currentVersionId` is `null`, `isDirty` is `false`, `isSaving` is `false`

#### Scenario: Content change marks dirty and schedules save
- **WHEN** `setContent("New script content")` is called
- **THEN** `content` is `"New script content"`, `isDirty` is `true`, and a debounced save is scheduled for 500ms

#### Scenario: Cancel pending save on version switch
- **WHEN** `cancelPendingSave()` is called while a debounced save is pending
- **THEN** the debounce timer is cleared and `isSaving` is `false`

### Requirement: Tiptap script editor component
The system SHALL provide `script-editor.tsx` that renders a Tiptap editor instance with: formatting toolbar (Bold, Italic, H1, H2, Bullet List, Ordered List, Undo, Redo), word count display (computed from editor text), dirty indicator ("Unsaved" when `isDirty`, "Saving..." when `isSaving`, "Saved" when clean), and structural cue highlighting. The editor SHALL call `setContent(editor.getText())` on every content update. On mount, it SHALL initialize with the content from the editor store. The editor SHALL be read-only when `isSaving` is `true`.

#### Scenario: Editor renders with initial content
- **WHEN** the editor mounts with `content = "Hello world"` in the store
- **THEN** the Tiptap editor displays "Hello world"

#### Scenario: Typing updates store and shows dirty indicator
- **WHEN** the user types in the editor
- **THEN** `setContent` is called with the new text, "Unsaved" indicator appears, and after 500ms `PATCH /scripts/{version_id}` is called

#### Scenario: Auto-save completes
- **WHEN** the debounced save completes successfully
- **THEN** the indicator shows "Saved", `isDirty` is `false`, `isSaving` is `false`

#### Scenario: Word count displays
- **WHEN** the editor contains "The quick brown fox"
- **THEN** a word count of "4 words" is shown below the editor

### Requirement: Structural cue highlighting extension
The system SHALL provide a custom Tiptap Mark extension (`structural-cue-extension.ts`) that detects `[B-ROLL]`, `[TEXT OVERLAY]`, and `[PAUSE]` patterns in the editor text and applies distinct background highlighting: amber/yellow for `[B-ROLL]`, blue for `[TEXT OVERLAY]`, purple for `[PAUSE]`. The extension SHALL use Tiptap's `addInputRules` to match bracket patterns as they are typed and `addProseMirrorPlugins` to decorate existing occurrences on document load. The highlighted text SHALL be visually distinct but remain editable.

#### Scenario: Type structural cue
- **WHEN** the user types `[B-ROLL]` in the editor
- **THEN** the text `[B-ROLL]` is highlighted with an amber/yellow background

#### Scenario: Different cues have different colors
- **WHEN** the editor contains `[B-ROLL] some text [TEXT OVERLAY] more text [PAUSE]`
- **THEN** `[B-ROLL]` has amber background, `[TEXT OVERLAY]` has blue background, `[PAUSE]` has purple background

#### Scenario: Structural cues load on document open
- **WHEN** a script containing `[B-ROLL]` is loaded into the editor
- **THEN** the `[B-ROLL]` pattern is immediately highlighted

### Requirement: Editor toolbar component
The system SHALL provide `toolbar.tsx` that renders formatting buttons for the Tiptap editor. Each button SHALL be visually indicated as active when the corresponding format is applied at the cursor position. Buttons SHALL include: Bold, Italic, Heading 1, Heading 2, Bullet List, Ordered List, Undo, Redo.

#### Scenario: Bold button toggles bold
- **WHEN** the Bold button is clicked
- **THEN** the selected text becomes bold, and the Bold button shows an active state

### Requirement: Version history dropdown
The system SHALL provide `version-dropdown.tsx` that fetches `GET /api/v1/projects/{project_id}/scripts` and renders a dropdown of script versions. Each option SHALL show the version number and creation timestamp. Selecting a version SHALL: (1) cancel any pending save via `cancelPendingSave()`, (2) load the version's content into the editor store, (3) update `currentVersionId` and `versionNumber` in the store. The currently active version SHALL be indicated in the dropdown.

#### Scenario: Version dropdown shows versions
- **WHEN** a project has 2 script versions
- **THEN** the dropdown shows "v1 — Apr 12, 2026" and "v2 — Apr 12, 2026"

#### Scenario: Switch version loads content
- **WHEN** the user selects "v1" from the dropdown
- **THEN** the editor loads v1's content, `currentVersionId` is updated to v1's ID, `versionNumber` is `1`, and `isDirty` is `false`

#### Scenario: Switching version cancels pending save
- **WHEN** the user types (triggering a debounced save) and then immediately switches to v2
- **THEN** the pending save is cancelled, and v2's content loads without overwriting v1

### Requirement: Dedicated editor page
The system SHALL provide `frontend/src/app/projects/[id]/editor/page.tsx` that renders the full script editor experience: a header with project name and back-to-pipeline link, the version dropdown, the toolbar, the Tiptap editor, and word count / save status. The page SHALL fetch the latest script version on mount and load it into the editor store. On unmount, the store SHALL be reset.

#### Scenario: Navigate to editor page
- **WHEN** the user navigates to `/projects/{id}/editor`
- **THEN** the full editor page renders with the latest script version loaded

#### Scenario: Back to pipeline
- **WHEN** the user clicks the back link
- **THEN** they are navigated to `/projects/{id}` (the pipeline view)

#### Scenario: No script versions exist
- **WHEN** the user navigates to the editor page and no script versions exist
- **THEN** a "Generate a script first" message is shown with a link back to the pipeline view
