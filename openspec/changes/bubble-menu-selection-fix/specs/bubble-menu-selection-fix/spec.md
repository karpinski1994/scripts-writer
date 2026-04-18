## ADDED Requirements

### Requirement: Selected text is preserved and displayed in BubbleMenu
The system SHALL preserve and display the selected text while the BubbleMenu is active, so users can see exactly which text they're rewriting.

#### Scenario: Selected text visible in BubbleMenu
- **WHEN** user selects text and BubbleMenu appears
- **THEN** the selected text is displayed within the BubbleMenu, visible to the user

#### Scenario: Selected text persists when input receives focus
- **WHEN** user clicks on the instruction input field in the BubbleMenu
- **THEN** the selected text remains visually highlighted/displayed in the BubbleMenu