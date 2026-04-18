## 1. Backend Agent Implementation

- [x] 1.1 Create `backend/app/agents/selection_rewrite_agent.py` with standalone LLM call (not BaseAgent)
- [x] 1.2 Define Pydantic input schema: SelectionRewriteInput (full_content, selected_text, instruction, icp_summary optional)
- [x] 1.3 Implement system prompt: "You are an expert editor. You will receive the FULL SCRIPT for context, but your ONLY job is to rewrite the EXACT SELECTED PORTION. Output ONLY the rewritten text."
- [ ] 1.4 Test agent with mock LLM provider

## 2. Backend API Endpoint

- [x] 2.1 Add `RewriteSelectionRequest` schema in `backend/app/schemas/script.py`
- [x] 2.2 Add `POST /{project_id}/scripts/rewrite-selection` endpoint in `backend/app/api/scripts.py`
- [x] 2.3 Implement endpoint logic: fetch ICP (if exists) → call SelectionRewriteAgent → return raw text
- [ ] 2.4 Test endpoint with curl/Postman

## 3. Frontend BubbleMenu Integration

- [x] 3.1 Import `BubbleMenu` from `@tiptap/react` in `script-editor.tsx`
- [x] 3.2 Add component state: `isRewriting: boolean`, `instruction: string`
- [x] 3.3 Add BubbleMenu component with Input field and Rewrite button
- [x] 3.4 Implement `handleRewrite` function:
  - Capture selection bounds (from, to)
  - Get full content via `editor.getText()`
  - Call API with full_content, selected_text, instruction
  - Replace selection with `editor.chain().focus().insertContentAt({ from, to }, newText).run()`
  - Trigger existing onUpdate for auto-save
- [x] 3.5 Add loading spinner (Loader2) to Rewrite button during API call

## 4. Error Handling & Polish

- [x] 4.1 Add error toast notification on API failure
- [x] 4.2 Ensure original selection preserved on failure (no replace called)
- [ ] 4.3 Test latency is under 3 seconds

## 5. Testing & Verification

- [ ] 5.1 Create unit test for selection_rewrite_agent prompt construction
- [ ] 5.2 Integration test: Select text → rewrite → verify replacement
- [ ] 5.3 Manual test: End-to-end in browser