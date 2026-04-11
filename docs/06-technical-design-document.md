# Technical Design Document – Scripts Writer

## System Component Breakdown

### Backend Package Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry, middleware, lifespan
│   ├── config.py                  # Pydantic Settings (env vars, API keys)
│   ├── db/
│   │   ├── database.py            # SQLAlchemy engine, session factory
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── migrations/           # Alembic migrations
│   ├── api/
│   │   ├── router.py             # Root router aggregation
│   │   ├── projects.py           # /api/v1/projects endpoints
│   │   ├── pipeline.py           # /api/v1/projects/{id}/pipeline endpoints
│   │   ├── icp.py                # /api/v1/projects/{id}/icp endpoints
│   │   ├── scripts.py            # /api/v1/projects/{id}/scripts endpoints
│   │   ├── analysis.py           # /api/v1/projects/{id}/analyze endpoints
│   │   ├── export.py            # /api/v1/projects/{id}/export endpoints
│   │   └── settings.py          # /api/v1/settings endpoints
│   ├── schemas/
│   │   ├── project.py           # Pydantic request/response schemas
│   │   ├── pipeline.py          # Pipeline step schemas
│   │   ├── icp.py               # ICP schemas
│   │   ├── script.py            # Script schemas
│   │   ├── analysis.py          # Analysis result schemas
│   │   └── settings.py          # Settings schemas
│   ├── agents/
│   │   ├── base.py              # BaseAgent abstract class
│   │   ├── icp_agent.py         # ICP Analysis Agent
│   │   ├── hook_agent.py        # Hook Suggestion Agent
│   │   ├── narrative_agent.py   # Narrative Pattern Agent
│   │   ├── retention_agent.py   # Retention Technique Agent
│   │   ├── cta_agent.py         # CTA Selection Agent
│   │   ├── writer_agent.py     # Script Generation Agent
│   │   ├── factcheck_agent.py  # Fact-Checking Agent
│   │   ├── readability_agent.py # Readability & Typo Agent
│   │   ├── copyright_agent.py  # Copyright Compliance Agent
│   │   └── policy_agent.py     # Platform Policy Agent
│   ├── llm/
│   │   ├── base.py              # LLMProvider abstract class
│   │   ├── modal_provider.py    # Modal (GLM-5.1) provider
│   │   ├── groq_provider.py     # Groq provider
│   │   ├── gemini_provider.py   # Google Gemini provider
│   │   ├── ollama_provider.py   # Ollama local provider
│   │   ├── provider_factory.py  # Provider factory + failover chain
│   │   └── cache.py            # LLM response LRU cache
│   ├── pipeline/
│   │   ├── orchestrator.py      # Pipeline execution orchestrator
│   │   └── state.py             # Pipeline state machine
│   ├── services/
│   │   ├── project_service.py   # Project CRUD business logic
│   │   ├── pipeline_service.py  # Pipeline execution business logic
│   │   ├── export_service.py    # Export file generation logic
│   │   └── analysis_service.py  # Analysis aggregation logic
│   └── ws/
│       └── handlers.py          # WebSocket connection & message handlers
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic.ini
├── pyproject.toml
└── Dockerfile
```

### Frontend Package Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Dashboard
│   │   ├── projects/
│   │   │   ├── page.tsx          # Project list
│   │   │   └── [id]/
│   │   │       ├── page.tsx      # Project pipeline view
│   │   │       └── editor/
│   │   │           └── page.tsx  # Script editor
│   │   └── settings/
│   │       └── page.tsx          # LLM settings
│   ├── components/
│   │   ├── ui/                   # Shadcn/UI primitives
│   │   ├── dashboard/
│   │   ├── pipeline/
│   │   │   ├── pipeline-view.tsx
│   │   │   ├── step-card.tsx
│   │   │   └── step-sidebar.tsx
│   │   ├── agents/
│   │   │   ├── agent-output-panel.tsx
│   │   │   ├── icp-panel.tsx
│   │   │   ├── hook-panel.tsx
│   │   │   ├── narrative-panel.tsx
│   │   │   ├── retention-panel.tsx
│   │   │   ├── cta-panel.tsx
│   │   │   └── analysis-panel.tsx
│   │   ├── editor/
│   │   │   └── script-editor.tsx
│   │   └── shared/
│   │       ├── loading-spinner.tsx
│   │       ├── error-boundary.tsx
│   │       └── streaming-text.tsx
│   ├── lib/
│   │   ├── api.ts                # API client (fetch wrapper)
│   │   ├── ws.ts                 # WebSocket client
│   │   └── utils.ts              # Utility functions
│   ├── hooks/
│   │   ├── use-pipeline.ts       # Pipeline state hook
│   │   ├── use-websocket.ts      # WebSocket connection hook
│   │   └── use-agent-stream.ts   # Agent streaming hook
│   ├── stores/
│   │   ├── project-store.ts      # Zustand project state
│   │   ├── pipeline-store.ts     # Zustand pipeline state
│   │   └── settings-store.ts     # Zustand settings state
│   └── types/
│       ├── project.ts
│       ├── pipeline.ts
│       ├── icp.ts
│       ├── script.ts
│       └── analysis.ts
├── tailwind.config.ts
├── next.config.ts
├── package.json
└── Dockerfile
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app/api/` | HTTP request handling, validation, response serialization |
| `app/agents/` | Individual agent logic — prompt construction, Pydantic AI agent definition, output parsing |
| `app/llm/` | LLM provider abstraction, failover chain, response caching |
| `app/pipeline/` | Orchestration of agent sequence, state transitions, branching |
| `app/services/` | Business logic layer between API and data/agents |
| `app/db/` | Database models, session management, migrations |
| `app/ws/` | WebSocket connection lifecycle and message routing |
| `frontend/src/stores/` | Client-side state management (Zustand) |
| `frontend/src/hooks/` | React hooks for API/WebSocket integration |
| `frontend/src/components/agents/` | Per-agent UI panels with selection/approval flows |

---

## Low-Level Design

### Class/Object Design

#### BaseAgent (Abstract)

```python
class BaseAgent(ABC, Generic[InputT, OutputT]):
    name: str
    step_type: StepType
    model_config: ModelConfig

    def __init__(self, llm_provider: LLMProvider, cache: LLMCache | None = None):
        self.llm_provider = llm_provider
        self.cache = cache
        self._agent = self._build_agent()

    @abstractmethod
    def _build_agent(self) -> pydantic_ai.Agent:
        """Define the Pydantic AI agent with system prompt and deps."""

    @abstractmethod
    def build_prompt(self, inputs: InputT) -> str:
        """Construct the user prompt from structured inputs."""

    async def execute(self, inputs: InputT, ws_handler: WSHandler | None = None) -> OutputT:
        """Run the agent with failover, caching, and streaming."""
        cache_key = self._compute_cache_key(inputs)
        if self.cache and (cached := await self.cache.get(cache_key)):
            return cached
        try:
            result = await self._run_with_failover(inputs, ws_handler)
            if self.cache:
                await self.cache.set(cache_key, result)
            return result
        except AllProvidersFailedError as e:
            raise AgentExecutionError(self.name, str(e))

    async def _run_with_failover(self, inputs: InputT, ws_handler: WSHandler | None) -> OutputT:
        """Try primary provider, failover to alternates."""

    def _compute_cache_key(self, inputs: InputT) -> str:
        """Hash inputs + model + provider for cache key."""
```

#### ICPAgent

```python
class ICPAgent(BaseAgent[ICPAgentInput, ICPAgentOutput]):
    name = "icp"
    step_type = StepType.ICP

    def _build_agent(self) -> pydantic_ai.Agent:
        return pydantic_ai.Agent(
            model=self.llm_provider.model_name,
            result_type=ICPAgentOutput,
            system_prompt=ICP_SYSTEM_PROMPT,
        )

    def build_prompt(self, inputs: ICPAgentInput) -> str:
        return f"""Analyze the following notes and create an Ideal Customer Profile.

Topic: {inputs.topic}
Content Format: {inputs.target_format}
Content Goal: {inputs.content_goal or 'not specified'}

Raw Notes:
{inputs.raw_notes}

Generate a detailed ICP including demographics, psychographics, pain points, desires, objections, and recommended language style."""
```

#### HookAgent

```python
class HookAgent(BaseAgent[HookAgentInput, HookAgentOutput]):
    name = "hook"
    step_type = StepType.HOOK

    def build_prompt(self, inputs: HookAgentInput) -> str:
        return f"""Based on the following ICP and topic, generate 5 compelling hooks for a {inputs.target_format}.

ICP:
{inputs.icp_summary()}

Topic: {inputs.topic}
Content Goal: {inputs.content_goal}

Each hook must:
1. Capture attention in the first 3-5 seconds
2. Be tailored to the ICP's pain points and desires
3. Create curiosity or urgency to continue

Rank hooks by predicted effectiveness for this specific ICP."""
```

#### NarrativeAgent

```python
class NarrativeAgent(BaseAgent[NarrativeAgentInput, NarrativeAgentOutput]):
    name = "narrative"
    step_type = StepType.NARRATIVE

    def build_prompt(self, inputs: NarrativeAgentInput) -> str:
        return f"""Based on the following context, recommend a narrative pattern for a {inputs.target_format}.

ICP: {inputs.icp_summary()}
Hook: {inputs.selected_hook}
Topic: {inputs.topic}
Content Goal: {inputs.content_goal}

Available patterns: PAS, AIDA, Story Loop, Before-After-Bridge, Problem-Solution-Benefit

For each pattern:
1. Explain how it applies to this specific content
2. Rate its fit for this ICP and format
3. Recommend the best choice with rationale"""
```

#### RetentionAgent, CTAAgent, WriterAgent — (same pattern, prompt-specific)

#### FactCheckAgent

```python
class FactCheckAgent(BaseAgent[FactCheckAgentInput, FactCheckAgentOutput]):
    name = "factcheck"
    step_type = StepType.FACTCHECK

    def build_prompt(self, inputs: FactCheckAgentInput) -> str:
        return f"""Analyze the following script for factual accuracy.

Script:
{inputs.script_content}

For each factual claim you identify:
1. Quote the exact claim
2. Assess verifiability (verifiable / unverifiable / questionable)
3. Provide confidence level (high / medium / low)
4. Suggest correction if applicable

Present findings as advisory — the user has final say."""
```

#### ReadabilityAgent, CopyrightAgent, PolicyAgent — (same pattern, prompt-specific)

---

#### LLMProvider (Abstract)

```python
class LLMProvider(ABC):
    provider_name: str
    model_name: str
    priority: int

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str, response_model: type[BaseModel] | None = None) -> str:
        """Generate completion. If response_model provided, use structured output."""

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        """Stream completion tokens."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is reachable."""

    def get_identifier(self) -> str:
        return f"{self.provider_name}:{self.model_name}"
```

#### ModalProvider

```python
class ModalProvider(LLMProvider):
    provider_name = "modal"
    model_name = "glm-5.1"

    def __init__(self, api_key: str, base_url: str = "https://api.us-west-2.modal.direct/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    async def generate(self, prompt: str, system_prompt: str, response_model: type[BaseModel] | None = None) -> str:
        kwargs = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }
        if response_model:
            kwargs["response_format"] = {"type": "json_object"}
        response = await asyncio.to_thread(self.client.chat.completions.create, **kwargs)
        return response.choices[0].message.content

    async def stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        stream = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def health_check(self) -> bool:
        try:
            await asyncio.to_thread(self.client.models.list)
            return True
        except Exception:
            return False
```

#### ProviderFactory

```python
class ProviderFactory:
    def __init__(self, config: LLMConfig):
        self._providers: list[LLMProvider] = []
        self._build_providers(config)

    def _build_providers(self, config: LLMConfig):
        if config.modal_api_key:
            self._providers.append(ModalProvider(config.modal_api_key, priority=0))
        if config.groq_api_key:
            self._providers.append(GroqProvider(config.groq_api_key, priority=1))
        if config.gemini_api_key:
            self._providers.append(GeminiProvider(config.gemini_api_key, priority=2))
        if config.ollama_enabled:
            self._providers.append(OllamaProvider(priority=3))
        self._providers.sort(key=lambda p: p.priority)

    async def get_provider(self) -> LLMProvider:
        for provider in self._providers:
            if await provider.health_check():
                return provider
        raise AllProvidersFailedError("No LLM provider available")

    async def execute_with_failover(self, prompt: str, system_prompt: str, response_model: type[BaseModel] | None = None) -> str:
        last_error: Exception | None = None
        for provider in self._providers:
            for attempt in range(3):
                try:
                    return await provider.generate(prompt, system_prompt, response_model)
                except RateLimitError:
                    await asyncio.sleep(2 ** attempt)
                    continue
                except (APIConnectionError, APIStatusError) as e:
                    last_error = e
                    break
        raise AllProvidersFailedError(str(last_error))
```

---

#### PipelineOrchestrator

```python
class PipelineOrchestrator:
    STEP_ORDER: list[StepType] = [
        StepType.ICP, StepType.HOOK, StepType.NARRATIVE,
        StepType.RETENTION, StepType.CTA, StepType.WRITER,
        StepType.FACTCHECK, StepType.READABILITY,
        StepType.COPYRIGHT, StepType.POLICY,
    ]

    ANALYSIS_STEPS: set[StepType] = {
        StepType.FACTCHECK, StepType.READABILITY,
        StepType.COPYRIGHT, StepType.POLICY,
    }

    def __init__(self, db: AsyncSession, provider_factory: ProviderFactory, cache: LLMCache):
        self.db = db
        self.provider_factory = provider_factory
        self.cache = cache
        self._agents: dict[StepType, BaseAgent] = self._init_agents()

    def _init_agents(self) -> dict[StepType, BaseAgent]:
        provider = asyncio.get_event_loop().run_until_complete(self.provider_factory.get_provider())
        return {
            StepType.ICP: ICPAgent(provider, self.cache),
            StepType.HOOK: HookAgent(provider, self.cache),
            StepType.NARRATIVE: NarrativeAgent(provider, self.cache),
            StepType.RETENTION: RetentionAgent(provider, self.cache),
            StepType.CTA: CTAAgent(provider, self.cache),
            StepType.WRITER: WriterAgent(provider, self.cache),
            StepType.FACTCHECK: FactCheckAgent(provider, self.cache),
            StepType.READABILITY: ReadabilityAgent(provider, self.cache),
            StepType.COPYRIGHT: CopyrightAgent(provider, self.cache),
            StepType.POLICY: PolicyAgent(provider, self.cache),
        }

    async def run_step(self, project_id: UUID, step_type: StepType, ws_handler: WSHandler | None = None) -> PipelineStep:
        step = await self._get_or_create_step(project_id, step_type)
        await self._update_step_status(step, StepStatus.RUNNING)
        try:
            agent = self._agents[step_type]
            inputs = await self._build_agent_inputs(project_id, step_type)
            output = await agent.execute(inputs, ws_handler)
            step.output_data = output.model_dump()
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            await self.db.commit()
            return step
        except AgentExecutionError as e:
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            await self.db.commit()
            raise

    async def run_analysis_parallel(self, project_id: UUID, ws_handler: WSHandler | None = None) -> list[PipelineStep]:
        tasks = [
            self.run_step(project_id, step_type, ws_handler)
            for step_type in self.ANALYSIS_STEPS
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def run_full_pipeline(self, project_id: UUID, ws_handler: WSHandler | None = None) -> list[PipelineStep]:
        results = []
        for step_type in self.STEP_ORDER:
            if step_type in self.ANALYSIS_STEPS:
                continue  # run analysis after writer
            result = await self.run_step(project_id, step_type, ws_handler)
            results.append(result)
            if step_type in {StepType.ICP, StepType.HOOK, StepType.NARRATIVE, StepType.RETENTION, StepType.CTA}:
                break  # pause for user selection
        return results

    async def _build_agent_inputs(self, project_id: UUID, step_type: StepType) -> BaseModel:
        """Assemble agent inputs from project context and previous step outputs."""
```

#### PipelineState

```python
class PipelineState:
    TRANSITIONS: dict[StepStatus, set[StepStatus]] = {
        StepStatus.PENDING: {StepStatus.RUNNING},
        StepStatus.RUNNING: {StepStatus.COMPLETED, StepStatus.FAILED},
        StepStatus.COMPLETED: {StepStatus.RUNNING},  # allow re-run
        StepStatus.FAILED: {StepStatus.RUNNING},      # allow retry
    }

    @classmethod
    def can_transition(cls, current: StepStatus, target: StepStatus) -> bool:
        return target in cls.TRANSITIONS.get(current, set())

    @classmethod
    def validate_step_ready(cls, step: PipelineStep, all_steps: list[PipelineStep]) -> None:
        if step.status not in {StepStatus.PENDING, StepStatus.FAILED}:
            raise InvalidStateTransitionError(f"Step {step.step_type} is {step.status}, cannot run")
        required = cls._get_dependencies(step.step_type)
        for dep in required:
            dep_step = next((s for s in all_steps if s.step_type == dep), None)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                raise DependencyNotMetError(f"Step {step.step_type} requires {dep} to be completed")
```

---

### Design Patterns

| Pattern | Where Used | Rationale |
|---------|-----------|-----------|
| **Strategy** | `LLMProvider` hierarchy | Interchangeable LLM providers with unified interface; new providers added without modifying agents |
| **Factory** | `ProviderFactory` | Centralizes provider instantiation and configuration; manages failover chain ordering |
| **Template Method** | `BaseAgent.execute()` | Defines the skeleton (cache check → failover run → cache write); subclasses override `build_prompt()` and `_build_agent()` |
| **Chain of Responsibility** | Provider failover chain | Each provider attempts the request; on failure, passes to next provider in chain |
| **Observer** | WebSocket event broadcasting | Pipeline orchestrator emits events (agent_start, agent_progress, agent_complete); WebSocket handler subscribes and pushes to clients |
| **Adapter** | Modal/Groq/Gemini/Ollama providers | Each wraps a different SDK behind the common `LLMProvider` interface |
| **Repository** | Service layer (`ProjectService`, `PipelineService`) | Encapsulates database access logic; keeps API handlers thin |
| **State Machine** | `PipelineState` | Enforces valid step transitions and dependency checks |

---

### Detailed Database Schema

```sql
CREATE TABLE projects (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    topic       VARCHAR(200) NOT NULL,
    target_format VARCHAR(20) NOT NULL CHECK (target_format IN ('VSL','YouTube','Tutorial','Facebook','LinkedIn','Blog')),
    content_goal  VARCHAR(20) CHECK (content_goal IN ('Sell','Educate','Entertain','Build Authority')),
    raw_notes   TEXT        NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','in_progress','completed')),
    current_step INTEGER    NOT NULL DEFAULT 0,
    created_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_updated ON projects(updated_at DESC);

CREATE TABLE icp_profiles (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID        NOT NULL UNIQUE REFERENCES projects(id) ON DELETE CASCADE,
    demographics    JSON        NOT NULL DEFAULT '{}',
    psychographics  JSON        NOT NULL DEFAULT '{}',
    pain_points     JSON        NOT NULL DEFAULT '[]',
    desires         JSON        NOT NULL DEFAULT '[]',
    objections      JSON        NOT NULL DEFAULT '[]',
    language_style  VARCHAR(50) NOT NULL DEFAULT 'professional',
    source          VARCHAR(20) NOT NULL DEFAULT 'generated' CHECK (source IN ('generated','uploaded')),
    approved        BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pipeline_steps (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    step_type       VARCHAR(30) NOT NULL CHECK (step_type IN ('icp','hook','narrative','retention','cta','writer','factcheck','readability','copyright','policy')),
    step_order      INTEGER     NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed')),
    input_data      JSON        NOT NULL DEFAULT '{}',
    output_data     JSON,
    selected_option JSON,
    llm_provider    VARCHAR(20),
    token_count     INTEGER,
    duration_ms     INTEGER,
    error_message   TEXT,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP
);

CREATE INDEX idx_pipeline_steps_project ON pipeline_steps(project_id, step_order);
CREATE INDEX idx_pipeline_steps_status ON pipeline_steps(project_id, status);

CREATE TABLE script_versions (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version_number      INTEGER     NOT NULL,
    content             TEXT        NOT NULL,
    format              VARCHAR(20) NOT NULL,
    hook_text           TEXT,
    narrative_pattern   VARCHAR(50),
    retention_techniques JSON,
    cta_text            TEXT,
    created_at          TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, version_number)
);

CREATE INDEX idx_script_versions_project ON script_versions(project_id, version_number DESC);

CREATE TABLE analysis_results (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID        NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    script_version_id   UUID        NOT NULL REFERENCES script_versions(id) ON DELETE CASCADE,
    agent_type          VARCHAR(20) NOT NULL CHECK (agent_type IN ('factcheck','readability','copyright','policy')),
    findings            JSON        NOT NULL DEFAULT '[]',
    overall_score       FLOAT,
    created_at          TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, script_version_id, agent_type)
);

CREATE INDEX idx_analysis_results_project ON analysis_results(project_id);
```

---

### API Endpoint Specifications

#### POST /api/v1/projects

**Request:**
```json
{
  "name": "My VSL Script",
  "topic": "Python course launch",
  "target_format": "VSL",
  "content_goal": "Sell",
  "raw_notes": "I want to sell my Python course..."
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My VSL Script",
  "topic": "Python course launch",
  "target_format": "VSL",
  "content_goal": "Sell",
  "status": "draft",
  "current_step": 0,
  "created_at": "2026-04-11T10:00:00Z",
  "updated_at": "2026-04-11T10:00:00Z"
}
```

**Errors:** 422 (validation error)

---

#### POST /api/v1/projects/{project_id}/pipeline/run/{step_type}

**Request:** Empty body (inputs assembled from project context)

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "step_type": "hook",
  "step_order": 2,
  "status": "completed",
  "input_data": { "icp_summary": "...", "topic": "..." },
  "output_data": {
    "suggestions": [
      { "rank": 1, "text": "What if I told you...", "rationale": "Directly addresses ICP pain point" },
      { "rank": 2, "text": "Stop writing Python the hard way...", "rationale": "Pattern interrupt for developers" }
    ]
  },
  "llm_provider": "modal",
  "token_count": 850,
  "duration_ms": 4500,
  "started_at": "2026-04-11T10:01:00Z",
  "completed_at": "2026-04-11T10:01:04Z"
}
```

**Errors:** 404 (project not found), 409 (dependency not met), 502 (all LLM providers failed)

---

#### PATCH /api/v1/projects/{project_id}/pipeline/{step_id}

**Request (user selection):**
```json
{
  "selected_option": {
    "hook_text": "What if I told you...",
    "rank": 1
  }
}
```

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "step_type": "hook",
  "status": "completed",
  "selected_option": {
    "hook_text": "What if I told you...",
    "rank": 1
  }
}
```

**Errors:** 422 (selection invalid for step type), 409 (step not in completed state)

---

#### POST /api/v1/projects/{project_id}/analyze/all

**Request:** Empty body

**Response (200):**
```json
[
  {
    "id": "...",
    "agent_type": "factcheck",
    "findings": [
      {
        "type": "factual_claim",
        "severity": "medium",
        "text": "Python is the most popular language",
        "suggestion": "Add qualifier: 'one of the most popular'",
        "confidence": "low"
      }
    ],
    "overall_score": null
  },
  {
    "id": "...",
    "agent_type": "readability",
    "findings": [],
    "overall_score": 72.5
  }
]
```

---

#### GET /api/v1/projects/{project_id}/export?format=md

**Response (200):**
```
Content-Type: text/markdown
Content-Disposition: attachment; filename="my-vsl-script.md"

# My VSL Script

**Hook:** What if I told you...
...
```

**Errors:** 404 (project not found), 409 (no completed script version)

---

### Sequence Diagrams

#### Full Pipeline Execution Flow

```
User              Frontend              Backend               Orchestrator           Agent              LLM Provider
  │                   │                     │                      │                    │                    │
  │  Create Project   │                     │                      │                    │                    │
  │──────────────────>│  POST /projects     │                      │                    │                    │
  │                   │────────────────────>│                      │                    │                    │
  │                   │  201 {project}      │                      │                    │                    │
  │                   │<────────────────────│                      │                    │                    │
  │                   │                     │                      │                    │                    │
  │  Enter Notes      │                     │                      │                    │                    │
  │──────────────────>│  PATCH /projects/1  │                      │                    │                    │
  │                   │────────────────────>│                      │                    │                    │
  │                   │                     │                      │                    │                    │
  │  Run ICP Agent    │                     │                      │                    │                    │
  │──────────────────>│  POST /pipeline/run/icp                   │                    │                    │
  │                   │────────────────────>│  run_step(ICP)       │                    │                    │
  │                   │                     │─────────────────────>│  execute()         │                    │
  │                   │                     │                      │───────────────────>│  generate()        │
  │                   │                     │                      │                    │───────────────────>│
  │                   │                     │                      │                    │  <streaming>       │
  │                   │  WS: agent_progress │                      │                    │<───────────────────│
  │  <streaming text> │<────────────────────│                      │                    │                    │
  │                   │                     │                      │  output            │                    │
  │                   │                     │                      │<───────────────────│                    │
  │                   │                     │  step completed      │                    │                    │
  │                   │                     │<─────────────────────│                    │                    │
  │                   │  200 {step result}  │                      │                    │                    │
  │  Review ICP       │<────────────────────│                      │                    │                    │
  │<──────────────────│                     │                      │                    │                    │
  │                   │                     │                      │                    │                    │
  │  Approve ICP      │                     │                      │                    │                    │
  │──────────────────>│  PATCH /pipeline/{step_id}                 │                    │                    │
  │                   │────────────────────>│  save selection      │                    │                    │
  │                   │                     │                      │                    │                    │
  │  ... (Hook, Narrative, Retention, CTA — same pattern)          │                    │                    │
  │                   │                     │                      │                    │                    │
  │  Run Writer       │                     │                      │                    │                    │
  │──────────────────>│  POST /pipeline/run/writer                 │                    │                    │
  │                   │────────────────────>│  run_step(WRITER)    │                    │                    │
  │                   │                     │─────────────────────>│  execute()         │                    │
  │                   │                     │                      │───────────────────>│  generate()        │
  │                   │                     │                      │                    │───────────────────>│
  │                   │  WS: streaming      │                      │                    │  <streaming>       │
  │  <script draft>   │<────────────────────│                      │                    │<───────────────────│
  │                   │                     │                      │                    │                    │
  │  Run All Analysis │                     │                      │                    │                    │
  │──────────────────>│  POST /analyze/all  │                      │                    │                    │
  │                   │────────────────────>│  run_analysis_parallel()               │                    │
  │                   │                     │─────────────────────>│  asyncio.gather(4) │                    │
  │                   │                     │                      │────────┬───────────>│  (4 agents run    │
  │                   │                     │                      │        │           │   in parallel)    │
  │                   │                     │                      │<───────┘           │──────────────────>│
  │                   │  WS: 4x results     │                      │                    │                    │
  │  <analysis tabs>  │<────────────────────│                      │                    │                    │
  │                   │                     │                      │                    │                    │
  │  Export Script    │                     │                      │                    │                    │
  │──────────────────>│  GET /export?format=md                     │                    │                    │
  │                   │────────────────────>│  generate file       │                    │                    │
  │  <download file>  │<────────────────────│                      │                    │                    │
```

#### LLM Provider Failover Sequence

```
Orchestrator          ModalProvider         GroqProvider          OllamaProvider
     │                     │                     │                     │
     │  generate()         │                     │                     │
     │────────────────────>│                     │                     │
     │                     │  POST /v1/chat      │                     │
     │                     │──────────────────────────────────────────>│
     │                     │  429 Rate Limit     │                     │
     │                     │<──────────────────────────────────────────│
     │  RateLimitError     │                     │                     │
     │<────────────────────│                     │                     │
     │  retry (attempt 1) │                     │                     │
     │────────────────────>│                     │                     │
     │                     │  POST /v1/chat      │                     │
     │                     │──────────────────────────────────────────>│
     │                     │  429 Rate Limit     │                     │
     │                     │<──────────────────────────────────────────│
     │  RateLimitError     │                     │                     │
     │<────────────────────│                     │                     │
     │  failover to Groq  │                     │                     │
     │─────────────────────────────────────────>│                     │
     │                     │                     │  POST /v1/chat      │
     │                     │                     │────────────────────>│
     │                     │                     │  200 OK             │
     │  result             │                     │<────────────────────│
     │<─────────────────────────────────────────│                     │
```

---

### Algorithms & Business Logic

#### ICP Generation Algorithm

```
INPUT: raw_notes (text), topic (string), target_format (enum), content_goal (enum)
OUTPUT: ICPProfile (demographics, psychographics, pain_points, desires, objections, language_style)

1. Construct system prompt with ICP schema definition
2. Construct user prompt:
   a. Include raw_notes verbatim
   b. Include topic, target_format, content_goal as context
   c. Request structured output matching ICP schema
3. Call LLM with structured output (response_model=ICPAgentOutput)
4. Validate output against Pydantic schema
5. If validation fails, retry with error feedback (max 2 retries)
6. Return validated ICP
```

#### Script Generation Algorithm

```
INPUT: icp (ICPProfile), hook (string), narrative_pattern (string), retention_techniques (string[]), cta (string), target_format (enum), topic (string), raw_notes (text)
OUTPUT: ScriptDraft (content, format, structural_cues)

1. Build generation context:
   a. Format template = get_format_template(target_format)
   b. Narrative outline = expand_narrative(narrative_pattern, topic, icp)
   c. Retention placements = compute_placements(retention_techniques, target_format)
   d. CTA integration point = determine_cta_position(target_format, narrative_pattern)

2. Construct system prompt:
   a. Role: expert copywriter for {target_format}
   b. Format rules from template
   c. Structural cue syntax: [B-ROLL], [TEXT OVERLAY], [PAUSE], etc.

3. Construct user prompt:
   a. ICP summary
   b. Selected hook (place at opening)
   c. Narrative structure to follow
   d. Retention techniques with placement markers
   e. CTA to integrate
   f. Raw notes as source material

4. Call LLM with streaming enabled
5. Stream tokens to frontend via WebSocket
6. On completion, parse structural cues into metadata
7. Save as new script version (increment version_number)
8. Return script draft
```

#### Readability Score Calculation

```
INPUT: script_content (text)
OUTPUT: ReadabilityResult (flesch_kincaid_score, gunning_fog_score, complex_sentences, suggestions)

1. Split text into sentences (regex on .!? with lookahead)
2. Split each sentence into words (whitespace tokenization)
3. Count syllables per word (heuristic: count vowel groups)
4. Compute Flesch-Kincaid Grade Level:
   FK = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
5. Compute Gunning Fog Index:
   GF = 0.4 * ((total_words / total_sentences) + 100 * (complex_words / total_words))
   where complex_words = words with 3+ syllables
6. Flag sentences with FK grade > target (default: 8 for general, 10 for technical)
7. For each flagged sentence, generate simplification suggestion via LLM
8. Return scores, flagged sentences, and suggestions
```

#### Pipeline Dependency Resolution

```
INPUT: step_type (enum), project_id (uuid)
OUTPUT: ready (bool), missing_dependencies (list[StepType])

DEPENDENCY_MAP = {
    ICP: [],
    HOOK: [ICP],
    NARRATIVE: [ICP, HOOK],
    RETENTION: [ICP, NARRATIVE],
    CTA: [ICP, HOOK, NARRATIVE],
    WRITER: [ICP, HOOK, NARRATIVE, RETENTION, CTA],
    FACTCHECK: [WRITER],
    READABILITY: [WRITER],
    COPYRIGHT: [WRITER],
    POLICY: [WRITER],
}

1. Look up DEPENDENCY_MAP[step_type]
2. For each dependency, check if pipeline_step exists with status=COMPLETED
3. Collect any unmet dependencies
4. If missing_dependencies is empty, return ready=True
5. Otherwise return ready=False with the list
```

---

### State Management

#### Backend State

| State | Storage | Mechanism |
|-------|---------|-----------|
| Project data | SQLite | SQLAlchemy ORM |
| Pipeline step state | SQLite | PipelineState state machine |
| ICP profile | SQLite | One-to-one with project |
| Script versions | SQLite | Versioned by version_number |
| Analysis results | SQLite | Per script version per agent type |
| LLM config | `.env` / environment | `pydantic-settings` Settings class |
| LLM response cache | In-memory LRU | `cachetools.LRUCache` (max 128 entries, 1h TTL) |

#### Frontend State

| State | Storage | Mechanism |
|-------|---------|-----------|
| Project list | Server cache | TanStack Query (staleTime: 30s) |
| Active project | Server cache + local | TanStack Query + Zustand |
| Pipeline state | Server cache | TanStack Query with WebSocket invalidation |
| Agent streaming output | Local | Zustand store updated by WebSocket messages |
| User selections (hook, narrative, etc.) | Server | PATCH requests on selection; optimistic updates via TanStack Query |
| Script editor content | Local + server | Zustand for live editing; debounced PATCH to backend |
| Settings (LLM config) | Server cache | TanStack Query |
| UI state (active tab, sidebar) | Local | Zustand |

#### Frontend Zustand Stores

```typescript
interface PipelineStore {
  activeProjectId: string | null;
  steps: PipelineStep[];
  streamingOutput: Record<StepType, string>;
  isRunning: boolean;

  setStepOutput: (stepType: StepType, output: string) => void;
  appendStreamingToken: (stepType: StepType, token: string) => void;
  setActiveProject: (id: string) => void;
  clearStreaming: (stepType: StepType) => void;
}

interface EditorStore {
  content: string;
  versionNumber: number;
  isDirty: boolean;
  isSaving: boolean;

  setContent: (content: string) => void;
  save: () => Promise<void>;
}
```

---

### Error & Exception Handling

#### Custom Exception Hierarchy

```python
class ScriptsWriterError(Exception):
    """Base exception for all application errors."""

class AgentExecutionError(ScriptsWriterError):
    """Agent failed to produce output after all retries and failover."""
    def __init__(self, agent_name: str, detail: str):
        self.agent_name = agent_name
        super().__init__(f"Agent '{agent_name}' failed: {detail}")

class AllProvidersFailedError(ScriptsWriterError):
    """All configured LLM providers failed to respond."""

class RateLimitExhaustedError(ScriptsWriterError):
    """Rate limit hit on all providers; retries exhausted."""
    def __init__(self, provider: str, retry_count: int):
        self.provider = provider
        self.retry_count = retry_count

class InvalidStateTransitionError(ScriptsWriterError):
    """Pipeline step cannot transition to requested state."""

class DependencyNotMetError(ScriptsWriterError):
    """Agent dependency not satisfied; cannot run step."""

class LLMOutputValidationError(ScriptsWriterError):
    """LLM output failed Pydantic schema validation."""

class ExportError(ScriptsWriterError):
    """File export failed."""
```

#### Error Response Format

```json
{
  "error": {
    "type": "AgentExecutionError",
    "message": "Agent 'hook' failed: All LLM providers unavailable",
    "detail": {
      "agent_name": "hook",
      "providers_attempted": ["modal", "groq", "gemini", "ollama"],
      "last_error": "Connection refused on localhost:11434"
    }
  }
}
```

#### Retry Configuration

| Scenario | Max Retries | Backoff | Failover |
|----------|------------|---------|----------|
| LLM 429 (rate limit) | 3 | Exponential: 1s, 2s, 4s | Yes — to next provider |
| LLM 5xx (server error) | 2 | Exponential: 1s, 2s | Yes — to next provider |
| LLM 4xx (auth/bad request) | 0 | None | No — return error |
| LLM malformed output | 2 | None (immediate) | No — retry same provider with reformatted prompt |
| Database write failure | 1 | 500ms | No — return 500 |
| WebSocket disconnect | Auto | Exponential: 1s, 2s, 4s, 8s | Client reconnects |

#### Logging Configuration

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

# Per-module log levels
logging_config = {
    "app.agents": "INFO",
    "app.llm": "DEBUG",
    "app.pipeline": "INFO",
    "app.api": "INFO",
}
```

---

### Testing Strategy

#### Unit Tests

| Module | Test Target | Framework | Coverage Target |
|--------|------------|-----------|-----------------|
| `app/agents/` | Each agent's `build_prompt()` output, input validation | `pytest` + `pytest-asyncio` | 90% |
| `app/llm/` | Provider instantiation, failover logic, cache hit/miss | `pytest` + mocked LLM responses | 95% |
| `app/pipeline/` | State transitions, dependency resolution, branching logic | `pytest` | 95% |
| `app/services/` | Business logic — project CRUD, export generation | `pytest` + mocked DB | 85% |
| `app/schemas/` | Pydantic validation — valid/invalid inputs, edge cases | `pytest` | 95% |

#### Unit Test Example: Agent Prompt Construction

```python
async def test_hook_agent_build_prompt():
    provider = MockLLMProvider()
    agent = HookAgent(provider)
    inputs = HookAgentInput(
        icp=ICPProfile(demographics={"age": "25-45"}, pain_points=["boring content"]),
        topic="Python course",
        target_format="VSL",
        content_goal="Sell",
    )
    prompt = agent.build_prompt(inputs)
    assert "Python course" in prompt
    assert "VSL" in prompt
    assert "5 compelling hooks" in prompt
```

#### Unit Test Example: Failover Logic

```python
async def test_provider_failover_modal_to_groq():
    modal = MockProvider("modal", should_fail=True)
    groq = MockProvider("groq", should_fail=False)
    factory = ProviderFactory(providers=[modal, groq])
    result = await factory.execute_with_failover("test prompt", "system")
    assert result == "groq response"
    assert modal.call_count == 3  # 3 retries before failover
    assert groq.call_count == 1
```

#### Integration Tests

| Scenario | Test Flow | Tools |
|----------|----------|-------|
| Full pipeline (happy path) | Create project → run all agents → verify output at each step | `pytest` + `httpx.AsyncClient` + test DB |
| Failover recovery | Start with failing primary provider → verify fallback to secondary | `pytest` + mock providers |
| WebSocket streaming | Connect WS → trigger agent → verify streaming tokens received | `pytest` + `websockets` library |
| Project persistence | Create project → kill server → restart → verify project loads | `pytest` + temp DB file |
| Export flow | Complete pipeline → export as txt and md → verify file contents | `pytest` + temp directory |

#### Mocking Strategy

| Component | Mock Approach |
|-----------|-------------|
| LLM providers | `MockLLMProvider` returning predefined responses; controllable failure modes |
| Database | In-memory SQLite for tests; `pytest` fixtures with transaction rollback |
| WebSocket | `MockWSHandler` collecting emitted events for assertion |
| External APIs | `httpx` mock routes; no real API calls in CI |

#### Frontend Tests

| Type | Target | Framework |
|------|--------|-----------|
| Component tests | Agent panels, pipeline view, script editor | `Vitest` + `React Testing Library` |
| Hook tests | `usePipeline`, `useWebSocket`, `useAgentStream` | `Vitest` + `@testing-library/react-hooks` |
| Store tests | Zustand stores — state transitions, actions | `Vitest` |
| E2E (future) | Full user flow | `Playwright` |
