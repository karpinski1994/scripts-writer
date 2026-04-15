# Low-Level Design – Scripts Writer

## Component Detailed Design

### Frontend: Dashboard Module

**File:** `frontend/src/app/page.tsx`

```
State:
  projects: Project[]           (fetched via TanStack Query)
  isLoading: boolean
  error: string | null
  deleteTarget: Project | null   (project pending deletion)

Lifecycle:
  1. On mount, fetch GET /api/v1/projects
  2. Render project cards sorted by updated_at DESC
  3. Each card shows: name, target_format badge, status badge, updated_at, delete button (X)
  4. "New Project" button → navigate to /projects/new
  5. Delete button (X) → set deleteTarget → open AlertDialog confirmation

Actions:
  - onClick(project) → navigate to /projects/{id}
  - onClick(new) → open create dialog
  - onDeleteClick(e, project) → e.stopPropagation(), set deleteTarget
  - onDeleteConfirm → DELETE /api/v1/projects/{id} → invalidate query → set deleteTarget(null)
  - onDeleteCancel → set deleteTarget(null)
```

**File:** `frontend/src/components/dashboard/create-project-dialog.tsx`

```
Props: open, onClose
State:
  form: { name }  (only name field - other fields set via Subject step)
  isSubmitting: boolean
  errors: Record<string, string>

Validation (Zod):
  name: string().min(1).max(100)

Actions:
  - onSubmit → POST /api/v1/projects { name } → on success, navigate to /projects/{id}
  - onCancel → close dialog
```

---

### Frontend: Pipeline Module

**File:** `frontend/src/components/pipeline/pipeline-view.tsx`

```
Props: projectId: string
State (Zustand pipelineStore):
  steps: PipelineStep[]
  streamingOutput: Record<string, string>
  isRunning: boolean

Layout:
  ┌──────────────────────────────────────────────────────┐
  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  │
  │  │ ICP  │─►│ Hook │─►│Narrat│─►│Reten │─►│ CTA  │  │
  │  │  ✓   │  │  ✓   │  │  ●   │  │      │  │      │  │
  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  │
  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐             │
  │  │Write │─►│FactC │─►│Read  │─►│Copy  │─►Policy    │
  │  │      │  │      │  │      │  │      │             │
  │  └──────┘  └──────┘  └──────┘  └──────┘             │
  └──────────────────────────────────────────────────────┘

  Status indicators: ✓ completed, ● running, ○ pending, ✗ failed

Actions:
  - onClick(step) → navigate to step's agent panel
  - onRun(step) → POST /pipeline/run/{step_type} → start streaming
```

**File:** `frontend/src/components/pipeline/step-sidebar.tsx`

```
Props: steps: PipelineStep[], currentStep: string
Render:
  Vertical list of steps with status icons
  Clickable for non-linear navigation (re-run completed, navigate to current)
  Current step highlighted
  Locked steps (dependency not met) grayed out with tooltip
```

---

### Frontend: Agent Interaction Panels

**File:** `frontend/src/components/agents/icp-panel.tsx`

```
Props: projectId: string, stepId: string
State:
  icp: ICPProfile | null
  isEditing: boolean
  editFields: { demographics, psychographics, pain_points, desires, objections, language_style }

Layout:
  ┌──────────────────────────────────────┐
  │  ICP Analysis                    [✎] │
  │──────────────────────────────────────│
  │  Demographics                        │
  │    Age: 25-45                        │
  │    Occupation: Software Engineer     │
  │                                      │
  │  Psychographics                       │
  │    Values: Efficiency, Learning      │
  │                                      │
  │  Pain Points                          │
  │    • Content is boring               │
  │    • Low retention rates             │
  │                                      │
  │  Desires                              │
  │    • Grow audience                   │
  │                                      │
  │  Objections                           │
  │    • Don't have time to learn         │
  │                                      │
  │  Language Style: Professional        │
  │                                      │
  │  Source: Generated                   │
  │──────────────────────────────────────│
  │  [Re-run ICP Agent]  [Approve & Continue] │
  └──────────────────────────────────────┘

Actions:
  - onEdit → toggle isEditing, show inline editable fields
  - onReRun → POST /pipeline/run/icp → stream new output
  - onApprove → PATCH /pipeline/{step_id} { approved: true } → navigate to next step
  - onFieldChange(field, value) → local state only (saved on Approve)

NotebookLM Context (shown when notebook connected to project):
  ┌──────────────────────────────────────┐
  │  NotebookLM Context                  │
  │──────────────────────────────────────│
  │  📓 Connected: "Audience Research"    │
  │  [Query for ICP insights]           │
  │                                      │
  │  Insights:                           │
  │  • Target audience is mid-level...   │
  │  • Primary pain point is...          │
  │  [Include in ICP generation] ☑      │
  └──────────────────────────────────────┘
```

**File:** `frontend/src/components/agents/hook-panel.tsx`

```
Props: projectId: string, stepId: string
State:
  hooks: HookSuggestion[]
  selectedIndex: number | null
  customHook: string
  isCustom: boolean

Layout:
  ┌──────────────────────────────────────┐
  │  Hook Suggestions                     │
  │──────────────────────────────────────│
  │  ○ #1  "What if I told you..."       │
  │       Rationale: Addresses pain point  │
  │       Effectiveness: ★★★★☆           │
  │                                      │
  │  ● #2  "Stop writing Python the..."   │  ← selected
  │       Rationale: Pattern interrupt     │
  │       Effectiveness: ★★★★★          │
  │                                      │
  │  ○ #3  ...                           │
  │                                      │
  │  ─── Or write your own ───            │
  │  [____________________________]       │
  │──────────────────────────────────────│
  │  [Edit Selected]  [Continue with Hook]│
  └──────────────────────────────────────┘

Actions:
  - onSelect(index) → selectedIndex = index; isCustom = false
  - onCustom() → isCustom = true; selectedIndex = null
  - onEdit → open inline editor for selected/custom hook
  - onContinue → PATCH /pipeline/{step_id} { selected_option: { hook_text, rank } }

NotebookLM Context (shown when notebook connected to project):
  ┌──────────────────────────────────────┐
  │  NotebookLM Context                  │
  │──────────────────────────────────────│
  │  📓 Connected: "Audience Research"    │
  │  [Query for Hook insights]          │
  │                                      │
  │  Insights:                           │
  │  • Best hooks for this audience...   │
  │  • Emotional triggers include...    │
  │  [Include in Hook generation] ☑     │
  └──────────────────────────────────────┘
```

**File:** `frontend/src/components/agents/narrative-panel.tsx`

```
Props: projectId: string, stepId: string
State:
  patterns: NarrativePattern[]
  selectedIndex: number | null
  descriptionVisible: number | null

Layout:
  ┌──────────────────────────────────────┐
  │  Narrative Patterns                  │
  │──────────────────────────────────────│
  │  ○ PAS - Problem-Agitate-Solution    │
  │    [?] ► "Best for pain-point..."    │
  │                                      │
  │  ● AIDA - Attention-Interest-...     │  ← selected, recommended
  │    [?] ► "Ideal for VSL format..."   │  ★ Recommended
  │                                      │
  │  ○ Story Loop                        │
  │    [?] ► "Open loop closes at end"   │
  │                                      │
  │  ○ Before-After-Bridge               │
  │    [?] ► "Contrast drives desire"    │
  │──────────────────────────────────────│
  │  [Continue with AIDA]                │
  └──────────────────────────────────────┘

Actions:
  - onSelect(index) → selectedIndex = index
  - onInfo(index) → toggle descriptionVisible
  - onContinue → PATCH /pipeline/{step_id} { selected_option: { pattern, recommendation_rank } }

NotebookLM Context (shown when notebook connected to project):
  ┌──────────────────────────────────────┐
  │  NotebookLM Context                  │
  │──────────────────────────────────────│
  │  📓 Connected: "Audience Research"    │
  │  [Query for Narrative insights]     │
  │                                      │
  │  Insights:                           │
  │  • Audience responds to stories...   │
  │  • PAS pattern historically works... │
  │  [Include in Narrative selection] ☑ │
  └──────────────────────────────────────┘
```

**File:** `frontend/src/components/agents/retention-panel.tsx`

```
Props: projectId: string, stepId: string
State:
  techniques: RetentionTechnique[]
  selectedIndices: Set<number>

Layout:
  ┌──────────────────────────────────────┐
  │  Retention Techniques                │
  │  (Select all that apply)             │
  │──────────────────────────────────────│
  │  ☑ Pattern Interrupt                 │
  │    Place at: 30% mark                │
  │                                      │
  │  ☑ Open Loop                         │
  │    Place at: 15% mark, close at 80%  │
  │                                      │
  │  ☐ Visual Cue                        │
  │    [B-ROLL] at key transitions       │
  │                                      │
  │  ☐ Subheading Reset                  │
  │    Every 300 words                   │
  │──────────────────────────────────────│
  │  [Continue with 2 techniques]        │
  └──────────────────────────────────────┘

Actions:
  - onToggle(index) → add/remove from selectedIndices
  - onContinue → PATCH /pipeline/{step_id} { selected_option: { techniques: [...] } }

NotebookLM Context (shown when notebook connected to project):
  ┌──────────────────────────────────────┐
  │  NotebookLM Context                  │
  │──────────────────────────────────────│
  │  📓 Connected: "Audience Research"    │
  │  [Query for Retention insights]     │
  │                                      │
  │  Insights:                           │
  │  • Audience drop-off at 40% mark...  │
  │  • Pattern interrupts effective...  │
  │  [Include in Retention selection] ☑│
  └──────────────────────────────────────┘
```

**File:** `frontend/src/components/agents/cta-panel.tsx`

```
Props: projectId: string, stepId: string
State:
  suggestions: CTASuggestion[]
  selectedType: string | null
  customWording: string
  placement: string

Layout:
  ┌──────────────────────────────────────┐
  │  Call to Action                      │
  │──────────────────────────────────────│
  │  Type: ○ Subscribe  ● Buy  ○ Click   │
  │                                      │
  │  Suggested wording:                   │
  │  "Enroll now and start building..."   │
  │                                      │
  │  Customize:                           │
  │  [____________________________]       │
  │                                      │
  │  Placement:                           │
  │  ○ End only                           │
  │  ● Mid + End                         │
  │  ○ Soft + Hard CTA                   │
  │──────────────────────────────────────│
  │  [Continue with CTA]                 │
  └──────────────────────────────────────┘

Actions:
  - onSelectType(type) → selectedType = type; load suggestion
  - onCustomize(text) → customWording = text
  - onSelectPlacement(p) → placement = p
  - onContinue → PATCH /pipeline/{step_id} { selected_option: { cta_type, cta_text, placement } }

NotebookLM Context (shown when notebook connected to project):
  ┌──────────────────────────────────────┐
  │  NotebookLM Context                  │
  │──────────────────────────────────────│
  │  📓 Connected: "Audience Research"    │
  │  [Query for CTA insights]           │
  │                                      │
  │  Insights:                           │
  │  • Audience prefers soft CTAs...     │
  │  • Mid-video CTAs convert at 2x...   │
  │  [Include in CTA generation] ☑     │
  └──────────────────────────────────────┘
```

---

### Frontend: Script Module

**File:** `frontend/src/components/editor/script-editor.tsx`

```
Props: projectId: string, versionId: string
State (Zustand editorStore):
  content: string
  versionNumber: number
  isDirty: boolean
  isSaving: boolean
  debounceTimer: NodeJS.Timeout | null

Editor: Tiptap rich-text editor
  - Toolbar: Bold, Italic, Headings, Lists, Undo/Redo
  - Custom markers for [B-ROLL], [TEXT OVERLAY], [PAUSE] (highlighted)
  - Word count display
  - Auto-save: debounced 500ms → PATCH /scripts/{version_id}

Actions:
  - onContentChange(content) → setContent(content), isDirty = true, schedule debounced save
  - onManualSave → immediate PATCH /scripts/{version_id}
  - onVersionSwitch(versionId) → load version content
```

---

### Frontend: Analysis Module

**File:** `frontend/src/components/agents/analysis-panel.tsx`

```
Props: projectId: string, scriptVersionId: string
State:
  results: AnalysisResult[]
  activeTab: "factcheck" | "readability" | "copyright" | "policy"
  isLoading: boolean

Layout:
  ┌──────────────────────────────────────────────┐
  │  [Fact Check] [Readability] [Copyright] [Policy] │
  │──────────────────────────────────────────────│
  │                                              │
  │  Fact Check Results                          │
  │  ┌──────────────────────────────────────┐    │
  │  │ ⚠ MEDIUM  "Python is the most..."     │    │
  │  │   Confidence: Low                     │    │
  │  │   Suggestion: Add qualifier           │    │
  │  │   [Dismiss] [Apply Suggestion]        │    │
  │  └──────────────────────────────────────┘    │
  │  ┌──────────────────────────────────────┐    │
  │  │ ✓ HIGH     "Ollama runs locally"      │    │
  │  │   Confidence: High                   │    │
  │  └──────────────────────────────────────┘    │
  │                                              │
  └──────────────────────────────────────────────┘

Per-Tab Rendering:
  - FactCheck: list of claims with severity, confidence, suggestion
  - Readability: overall score gauge, flagged sentences with suggestions
  - Copyright: warnings with acknowledge button
  - Policy: platform-specific flags with advisory notices

Actions:
  - onTabChange(tab) → activeTab = tab
  - onDismiss(findingId) → mark as acknowledged (local state only)
  - onApplySuggestion(findingId) → insert suggestion into script editor
  - onReRun(agentType) → POST /analyze/{agent_type}
```

---

### Frontend: Settings Module

**File:** `frontend/src/app/settings/page.tsx`

```
State:
  config: LLMConfig
  providerStatus: Record<string, boolean>

Layout:
  ┌──────────────────────────────────────┐
  │  LLM Provider Configuration          │
  │──────────────────────────────────────│
  │  Provider Priority Order:            │
  │  1. Modal (GLM-5.1)    [●]  [Test]  │
  │  2. Groq               [●]  [Test]  │
  │  3. Google Gemini       [●]  [Test]  │
  │  4. Ollama (local)     [●]  [Test]  │
  │                                      │
  │  Modal API Key: [••••••••nyTp]       │
  │  Groq API Key:  [••••••••]          │
  │  Gemini API Key:[••••••••]          │
  │  Ollama URL:    [localhost:11434]    │
  │                                      │
  │  [Test All Connections]  [Save]      │
  └──────────────────────────────────────┘

Actions:
  - onTestProvider(name) → GET /settings/llm/status → show checkmark/X
  - onTestAll → GET /settings/llm/status → show all statuses
  - onSave → PATCH /settings/llm → save config
  - onReorder → drag-and-drop priority → PATCH /settings/llm
```

---

### Frontend: WebSocket & Streaming Hooks

**File:** `frontend/src/hooks/use-websocket.ts`

```typescript
function useWebSocket(projectId: string) {
  const [status, setStatus] = useState<"connecting" | "open" | "closed">("connecting");
  const [lastEvent, setLastEvent] = useState<WSEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/pipeline/${projectId}`);
    ws.onopen = () => { setStatus("open"); reconnectAttempts.current = 0; };
    ws.onclose = () => {
      setStatus("closed");
      const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000);
      reconnectAttempts.current += 1;
      setTimeout(connect, delay);
    };
    ws.onmessage = (event) => {
      const data: WSEvent = JSON.parse(event.data);
      setLastEvent(data);
    };
    wsRef.current = ws;
  }, [projectId]);

  useEffect(() => { connect(); return () => wsRef.current?.close(); }, [connect]);

  return { status, lastEvent, send: (data: unknown) => wsRef.current?.send(JSON.stringify(data)) };
}
```

**File:** `frontend/src/hooks/use-agent-stream.ts`

```typescript
function useAgentStream(projectId: string) {
  const { lastEvent } = useWebSocket(projectId);
  const appendToken = usePipelineStore((s) => s.appendStreamingToken);
  const clearStreaming = usePipelineStore((s) => s.clearStreaming);
  const setStepOutput = usePipelineStore((s) => s.setStepOutput);

  useEffect(() => {
    if (!lastEvent) return;
    switch (lastEvent.event) {
      case "agent_start":
        clearStreaming(lastEvent.step_type);
        break;
      case "agent_progress":
        appendToken(lastEvent.step_type, lastEvent.streaming_token);
        break;
      case "agent_complete":
        setStepOutput(lastEvent.step_type, lastEvent.output);
        break;
    }
  }, [lastEvent]);
}
```

---

### Frontend: NotebookLM API Client

**File:** `frontend/src/lib/notebooklm-api.ts`

```typescript
const notebooklmApi = {
  listNotebooks: (projectId: string) =>
    api.get<{ id: string; title: string }[]>(`/api/v1/projects/${projectId}/notebooklm/notebooks`),

  connectNotebook: (projectId: string, notebookId: string) =>
    api.post(`/api/v1/projects/${projectId}/notebooklm/connect`, { notebook_id: notebookId }),

  disconnectNotebook: (projectId: string) =>
    api.delete(`/api/v1/projects/${projectId}/notebooklm/connect`),

  queryNotebook: (projectId: string, query: string, stepType: string) =>
    api.post<{ context: string }>(`/api/v1/projects/${projectId}/notebooklm/query`, { query, step_type: stepType }),
};
```

**File:** `frontend/src/stores/pipeline-store.ts`

```typescript
interface PipelineStore {
  activeProjectId: string | null;
  steps: PipelineStep[];
  streamingOutput: Record<string, string>;
  isRunning: boolean;

  setActiveProject: (id: string) => void;
  setSteps: (steps: PipelineStep[]) => void;
  setStepOutput: (stepType: string, output: string) => void;
  appendStreamingToken: (stepType: string, token: string) => void;
  clearStreaming: (stepType: string) => void;
  setIsRunning: (running: boolean) => void;
  reset: () => void;
}

const usePipelineStore = create<PipelineStore>((set) => ({
  activeProjectId: null,
  steps: [],
  streamingOutput: {},
  isRunning: false,

  setActiveProject: (id) => set({ activeProjectId: id }),
  setSteps: (steps) => set({ steps }),
  setStepOutput: (stepType, output) =>
    set((state) => ({
      steps: state.steps.map((s) =>
        s.step_type === stepType ? { ...s, output_data: output, status: "completed" } : s
      ),
    })),
  appendStreamingToken: (stepType, token) =>
    set((state) => ({
      streamingOutput: {
        ...state.streamingOutput,
        [stepType]: (state.streamingOutput[stepType] || "") + token,
      },
    })),
  clearStreaming: (stepType) =>
    set((state) => ({
      streamingOutput: { ...state.streamingOutput, [stepType]: "" },
    })),
  setIsRunning: (running) => set({ isRunning: running }),
  reset: () => set({ activeProjectId: null, steps: [], streamingOutput: {}, isRunning: false }),
}));
```

**File:** `frontend/src/stores/editor-store.ts`

```typescript
interface EditorStore {
  content: string;
  versionNumber: number;
  isDirty: boolean;
  isSaving: boolean;

  setContent: (content: string) => void;
  setVersionNumber: (n: number) => void;
  setIsSaving: (saving: boolean) => void;
  markClean: () => void;
  reset: () => void;
}

const useEditorStore = create<EditorStore>((set) => ({
  content: "",
  versionNumber: 1,
  isDirty: false,
  isSaving: false,

  setContent: (content) => set({ content, isDirty: true }),
  setVersionNumber: (n) => set({ versionNumber: n }),
  setIsSaving: (saving) => set({ isSaving: saving }),
  markClean: () => set({ isDirty: false }),
  reset: () => set({ content: "", versionNumber: 1, isDirty: false, isSaving: false }),
}));
```

**File:** `frontend/src/stores/notebooklm-store.ts`

```typescript
interface NotebookLMStore {
  connectedNotebook: { id: string; title: string } | null;
  stepContexts: Record<string, string>;
  isQuerying: boolean;

  setConnectedNotebook: (notebook: { id: string; title: string } | null) => void;
  setStepContext: (stepType: string, context: string) => void;
  clearStepContext: (stepType: string) => void;
  setIsQuerying: (querying: boolean) => void;
  reset: () => void;
}

const useNotebookLMStore = create<NotebookLMStore>((set) => ({
  connectedNotebook: null,
  stepContexts: {},
  isQuerying: false,

  setConnectedNotebook: (notebook) => set({ connectedNotebook: notebook }),
  setStepContext: (stepType, context) =>
    set((state) => ({
      stepContexts: { ...state.stepContexts, [stepType]: context },
    })),
  clearStepContext: (stepType) =>
    set((state) => {
      const { [stepType]: _, ...rest } = state.stepContexts;
      return { stepContexts: rest };
    }),
  setIsQuerying: (querying) => set({ isQuerying: querying }),
  reset: () => set({ connectedNotebook: null, stepContexts: {}, isQuerying: false }),
}));
```

---

## Class & Object Design

### Backend: Complete Class Hierarchy

```
ScriptsWriterError
├── AgentExecutionError
├── AllProvidersFailedError
├── RateLimitExhaustedError
├── InvalidStateTransitionError
├── DependencyNotMetError
├── LLMOutputValidationError
└── ExportError

BaseAgent[InputT, OutputT] (ABC, Generic)
├── ICPAgent[ICPAgentInput, ICPAgentOutput]
├── HookAgent[HookAgentInput, HookAgentOutput]
├── NarrativeAgent[NarrativeAgentInput, NarrativeAgentOutput]
├── RetentionAgent[RetentionAgentInput, RetentionAgentOutput]
├── CTAAgent[CTAAgentInput, CTAAgentOutput]
├── WriterAgent[WriterAgentInput, WriterAgentOutput]
├── FactCheckAgent[FactCheckAgentInput, FactCheckAgentOutput]
├── ReadabilityAgent[ReadabilityAgentInput, ReadabilityAgentOutput]
├── CopyrightAgent[CopyrightAgentInput, CopyrightAgentOutput]
└── PolicyAgent[PolicyAgentInput, PolicyAgentOutput]

LLMProvider (ABC)
├── ModalProvider
├── GroqProvider
├── GeminiProvider
└── OllamaProvider

ProviderFactory
LLMCache
PipelineOrchestrator
PipelineState

ProjectService
PipelineService
AnalysisService
ExportService

Settings (pydantic-settings)
```

### Backend: Pydantic Agent Input/Output Models

#### ICP Agent

```python
class ICPDemographics(BaseModel):
    age_range: str = ""
    gender: str = ""
    location: str = ""
    occupation: list[str] = []
    income: str = ""

class ICPPsychographics(BaseModel):
    values: list[str] = []
    interests: list[str] = []
    attitudes: list[str] = []
    lifestyle: list[str] = []

class ICPProfile(BaseModel):
    demographics: ICPDemographics
    psychographics: ICPPsychographics
    pain_points: list[str] = []
    desires: list[str] = []
    objections: list[str] = []
    language_style: str = "professional"

class ICPAgentInput(BaseModel):
    raw_notes: str
    topic: str
    target_format: str
    content_goal: str | None = None
    notebooklm_context: str | None = None

class ICPAgentOutput(BaseModel):
    icp: ICPProfile
    confidence: float = Field(ge=0, le=1)
    suggestions: list[str] = []
```

#### Hook Agent

```python
class HookSuggestion(BaseModel):
    rank: int = Field(ge=1)
    text: str
    rationale: str = ""
    effectiveness_score: float = Field(ge=0, le=1, default=0.5)

class HookAgentInput(BaseModel):
    icp: ICPProfile
    topic: str
    target_format: str
    content_goal: str | None = None
    notebooklm_context: str | None = None

    def icp_summary(self) -> str:
        return f"Audience: {self.icp.demographics.age_range}, {', '.join(self.icp.demographics.occupation)}. Pain points: {', '.join(self.icp.pain_points[:3])}. Desires: {', '.join(self.icp.desires[:3])}."

class HookAgentOutput(BaseModel):
    suggestions: list[HookSuggestion] = Field(min_length=5)
```

#### Narrative Agent

```python
class NarrativePattern(BaseModel):
    name: str
    description: str
    fit_score: float = Field(ge=0, le=1, default=0.5)
    is_recommended: bool = False
    application_notes: str = ""

class NarrativeAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: str
    topic: str
    target_format: str
    content_goal: str | None = None
    notebooklm_context: str | None = None

    def icp_summary(self) -> str:
        return f"Audience: {self.icp.demographics.age_range}. Pain: {', '.join(self.icp.pain_points[:3])}."

class NarrativeAgentOutput(BaseModel):
    patterns: list[NarrativePattern] = Field(min_length=4)
    recommended_index: int = Field(ge=0)
```

#### Retention Agent

```python
class RetentionTechnique(BaseModel):
    name: str
    description: str
    placement: str = ""
    fit_for_format: list[str] = []

class RetentionAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: str
    selected_narrative: str
    target_format: str
    notebooklm_context: str | None = None

class RetentionAgentOutput(BaseModel):
    techniques: list[RetentionTechnique] = Field(min_length=3)
```

#### CTA Agent

```python
class CTASuggestion(BaseModel):
    cta_type: str
    suggested_wording: str
    rationale: str = ""
    placement_options: list[str] = []

class CTAAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: str
    selected_narrative: str
    content_goal: str | None = None
    notebooklm_context: str | None = None

class CTAAgentOutput(BaseModel):
    suggestions: list[CTASuggestion] = Field(min_length=2)
```

#### Writer Agent

```python
class ScriptDraft(BaseModel):
    content: str
    format: str
    structural_cues: list[str] = []
    word_count: int = 0

class WriterAgentInput(BaseModel):
    icp: ICPProfile
    selected_hook: str
    selected_narrative: str
    selected_retention: list[RetentionTechnique]
    selected_cta: str
    target_format: str
    topic: str
    raw_notes: str
    notebooklm_context: str | None = None

class WriterAgentOutput(BaseModel):
    script: ScriptDraft
```

#### Analysis Agents

```python
class Finding(BaseModel):
    type: str
    severity: str = Field(pattern="^(low|medium|high)$")
    text: str
    suggestion: str = ""
    confidence: str = Field(pattern="^(low|medium|high)$", default="medium")

class FactCheckAgentInput(BaseModel):
    script_content: str

class FactCheckAgentOutput(BaseModel):
    findings: list[Finding] = []
    claims_identified: int = 0
    claims_flagged: int = 0

class ReadabilityAgentInput(BaseModel):
    script_content: str
    target_grade: int = 8

class ReadabilityAgentOutput(BaseModel):
    findings: list[Finding] = []
    flesch_kincaid_score: float = 0
    gunning_fog_score: float = 0
    complex_sentence_count: int = 0

class CopyrightAgentInput(BaseModel):
    script_content: str

class CopyrightAgentOutput(BaseModel):
    findings: list[Finding] = []
    risk_level: str = Field(pattern="^(low|medium|high)$", default="low")

class PolicyAgentInput(BaseModel):
    script_content: str
    target_platforms: list[str] = []

class PolicyAgentOutput(BaseModel):
    findings: list[Finding] = []
    platforms_checked: list[str] = []
```

### Backend: Settings Model

```python
class AppSettings(BaseSettings):
    modal_api_key: str = ""
    modal_base_url: str = "https://api.us-west-2.modal.direct/v1"
    groq_api_key: str = ""
    gemini_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_enabled: bool = False
    database_url: str = "sqlite+aiosqlite:///./data/scripts_writer.db"
    export_dir: str = "./data/exports"
    log_level: str = "INFO"
    cache_max_size: int = 128
    cache_ttl_seconds: int = 3600
    max_retries: int = 3
    debounce_save_ms: int = 500

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

---

## Database Schema – Physical Design

### Final Table Definitions

```sql
-- Projects: core entity for each script pipeline
CREATE TABLE projects (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    topic           VARCHAR(200) NOT NULL,
    target_format   VARCHAR(20)  NOT NULL
                    CHECK (target_format IN ('VSL','YouTube','Tutorial','Facebook','LinkedIn','Blog')),
    content_goal    VARCHAR(20)
                    CHECK (content_goal IN ('Sell','Educate','Entertain','Build Authority')),
    raw_notes       TEXT         NOT NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','in_progress','completed')),
    current_step    INTEGER      NOT NULL DEFAULT 0,
    notebooklm_notebook_id VARCHAR(100) NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_updated_at ON projects(updated_at DESC);

-- ICP Profiles: one per project
CREATE TABLE icp_profiles (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID        NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    demographics    JSONB       NOT NULL DEFAULT '{}'::jsonb,
    psychographics  JSONB       NOT NULL DEFAULT '{}'::jsonb,
    pain_points     JSONB       NOT NULL DEFAULT '[]'::jsonb,
    desires         JSONB       NOT NULL DEFAULT '[]'::jsonb,
    objections      JSONB       NOT NULL DEFAULT '[]'::jsonb,
    language_style  VARCHAR(50)  NOT NULL DEFAULT 'professional',
    source          VARCHAR(20)  NOT NULL DEFAULT 'generated'
                    CHECK (source IN ('generated','uploaded','notebooklm')),
    approved        BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Pipeline Steps: tracks each agent execution
CREATE TABLE pipeline_steps (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    step_type       VARCHAR(30) NOT NULL
                    CHECK (step_type IN ('icp','hook','narrative','retention','cta',
                                         'writer','factcheck','readability','copyright','policy')),
    step_order      INTEGER     NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','running','completed','failed')),
    input_data      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    output_data     JSONB,
    selected_option JSONB,
    llm_provider    VARCHAR(20),
    token_count     INTEGER,
    duration_ms     INTEGER,
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    CONSTRAINT uq_project_step_type UNIQUE (project_id, step_type, step_order)
);

CREATE INDEX idx_pipeline_steps_project_order ON pipeline_steps(project_id, step_order);
CREATE INDEX idx_pipeline_steps_status ON pipeline_steps(project_id, status);

-- Script Versions: versioned script content
CREATE TABLE script_versions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_number      INTEGER     NOT NULL,
    content             TEXT        NOT NULL,
    format              VARCHAR(20) NOT NULL,
    hook_text           TEXT,
    narrative_pattern   VARCHAR(50),
    retention_techniques JSONB,
    cta_text            TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_project_version UNIQUE (project_id, version_number)
);

CREATE INDEX idx_script_versions_project ON script_versions(project_id, version_number DESC);

-- Analysis Results: per script version per agent type
CREATE TABLE analysis_results (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    script_version_id   UUID        NOT NULL REFERENCES script_versions(id) ON DELETE CASCADE,
    agent_type          VARCHAR(20) NOT NULL
                        CHECK (agent_type IN ('factcheck','readability','copyright','policy')),
    findings            JSONB       NOT NULL DEFAULT '[]'::jsonb,
    overall_score       FLOAT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_analysis_version_agent UNIQUE (project_id, script_version_id, agent_type)
);

CREATE INDEX idx_analysis_results_project ON analysis_results(project_id);
CREATE INDEX idx_analysis_results_version ON analysis_results(script_version_id);
```

### Schema Notes

| Decision | Rationale |
|----------|-----------|
| JSONB for structured agent data | Flexible schema for agent outputs that may evolve; queryable in SQLite as JSON |
| UUID primary keys | Globally unique; safe for future distributed scenarios |
| TIMESTAMPTZ | Timezone-aware timestamps for correctness |
| CASCADE deletes | Project deletion removes all related data; no orphaned records |
| UNIQUE constraint on (project_id, step_type, step_order) | Prevents duplicate steps; allows re-runs as new step_order entries |
| CHECK constraints | Enforce enum values at DB level as defense-in-depth alongside Pydantic |

---

## Detailed Logic & Algorithms

### Pipeline Orchestrator: Step Input Assembly

```python
async def _build_agent_inputs(self, project_id: UUID, step_type: StepType) -> BaseModel:
    project = await self._get_project(project_id)
    steps = await self._get_all_steps(project_id)
    step_map = {s.step_type: s for s in steps}
    notebooklm_context = await self._get_notebooklm_context(project) if project.notebooklm_notebook_id else None

    match step_type:
        case StepType.ICP:
            return ICPAgentInput(
                raw_notes=project.raw_notes,
                topic=project.topic,
                target_format=project.target_format,
                content_goal=project.content_goal,
                notebooklm_context=notebooklm_context,
            )
        case StepType.HOOK:
            icp = ICPProfile.model_validate(step_map[StepType.ICP].selected_option or step_map[StepType.ICP].output_data)
            return HookAgentInput(icp=icp, topic=project.topic, target_format=project.target_format, content_goal=project.content_goal, notebooklm_context=notebooklm_context)
        case StepType.NARRATIVE:
            icp = self._extract_icp(step_map)
            hook = step_map[StepType.HOOK].selected_option["hook_text"]
            return NarrativeAgentInput(icp=icp, selected_hook=hook, topic=project.topic, target_format=project.target_format, content_goal=project.content_goal, notebooklm_context=notebooklm_context)
        case StepType.RETENTION:
            icp = self._extract_icp(step_map)
            hook = step_map[StepType.HOOK].selected_option["hook_text"]
            narrative = step_map[StepType.NARRATIVE].selected_option["pattern"]
            return RetentionAgentInput(icp=icp, selected_hook=hook, selected_narrative=narrative, target_format=project.target_format, notebooklm_context=notebooklm_context)
        case StepType.CTA:
            icp = self._extract_icp(step_map)
            hook = step_map[StepType.HOOK].selected_option["hook_text"]
            narrative = step_map[StepType.NARRATIVE].selected_option["pattern"]
            return CTAAgentInput(icp=icp, selected_hook=hook, selected_narrative=narrative, content_goal=project.content_goal, notebooklm_context=notebooklm_context)
        case StepType.WRITER:
            icp = self._extract_icp(step_map)
            hook = step_map[StepType.HOOK].selected_option["hook_text"]
            narrative = step_map[StepType.NARRATIVE].selected_option["pattern"]
            retention = [RetentionTechnique(**t) for t in step_map[StepType.RETENTION].selected_option["techniques"]]
            cta = step_map[StepType.CTA].selected_option["cta_text"]
            return WriterAgentInput(icp=icp, selected_hook=hook, selected_narrative=narrative, selected_retention=retention, selected_cta=cta, target_format=project.target_format, topic=project.topic, raw_notes=project.raw_notes, notebooklm_context=notebooklm_context)
        case StepType.FACTCHECK | StepType.READABILITY | StepType.COPYRIGHT | StepType.POLICY:
            latest_script = await self._get_latest_script(project_id)
            input_cls = self._get_analysis_input_class(step_type)
            return input_cls(script_content=latest_script.content)
```

### Pipeline Orchestrator: Invalidating Downstream Steps

```python
async def _invalidate_downstream(self, project_id: UUID, from_step: StepType) -> None:
    downstream = self._get_downstream_steps(from_step)
    steps = await self._get_all_steps(project_id)
    for step in steps:
        if step.step_type in downstream and step.status == StepStatus.COMPLETED:
            step.status = StepStatus.PENDING
            step.selected_option = None
            step.output_data = None
            # Log warning
            logger.warning("invalidating_downstream_step", step_type=step.step_type, project_id=str(project_id))
    await self.db.commit()

def _get_downstream_steps(self, step_type: StepType) -> set[StepType]:
    step_index = self.STEP_ORDER.index(step_type)
    return set(self.STEP_ORDER[step_index + 1:])
```

### Export Service: File Generation

```python
class ExportService:
    def __init__(self, db: AsyncSession, export_dir: str):
        self.db = db
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_txt(self, project_id: UUID, version_id: UUID) -> Path:
        version = await self._get_version(version_id)
        project = await self._get_project(project_id)
        filename = f"{self._slugify(project.name)}-v{version.version_number}.txt"
        filepath = self.export_dir / filename
        async with aiofiles.open(filepath, "w") as f:
            await f.write(version.content)
        return filepath

    async def export_md(self, project_id: UUID, version_id: UUID) -> Path:
        version = await self._get_version(version_id)
        project = await self._get_project(project_id)
        filename = f"{self._slugify(project.name)}-v{version.version_number}.md"
        filepath = self.export_dir / filename
        md_content = self._format_as_markdown(project, version)
        async with aiofiles.open(filepath, "w") as f:
            await f.write(md_content)
        return filepath

    def _format_as_markdown(self, project, version) -> str:
        lines = [
            f"# {project.name}",
            f"",
            f"**Format:** {version.format}  ",
            f"**Topic:** {project.topic}  ",
        ]
        if version.hook_text:
            lines.append(f"**Hook:** {version.hook_text}  ")
        if version.narrative_pattern:
            lines.append(f"**Narrative:** {version.narrative_pattern}  ")
        if version.cta_text:
            lines.append(f"**CTA:** {version.cta_text}  ")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(version.content)
        return "\n".join(lines)

    @staticmethod
    def _slugify(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
```

### LLM Cache

```python
class LLMCache:
    def __init__(self, max_size: int = 128, ttl_seconds: int = 3600):
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def _make_key(self, prompt: str, system_prompt: str, model: str) -> str:
        raw = f"{model}:{system_prompt}:{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, prompt: str, system_prompt: str, model: str) -> str | None:
        key = self._make_key(prompt, system_prompt, model)
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                self._cache.move_to_end(key)
                return value
            del self._cache[key]
        return None

    async def set(self, prompt: str, system_prompt: str, model: str, value: str) -> None:
        key = self._make_key(prompt, system_prompt, model)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, time.time())
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
```

---

## Sequence Diagrams

### User Editing ICP and Continuing to Hook

```
User         ICPPanel       PipelineStore     API            PipelineService    DB
  │              │               │             │                  │              │
  │  Edit ICP   │               │             │                  │              │
  │─────────────>│               │             │                  │              │
  │              │  (local state │             │                  │              │
  │              │   only)       │             │                  │              │
  │              │               │             │                  │              │
  │  Approve    │               │             │                  │              │
  │─────────────>│               │             │                  │              │
  │              │ PATCH /pipeline/{step_id}   │                  │              │
  │              │──────────────>│             │                  │              │
  │              │               │─────────────>│                  │              │
  │              │               │             │ save selection   │              │
  │              │               │             │─────────────────>│              │
  │              │               │             │                  │ UPDATE step │
  │              │               │             │                  │─────────────>│
  │              │               │             │ 200 {step}       │              │
  │              │               │◄────────────│◄─────────────────│              │
  │              │ Update steps   │             │                  │              │
  │              │◄──────────────│             │                  │              │
  │              │               │             │                  │              │
  │  Navigate   │               │             │                  │              │
  │  to Hook    │               │             │                  │              │
  │─────────────>│               │             │                  │              │
  │              │ POST /pipeline/run/hook      │                  │              │
  │              │──────────────>│             │                  │              │
  │              │               │─────────────>│ run_step(HOOK)   │              │
  │              │               │             │─────────────────>│              │
  │              │               │             │                  │ (agent runs) │
  │  <streaming>│               │             │                  │              │
  │◄─────────────│◄──────────────│◄──WS────────│◄─────────────────│              │
```

### Script Version Save Flow

```
User       EditorStore      ScriptEditor      API          ScriptService       DB
  │             │                │              │                │              │
  │  Type text  │                │              │                │              │
  │────────────>│                │              │                │              │
  │             │ setContent()   │              │                │              │
  │             │ isDirty = true │              │                │              │
  │             │ 500ms debounce │              │                │              │
  │             │────timer──────>│              │                │              │
  │             │                │ PATCH        │                │              │
  │             │                │ /scripts/{v} │                │              │
  │             │                │─────────────>│                │              │
  │             │                │              │ update content  │              │
  │             │                │              │───────────────>│              │
  │             │                │              │                │ UPDATE       │
  │             │                │              │                │─────────────>│
  │             │                │              │ 200 {version}  │              │
  │             │                │              │◄───────────────│              │
  │             │                │ 200          │                │              │
  │             │                │◄─────────────│                │              │
  │             │ markClean()    │              │                │              │
  │             │ isDirty=false  │              │                │              │
```

### Branch Project Flow

```
User       PipelineView       API          PipelineService       DB
  │             │              │                │                │
  │  Click      │              │                │                │
  │  "Branch"   │              │                │                │
  │────────────>│              │                │                │
  │             │ POST         │                │                │
  │             │ /projects/{id}/branch         │                │
  │             │─────────────>│                │                │
  │             │              │ branch_project()│                │
  │             │              │───────────────>│                │
  │             │              │                │ BEGIN TX       │                │
  │             │              │                │──────────────────────────────>│
  │             │              │                │ COPY project   │                │
  │             │              │                │──────────────────────────────>│
  │             │              │                │ COPY steps     │                │
  │             │              │                │  (up to step N)│               │
  │             │              │                │──────────────────────────────>│
  │             │              │                │ COMMIT         │                │
  │             │              │                │──────────────────────────────>│
  │             │              │ 201 {new_proj} │                │
  │             │              │◄───────────────│                │
  │  Navigate   │              │                │                │
  │  to branch  │              │                │                │
  │◄────────────│              │                │                │
```

---

## API Interface Definitions

### Complete API Signature Reference

#### Projects

```python
# POST /api/v1/projects
async def create_project(body: ProjectCreateRequest) -> ProjectResponse:
    """
    Request:  ProjectCreateRequest(name, topic, target_format, content_goal?, raw_notes)
    Response: ProjectResponse(id, name, topic, target_format, content_goal, status, current_step, created_at, updated_at)
    Errors:   422 validation error
    """

# GET /api/v1/projects
async def list_projects(skip: int = 0, limit: int = 50) -> list[ProjectSummaryResponse]:
    """
    Response: [{id, name, target_format, status, updated_at}]
    """

# GET /api/v1/projects/{project_id}
async def get_project(project_id: UUID) -> ProjectDetailResponse:
    """
    Response: ProjectDetailResponse(+ raw_notes, content_goal, current_step, icp?, latest_script_version?)
    Errors:   404 project not found
    """

# PATCH /api/v1/projects/{project_id}
async def update_project(project_id: UUID, body: ProjectUpdateRequest) -> ProjectResponse:
    """
    Request:  ProjectUpdateRequest(name?, topic?, raw_notes?, content_goal?)
    Response: ProjectResponse
    Errors:   404, 422
    """

# DELETE /api/v1/projects/{project_id}
async def delete_project(project_id: UUID) -> None:
    """
    Errors: 404
    """
```

#### Pipeline

```python
# GET /api/v1/projects/{project_id}/pipeline
async def get_pipeline(project_id: UUID) -> PipelineResponse:
    """
    Response: { project_id, current_step, steps: [PipelineStepResponse] }
    PipelineStepResponse: { id, step_type, step_order, status, output_data?, selected_option?, duration_ms?, error_message? }
    """

# POST /api/v1/projects/{project_id}/pipeline/run/{step_type}
async def run_step(project_id: UUID, step_type: StepType) -> PipelineStepResponse:
    """
    Side effects: WebSocket events emitted (agent_start, agent_progress, agent_complete)
    Response: PipelineStepResponse (with output_data populated)
    Errors: 404 project not found, 409 dependency not met, 502 all providers failed
    """

# POST /api/v1/projects/{project_id}/pipeline/run-all
async def run_all_creative(project_id: UUID) -> list[PipelineStepResponse]:
    """
    Runs ICP → Hook → Narrative → Retention → CTA → Writer sequentially.
    Pauses at each step requiring user selection.
    Returns results of all completed steps.
    Errors: 404, 502
    """

# PATCH /api/v1/projects/{project_id}/pipeline/{step_id}
async def update_step(project_id: UUID, step_id: UUID, body: StepUpdateRequest) -> PipelineStepResponse:
    """
    Request:  StepUpdateRequest(selected_option: dict)
    Side effects: Invalidates downstream steps if re-selecting a completed step
    Response: PipelineStepResponse
    Errors: 404, 409 step not in completed state, 422 invalid selection
    """

# POST /api/v1/projects/{project_id}/pipeline/branch
async def branch_project(project_id: UUID, body: BranchRequest) -> ProjectResponse:
    """
    Request:  BranchRequest(from_step: StepType)
    Response: ProjectResponse (new project copy with steps up to from_step)
    Errors: 404
    """
```

#### ICP

```python
# GET /api/v1/projects/{project_id}/icp
async def get_icp(project_id: UUID) -> ICPProfileResponse:
    """
    Response: ICPProfileResponse(demographics, psychographics, pain_points, desires, objections, language_style, source, approved)
    Errors: 404 (no ICP generated yet)
    """

# POST /api/v1/projects/{project_id}/icp/generate
async def generate_icp(project_id: UUID) -> ICPProfileResponse:
    """
    Response: ICPProfileResponse (generated, not yet approved)
    Errors: 404, 502
    """

# PATCH /api/v1/projects/{project_id}/icp
async def update_icp(project_id: UUID, body: ICPUpdateRequest) -> ICPProfileResponse:
    """
    Request:  ICPUpdateRequest(demographics?, psychographics?, ..., approved?)
    Response: ICPProfileResponse
    """

# POST /api/v1/projects/{project_id}/icp/upload
async def upload_icp(project_id: UUID, file: UploadFile) -> ICPProfileResponse:
    """
    Request:  Multipart file upload (.txt or .json)
    Response: ICPProfileResponse (source="uploaded")
    Errors: 422 file format invalid
    """
```

#### Scripts

```python
# GET /api/v1/projects/{project_id}/scripts
async def list_scripts(project_id: UUID) -> list[ScriptVersionSummary]:
    """
    Response: [{id, version_number, format, created_at}]
    """

# GET /api/v1/projects/{project_id}/scripts/{version_id}
async def get_script(project_id: UUID, version_id: UUID) -> ScriptVersionResponse:
    """
    Response: ScriptVersionResponse(id, version_number, content, format, hook_text, narrative_pattern, retention_techniques, cta_text, created_at)
    """

# POST /api/v1/projects/{project_id}/scripts/generate
async def generate_script(project_id: UUID) -> ScriptVersionResponse:
    """
    Response: New ScriptVersionResponse (version_number incremented)
    Errors: 409 pipeline not complete through CTA step
    """

# PATCH /api/v1/projects/{project_id}/scripts/{version_id}
async def update_script(project_id: UUID, version_id: UUID, body: ScriptUpdateRequest) -> ScriptVersionResponse:
    """
    Request:  ScriptUpdateRequest(content?)
    Response: ScriptVersionResponse
    """
```

#### Analysis

```python
# POST /api/v1/projects/{project_id}/analyze/{agent_type}
async def run_analysis(project_id: UUID, agent_type: AnalysisAgentType) -> AnalysisResultResponse:
    """
    agent_type: factcheck | readability | copyright | policy
    Response: AnalysisResultResponse(agent_type, findings, overall_score)
    Errors: 404, 409 no script version available, 502
    """

# POST /api/v1/projects/{project_id}/analyze/all
async def run_all_analysis(project_id: UUID) -> list[AnalysisResultResponse]:
    """
    Runs factcheck + readability + copyright + policy in parallel.
    Response: [AnalysisResultResponse x4]
    """

# GET /api/v1/projects/{project_id}/analysis
async def get_analysis(project_id: UUID, version_id: UUID | None = None) -> list[AnalysisResultResponse]:
    """
    version_id: optional, defaults to latest version
    Response: [AnalysisResultResponse]
    """
```

#### Export

```python
# GET /api/v1/projects/{project_id}/export?format=txt|md
async def export_script(project_id: UUID, format: Literal["txt", "md"], version_id: UUID | None = None) -> StreamingResponse:
    """
    Response: File download (text/plain or text/markdown)
    Errors: 404, 409 no script version
    """

# POST /api/v1/projects/{project_id}/export/clipboard
async def copy_to_clipboard(project_id: UUID, version_id: UUID | None = None) -> ClipboardResponse:
    """
    Response: { success: true, content: "..." }
    Note: Server-side clipboard not practical; frontend should handle clipboard via JS
    """
```

#### Settings

```python
# GET /api/v1/settings/llm
async def get_llm_settings() -> LLMSettingsResponse:
    """
    Response: LLMSettingsResponse(providers: [{name, enabled, priority}], api_keys_masked: {modal: "****nyTp", ...})
    """

# PATCH /api/v1/settings/llm
async def update_llm_settings(body: LLMSettingsUpdateRequest) -> LLMSettingsResponse:
    """
    Request:  LLMSettingsUpdateRequest(modal_api_key?, groq_api_key?, gemini_api_key?, ollama_enabled?, provider_priority?: [str])
    """

# GET /api/v1/settings/llm/status
async def get_llm_status() -> LLMStatusResponse:
    """
    Response: { providers: [{name: "modal", reachable: true}, {name: "groq", reachable: false}, ...] }
    """
```

#### NotebookLM

```python
# GET /api/v1/projects/{project_id}/notebooklm/notebooks
async def list_notebooks(project_id: UUID) -> list[NotebookSummary]:
    """
    Response: [{id: "notebook-uuid", title: "Audience Research"}]
    Errors: 404 project not found, 502 Google API unavailable
    """

# POST /api/v1/projects/{project_id}/notebooklm/connect
async def connect_notebook(project_id: UUID, body: ConnectNotebookRequest) -> ConnectNotebookResponse:
    """
    Request:  ConnectNotebookRequest(notebook_id: str)
    Response: ConnectNotebookResponse(id, title, connected_at)
    Side effects: Stores notebook_id on project; queries notebook for validation
    Errors: 404, 422 invalid notebook_id, 502 Google API unavailable
    """

# DELETE /api/v1/projects/{project_id}/notebooklm/connect
async def disconnect_notebook(project_id: UUID) -> None:
    """
    Side effects: Removes notebook_id from project; clears stored step contexts
    Errors: 404
    """

# POST /api/v1/projects/{project_id}/notebooklm/query
async def query_notebook(project_id: UUID, body: NotebookQueryRequest) -> NotebookQueryResponse:
    """
    Request:  NotebookQueryRequest(query: str, step_type: str)
    Response: NotebookQueryResponse(context: str)
    Errors: 404, 409 no notebook connected, 502 Google API unavailable
    """
```

---

## State Management & Data Persistence

### Server-Side State Machine: Pipeline Step

```
                    ┌─────────┐
          ┌────────►│ PENDING │◄──────────┐
          │         └────┬────┘            │
          │              │ run_step()       │
          │              ▼                  │
          │         ┌─────────┐            │
          │         │ RUNNING │──────────────┤
          │         └────┬────┘  timeout/   │
          │              │       error      │
          │    ┌─────────┴─────────┐        │
          │    │                   │        │
          │    ▼                   ▼        │
          │ ┌──────────┐    ┌──────────┐   │
          │ │COMPLETED │    │  FAILED  │───┘
          │ └────┬─────┘    └──────────┘
          │      │
          │      │ re-run (user action)
          └──────┘
```

### Server-Side State Machine: Project

```
 ┌────────┐   first agent run   ┌─────────────┐   all steps completed   ┌───────────┐
 │ DRAFT  │───────────────────►│IN_PROGRESS  │────────────────────────►│ COMPLETED │
 └────────┘                    └─────────────┘                          └───────────┘
```

### Client-Side State Flow: Agent Interaction

```
[Idle] ──user clicks Run──► [Loading] ──WS: agent_start──► [Streaming]
                                                                  │
                                              WS: agent_progress │ (append tokens)
                                                                  │
                                              WS: agent_complete │
                                                                  ▼
                                                           [Review] ──user edits──► [Editing]
                                                                │                         │
                                                                │ user approves           │ user saves
                                                                ▼                         ▼
                                                           [Approved] ──navigate──► [Next Step]
```

### Persistence Points

| Event | What is Persisted | Where | When |
|-------|-------------------|-------|------|
| Project created | Project metadata + raw_notes | SQLite | Immediately |
| Agent starts | PipelineStep(status=RUNNING) | SQLite | Before LLM call |
| Agent streams tokens | Not persisted (ephemeral) | Frontend Zustand | Real-time via WS |
| Agent completes | PipelineStep(status=COMPLETED, output_data, token_count, duration_ms) | SQLite | After LLM response |
| User makes selection | PipelineStep(selected_option) | SQLite | On PATCH request |
| User edits ICP | ICPProfile fields | SQLite | On PATCH request |
| User edits script | ScriptVersion.content | SQLite | Debounced 500ms PATCH |
| Analysis completes | AnalysisResult(findings, overall_score) | SQLite | After each agent |
| NotebookLM notebook connected | project.notebooklm_notebook_id | SQLite | On connect/disconnect |
| User exports | File on disk | Filesystem | On GET request |

---

## Unit Testing Strategy

### Backend Test Plan

#### Agent Tests

| Test ID | Module | Test Case | Input | Expected Output | Mock |
|---------|--------|-----------|-------|-----------------|------|
| T-AGT-01 | ICPAgent | Generate ICP from valid notes | ICPAgentInput(raw_notes="...", topic="Python") | ICPAgentOutput with non-empty ICPProfile | MockLLMProvider |
| T-AGT-02 | ICPAgent | Handles empty notes | ICPAgentInput(raw_notes="", topic="Python") | AgentExecutionError | MockLLMProvider |
| T-AGT-03 | HookAgent | Generate 5 hooks | HookAgentInput(icp=..., topic="...") | HookAgentOutput with 5+ suggestions | MockLLMProvider |
| T-AGT-04 | HookAgent | Ranks hooks by effectiveness | HookAgentInput(icp=...) | suggestions[0].effectiveness_score >= suggestions[4].effectiveness_score | MockLLMProvider |
| T-AGT-05 | NarrativeAgent | Recommends pattern based on goal | NarrativeAgentInput(content_goal="Sell") | recommended_index points to PAS or AIDA | MockLLMProvider |
| T-AGT-06 | WriterAgent | Includes all selections in output | WriterAgentInput with hook, narrative, CTA | ScriptDraft.content contains hook text | MockLLMProvider |
| T-AGT-07 | FactCheckAgent | Flags unverifiable claims | FactCheckAgentInput("Python is #1 language") | Finding with severity="medium", confidence="low" | MockLLMProvider |
| T-AGT-08 | ReadabilityAgent | Computes FK score | ReadabilityAgentInput(complex text) | flesch_kincaid_score > 0 | MockLLMProvider |

#### LLM Provider Tests

| Test ID | Module | Test Case | Input | Expected Output | Mock |
|---------|--------|-----------|-------|-----------------|------|
| T-LLM-01 | ModalProvider | Successful generation | "test prompt" | Non-empty string response | Mock OpenAI client |
| T-LLM-02 | ModalProvider | Handles rate limit (429) | "test prompt" | RateLimitError raised | Mock 429 response |
| T-LLM-03 | ProviderFactory | Failover from Modal to Groq | "test prompt" | Response from GroqProvider | MockModal(fail), MockGroq(ok) |
| T-LLM-04 | ProviderFactory | All providers fail | "test prompt" | AllProvidersFailedError | Mock all providers to fail |
| T-LLM-05 | LLMCache | Cache hit on repeat request | Same prompt twice | Second call returns cached value | N/A |
| T-LLM-06 | LLMCache | Cache miss on different prompt | Different prompts | Two LLM calls | N/A |
| T-LLM-07 | LLMCache | Cache eviction at max_size | 129 unique prompts | First entry evicted | N/A |

#### Pipeline Tests

| Test ID | Module | Test Case | Input | Expected Output | Mock |
|---------|--------|-----------|-------|-----------------|------|
| T-PIP-01 | PipelineState | Valid transition: pending → running | (PENDING, RUNNING) | True | N/A |
| T-PIP-02 | PipelineState | Invalid transition: pending → completed | (PENDING, COMPLETED) | False | N/A |
| T-PIP-03 | PipelineState | Re-run: completed → running | (COMPLETED, RUNNING) | True | N/A |
| T-PIP-04 | PipelineState | Dependency check: hook requires ICP completed | ICP pending | DependencyNotMetError | N/A |
| T-PIP-05 | PipelineState | Dependency check: writer requires all creative steps | All creative steps completed | No error | N/A |
| T-PIP-06 | Orchestrator | Invalidation of downstream steps | Re-run ICP | Hook, Narrative, etc. reset to PENDING | MockDB |

#### API Tests

| Test ID | Module | Test Case | Input | Expected Output | Mock |
|---------|--------|-----------|-------|-----------------|------|
| T-API-01 | projects | Create project with valid data | POST {name, topic, format, notes} | 201 with project | Test DB |
| T-API-02 | projects | Create project with missing required field | POST {name only} | 422 validation error | Test DB |
| T-API-03 | pipeline | Run step with met dependencies | POST /pipeline/run/hook (ICP completed) | 200 with step result | MockAgent |
| T-API-04 | pipeline | Run step with unmet dependencies | POST /pipeline/run/hook (ICP pending) | 409 dependency not met | MockAgent |
| T-API-05 | pipeline | User selection saved | PATCH /pipeline/{id} {selected_option: {...}} | 200 with updated step | Test DB |
| T-API-06 | export | Export as markdown | GET /export?format=md | 200 text/markdown file | Test DB |
| T-API-07 | analysis | Run all analysis agents | POST /analyze/all | 200 with 4 analysis results | MockAgent |
| T-API-08 | notebooklm | Connect notebook to project | POST /notebooklm/connect | 200 with notebook details | Mock Google API |

#### Service Tests

| Test ID | Module | Test Case | Input | Expected Output | Mock |
|---------|--------|-----------|-------|-----------------|------|
| T-SVC-01 | ExportService | Slugify project name | "My VSL Script!" | "my-vsl-script" | N/A |
| T-SVC-02 | ExportService | Format as markdown | project + script version | Well-formed markdown string | N/A |
| T-SVC-03 | ProjectService | Delete project cascades | DELETE project with steps, ICP, scripts | All related records deleted | Test DB |

### Frontend Test Plan

| Test ID | Module | Test Case | Expected Behavior |
|---------|--------|-----------|-------------------|
| T-FE-01 | CreateProjectDialog | Submit valid form | Calls POST /projects, navigates to project |
| T-FE-02 | CreateProjectDialog | Submit with empty name | Shows validation error, no API call |
| T-FE-03 | PipelineView | Render steps with statuses | Completed steps show ✓, running shows spinner |
| T-FE-04 | ICPPanel | Approve ICP | Calls PATCH with approved=true, navigates to hook |
| T-FE-05 | HookPanel | Select a hook | Highlights selected hook, enables Continue button |
| T-FE-06 | HookPanel | Enter custom hook | Switches to custom mode, hides radio buttons |
| T-FE-07 | NarrativePanel | Click info icon | Shows/hides pattern description |
| T-FE-08 | RetentionPanel | Toggle technique | Checkbox toggles, technique added/removed from selection |
| T-FE-09 | ScriptEditor | Type content | EditorStore.isDirty becomes true, debounced save triggers |
| T-FE-10 | AnalysisPanel | Switch tabs | Active tab content renders, others hidden |
| T-FE-11 | useWebSocket | Receive agent_start | Clears streaming output for step_type |
| T-FE-12 | useWebSocket | Receive agent_progress | Appends token to streaming output |
| T-FE-13 | useAgentStream | Token accumulation | streamingOutput grows with each token |
| T-FE-14 | pipelineStore | setStepOutput | Updates step status to completed |
| T-FE-15 | editorStore | markClean | Sets isDirty to false |

### Test Fixtures

```python
# conftest.py

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()

@pytest.fixture
def mock_llm_provider():
    return MockLLMProvider(responses={
        "icp": ICPAgentOutput(icp=ICPProfile(demographics=ICPDemographics(age_range="25-45")), confidence=0.8),
        "hook": HookAgentOutput(suggestions=[HookSuggestion(rank=1, text="Test hook") for _ in range(5)]),
    })

@pytest.fixture
def sample_project_data():
    return {
        "name": "Test Project",
        "topic": "Python course",
        "target_format": "VSL",
        "content_goal": "Sell",
        "raw_notes": "I want to sell my Python course to developers",
    }
```

```typescript
// frontend test setup

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};
```

### Test Execution

```bash
# Backend
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing

# Frontend
cd frontend
npm run test -- --coverage

# Integration (requires running services)
pytest tests/integration/ -v --timeout=60
```
