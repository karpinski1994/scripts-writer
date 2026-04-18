## Context

The Scripts Writer application has a Dashboard (`frontend/src/app/page.tsx`) that displays project cards. Currently there is no way to delete projects. The backend already has a DELETE endpoint at `/api/v1/projects/{project_id}` which cascades database deletions via SQLAlchemy relationships, but it does not clean up the project's documents folder (`documents/{project_slug}/`).

## Goals / Non-Goals

**Goals:**
- Add delete button (X) to each project card in the Dashboard
- Show confirmation dialog before deletion to prevent accidental deletes
- Clean up both database records AND filesystem artifacts when deleting
- Ensure delete button doesn't trigger card navigation (stopPropagation)

**Non-Goals:**
- Add trash/restore functionality (permanent deletion only)
- Bulk delete (single project at a time)
- Add delete to project detail view (dashboard only for now)

## Decisions

1. **Use shadcn AlertDialog for confirmation**
   - Already available in the project
   - Provides accessible confirmation flow
   - Consistent with existing UI patterns

2. **Delete project folder using project name**
   - Folder path: `documents/{project_slug}/` where `project_slug = project.name.lower().replace(" ", "-")`
   - This matches how folders are created during pipeline execution

3. **Frontend-only delete button placement**
   - Button appears on each project card as an X in the top-right corner
   - Uses `e.stopPropagation()` to prevent click from navigating to project

## Risks / Trade-offs

- **Risk**: Project name changes after documents folder is created → folder orphaning
  - **Mitigation**: This is an existing issue not introduced by this change. The delete function uses current project name.
  
- **Risk**: Filesystem deletion fails but DB deletion succeeds
  - **Mitigation**: Wrap filesystem deletion in try/except, log error but don't fail the request (DB deletion is primary)

- **Risk**: Race condition if user clicks delete while project is being processed
  - **Mitigation**: Not handled in v1 - assume single user, sequential operations