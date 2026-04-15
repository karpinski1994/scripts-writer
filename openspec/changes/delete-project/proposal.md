## Why

The Dashboard currently lacks a way to delete projects. Users cannot remove unwanted projects, and when deleted, only database records are removed while the project's documents folder (`documents/{project_slug}/`) remains orphaned on disk.

## What Changes

- Add a delete button (X) on each project card in the Dashboard
- Add a confirmation dialog using shadcn AlertDialog before deletion
- Extend ProjectService.delete() to also remove the project's documents folder
- Use `e.stopPropagation()` on the delete button to prevent navigating to the project

## Capabilities

### New Capabilities
- `delete-project`: Delete a project from the dashboard, removing both database records (via cascade) and the project's documents folder

### Modified Capabilities
- None - existing Project API already has DELETE endpoint, just needs filesystem cleanup enhancement

## Impact

- **Backend**: Modify `ProjectService.delete()` to remove `documents/{project_slug}/` folder
- **Frontend**: Add delete button and confirmation dialog to Dashboard (`frontend/src/app/page.tsx`)
- **API**: Existing `/api/v1/projects/{project_id}` DELETE endpoint already exists, only needs service layer enhancement