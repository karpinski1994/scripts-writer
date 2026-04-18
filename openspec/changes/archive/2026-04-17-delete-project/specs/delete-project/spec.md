## ADDED Requirements

### Requirement: Delete Project
The system SHALL allow users to delete a project from the dashboard, removing both database records and the project's documents folder.

#### Scenario: Successful deletion
- **WHEN** user clicks the delete button (X) on a project card and confirms in the dialog
- **THEN** the system removes the project from the database (cascading to related records) and deletes the `documents/{project_slug}/` folder
- **AND** the project is removed from the dashboard list

#### Scenario: Cancel deletion
- **WHEN** user clicks the delete button (X) on a project card but clicks "Cancel" in the confirmation dialog
- **THEN** the project remains intact and the dialog closes

#### Scenario: Delete button does not navigate to project
- **WHEN** user clicks the delete button (X) on a project card
- **THEN** the click event propagation is stopped, preventing navigation to the project detail page

#### Scenario: Filesystem deletion fails
- **WHEN** the delete operation is triggered but the documents folder deletion fails
- **THEN** the database deletion proceeds and the error is logged; user sees successful deletion