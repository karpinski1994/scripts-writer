## Why

The current Piragi RAG integration queries only ONE document category per pipeline step. This means each step (ICP, Hook, Narrative, etc.) only sees its own documents, missing cumulative context from earlier steps. Additionally, Narrative/Retention/CTA steps need access to developer-provided hardcoded templates that are consistent across projects.

## What Changes

1. **Cumulative RAG context** - Each step queries all dependency categories plus its own category
2. **Step-based document uploads** - Users upload documents only for the pending step panel (ICP & Hook), not globally
3. **Dev-provided templates** - Hardcoded templates for Narrative/Retention/CTA that users can select from a fixed list

## Capabilities

### New Capabilities

- **cumulative-rag-context**: Each pipeline step queries cumulative documents from all dependency steps. Step 1 (ICP) gets ICP documents + notes. Step 2 (Hook) gets ICP + Hook documents + notes. Step 3+ gets cumulative context. Narrative/Retention/CTA also get dev-provided templates from `documents/narrative_patterns/` and `documents/retention_tactics/`.

- **step-document-upload**: Document dropzone appears on the pending step panel rather than a global Documents button. Only ICP & Hook steps support document uploads. Later steps show fixed template options.

- **template-selection**: Narrative, Retention, and CTA panels show 2 fixed template options (AIDA/PAS for Narrative, Curiosity Gap/Teasers for Retention) instead of dropzones. Templates are stored in `documents/narrative_patterns/` and `documents/retention_tactics/`.

### Modified Capabilities

- **piragi-rag-integration**: Update `get_step_context()` to use cumulative `STEP_DEPENDENCIES` mapping from config. Modify frontend panels: remove dropzone from Narrative/Retention/CTA, add to pending step panel only. Narrative/Retention/CTA panels show agent results first, then template options with "why_best" explanations.

## Impact

- Backend: `piragi_service.py` - `get_step_context()` modified to iterate over `STEP_DEPENDENCIES`
- Backend: `rag/config.py` - Added `STEP_DEPENDENCIES` and `DEV_PROVIDED_CATEGORIES` config
- Frontend: `step-document-dropzone.tsx` - New component added to pending step panels
- Documents: New folders `documents/narrative_patterns/` and `documents/retention_tactics/` with .txt templates