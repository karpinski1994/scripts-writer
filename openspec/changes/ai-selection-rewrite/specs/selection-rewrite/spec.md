## ADDED Requirements

### Requirement: User can rewrite selected text in the Script Editor
The system SHALL allow users to select text in the Script Editor and request an AI-powered rewrite of only the selected portion while preserving the surrounding context.

#### Scenario: User rewrites selected text with instruction
- **WHEN** user selects text in the editor, enters an instruction (e.g., "make this punchier"), and clicks "Rewrite"
- **THEN** the system sends the full script content, selected text, and instruction to the backend, receives a rewritten version, and replaces the selection with the new text

#### Scenario: Rewrite button shows loading state during API call
- **WHEN** user clicks "Rewrite" button
- **THEN** the button displays a loading spinner and is disabled until the API response is received

#### Scenario: Rewrite fails gracefully
- **WHEN** the rewrite API returns an error or times out
- **THEN** the editor displays an error toast and the original selection remains unchanged

### Requirement: BubbleMenu appears on text selection
The system SHALL display a floating BubbleMenu above or below the selected text in the Script Editor when a user makes a text selection.

#### Scenario: BubbleMenu appears on non-empty selection
- **WHEN** user selects any non-empty text in the editor
- **THEN** a BubbleMenu appears anchored to the selection with an input field for instructions and a "Rewrite" button

#### Scenario: BubbleMenu hides on deselection
- **WHEN** user clicks away from the selection or presses Escape
- **THEN** the BubbleMenu disappears

### Requirement: Rewrite is auto-saved after replacement
The system SHALL automatically save the script after a successful rewrite operation using the existing debounced auto-save mechanism.

#### Scenario: Auto-save triggers after rewrite
- **WHEN** a rewrite operation successfully replaces the selected text
- **THEN** the auto-save mechanism captures the change within the existing 500ms debounce window

### Requirement: Rewrite uses ICP for tone matching (when available)
The system SHALL pass the project's ICP profile to the rewrite agent when an ICP exists, enabling the LLM to match the target audience's tone.

#### Scenario: Rewrite uses ICP context when available
- **WHEN** a project has an approved ICP profile and user triggers a rewrite
- **THEN** the ICP summary is included in the rewrite request for tone matching

#### Scenario: Rewrite works without ICP
- **WHEN** a project has no ICP profile and user triggers a rewrite
- **THEN** the rewrite proceeds without ICP context, using only the script content and instruction

### Requirement: Rewrite completes within 3 seconds
The system SHALL complete the rewrite operation within 3 seconds under normal conditions.

#### Scenario: Rewrite latency within target
- **WHEN** user triggers a rewrite
- **THEN** the operation completes and returns results within 3 seconds using the fastest available LLM provider

### Requirement: Rewrite returns raw text only
The system SHALL return only the rewritten text without markdown, JSON wrapper, or conversational filler.

#### Scenario: Rewrite returns plain text
- **WHEN** the rewrite agent returns a response
- **THEN** the response is plain text only, directly usable in the editor without parsing