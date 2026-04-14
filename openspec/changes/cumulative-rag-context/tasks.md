## 1. Backend Configuration

- [x] 1.1 Add STEP_DEPENDENCIES mapping to rag/config.py
- [x] 1.2 Add DEV_PROVIDED_CATEGORIES config to rag/config.py

## 2. Backend Service Implementation

- [x] 2.1 Update PiragiService.get_step_context() to query cumulative categories
- [x] 2.2 Test cumulative context retrieval

## 3. Dev-Provided Template Documents

- [x] 3.1 Create documents/narrative_patterns/ folder with AIDA template
- [x] 3.2 Add HERO'S Journey narrative template
- [x] 3.3 Add PAS narrative template
- [x] 3.4 Create documents/retention_tactics/ folder with Curiosity Gap template
- [x] 3.5 Add Teasers retention template

## 4. Frontend Panel Updates

- [x] 4.1 Update Narrative panel to show agent results first, then 2 fixed options (AIDA, PAS) with why_best explanations
- [x] 4.2 Update Retention panel to show agent results first, then 2 fixed options (Curiosity Gap, Teasers) with why_best explanations
- [x] 4.3 Update CTA panel to show agent results first, then fixed options (Subscribe, Buy) with why_best explanations
- [x] 4.4 Remove global Documents button from project page
- [x] 4.5 Add NotebookLMContext component to Narrative/Retention/CTA panels

## 5. Integration Testing

- [ ] 5.1 Test ICP step gets only ICP context
- [ ] 5.2 Test Hook step gets ICP + Hook cumulative context
- [ ] 5.3 Test Narrative step gets ICP + Hook + narrative_patterns context
- [ ] 5.4 Test template selection flow
- [ ] 5.5 Test agent results display in panels