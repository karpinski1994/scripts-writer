## 1. Backend Enhancement

- [x] 1.1 Modify ProjectService.delete() to remove documents/{project_slug}/ folder
- [x] 1.2 Add filesystem path constant or helper to determine documents folder location

## 2. Frontend Implementation

- [x] 2.1 Import AlertDialog component in Dashboard page
- [x] 2.2 Add deleteTarget state to track which project is being deleted
- [x] 2.3 Add delete button (X) to each project card with stopPropagation
- [x] 2.4 Implement confirmation dialog with project name
- [x] 2.5 Connect delete dialog to API DELETE endpoint
- [x] 2.6 Add optimistic update to remove project from list after deletion

## 3. Testing & Verification

- [x] 3.1 Test deletion with a project that has documents folder
- [x] 3.2 Test deletion with a project that has no documents folder
- [x] 3.3 Verify database cascade deletion works (related records removed)
- [x] 3.4 Test cancel button behavior
- [x] 3.5 Test that clicking X doesn't navigate to project