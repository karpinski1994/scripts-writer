# Software Requirements Specification – Scripts Writer

## 1. Introduction

### Purpose

This Software Requirements Specification (SRS) defines the complete set of requirements for Scripts Writer, an agentic AI application that guides content creators through a structured, multi-step workflow to produce high-converting, compliant video scripts and marketing posts. This document serves as the definitive reference for developers, testers, and stakeholders throughout the development lifecycle.

### Scope

Scripts Writer transforms raw notes and audience insights into polished, analyzed scripts for videos (VSLs, YouTube, tutorials) and written marketing posts (Facebook, LinkedIn, blogs). The system orchestrates specialized AI agents — ICP Analysis, Hook Suggestion, Narrative Pattern, Retention Technique, CTA Selection, Script Generation, and Analysis (Fact-check, Readability, Copyright, Policy) — in a sequential pipeline with user direction at each decision point.

**In Scope:**
- Full agentic pipeline from raw notes to exported script
- Multi-format output (VSL, YouTube, tutorial, Facebook, LinkedIn, blog)
- Automated compliance and quality analysis
- Free-tier LLM integration (local + cloud)
- Local-first, self-hosted deployment
- Project management with version history

**Out of Scope:**
- Video/audio production or editing
- Social media scheduling or publishing
- Multi-tenant SaaS or user authentication system
- Mobile application
- Real-time collaboration
- Paid LLM API tiers

### Definitions & Acronyms

| Term | Definition |
|------|-----------|
| **Agentic** | AI system where autonomous agents perform tasks in sequence, each with a specific role |
| **ICP** | Ideal Customer Profile — detailed description of the target audience |
| **VSL** | Video Sales Letter — long-form video designed to sell a product or service |
| **CTA** | Call To Action — directs the audience to take a specific action |
| **PAS** | Problem-Agitate-Solution — copywriting framework |
| **AIDA** | Attention-Interest-Desire-Action — copywriting framework |
| **LLM** | Large Language Model |
| **Pydantic AI** | Python framework for building AI agents with structured input/output using Pydantic models |
| **FastAPI** | Python web framework for building APIs with automatic validation |
| **Next.js** | React framework for full-stack web applications |
| **Shadcn/UI** | Re-usable UI component library for React with Tailwind CSS |
| **Groq** | Cloud LLM inference provider with free-tier access |
| **Modal** | Cloud compute platform hosting LLM inference endpoints |
| **Ollama** | Local LLM runtime for running models on-device |

---

## 2. Overall Description

### Product Perspective

Scripts Writer is a standalone web application with a client-server architecture. The frontend (Next.js) provides the user interface; the backend (FastAPI) hosts the agentic pipeline, LLM integration layer, and data persistence. The system depends on external LLM providers (Modal, Groq, Google Gemini, local Ollama) for AI inference, and optionally on YouTube Data API and Google LM Notes for enhanced context.

The system is not part of a larger product suite. It is a self-contained tool deployed locally or on a single server instance.

```
┌──────────────┐     HTTP/WS     ┌──────────────┐     API      ┌─────────────────┐
│  Next.js     │ ◄────────────► │  FastAPI      │ ◄──────────► │  LLM Providers  │
│  Frontend    │                │  Backend      │              │  (Modal, Groq,  │
│  (Shadcn/UI, │                │  (Pydantic AI)│              │   Gemini,       │
│   Tailwind)  │                │               │              │   Ollama)       │
└──────────────┘                └──────────────┘              └─────────────────┘
                                       │
                                       │ API
                                       ▼
                                ┌─────────────────┐
                                │  External APIs   │
                                │  (YouTube Data,  │
                                │   Google LM Notes│
                                │   )              │
                                └─────────────────┘
```

### User Classes & Characteristics

| User Class | Description | Technical Proficiency | Frequency of Use |
|------------|-------------|----------------------|-----------------|
| **Creator (Primary)** | Developer-educator who creates technical/marketing content | High — comfortable with CLI, self-hosting, APIs | Daily to weekly |
| **General Creator** | Solo marketer or small business owner | Medium — can follow setup guides, prefers GUI | Weekly to monthly |
| **Student Learner** | Learner practicing copywriting methodology | Varies — needs clear onboarding | Course-bound, episodic |

### Operating Environment

| Component | Requirement |
|-----------|-------------|
| **Server OS** | macOS (must), Windows/Linux (should) |
| **Client Browser** | Chrome, Firefox, Safari, Edge (latest 2 major versions) |
| **Runtime** | Python 3.11+, Node.js 20+ |
| **Local LLM** | Ollama installed and running (optional, for local inference) |
| **Minimum Hardware** | 8 GB RAM, 2 CPU cores (for app server); 16 GB RAM recommended for local LLM inference |
| **Network** | Internet connection required for cloud LLM providers; not required for Ollama-only mode |

---

## 3. System Features & Functional Requirements

### SRS-F01: Note & Context Collection

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F01.1 | The system shall provide an input interface for raw notes (freeform text, max 10,000 characters) | Must |
| SRS-F01.2 | The system shall provide an upload interface for text files (ICP profiles, notes, etc.) | Must |
| SRS-F01.3 | The system shall allow the user to specify the topic/subject (max 200 characters) | Must |
| SRS-F01.4 | The system shall allow the user to select the target format from: VSL, YouTube, Tutorial, Facebook, LinkedIn, Blog | Must |
| SRS-F01.5 | The system shall allow the user to specify the content goal: Sell, Educate, Entertain, Build Authority | Should |
| SRS-F01.6 | The system shall persist all inputs per project for later resumption | Must |

### SRS-F02: ICP Analysis Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F02.1 | The system shall analyze raw notes and generate an ICP profile including demographics, psychographics, pain points, desires, objections, and language style | Must |
| SRS-F02.2 | The system shall present the generated ICP to the user for review and editing before proceeding | Must |
| SRS-F02.3 | The system shall allow the user to upload an existing ICP profile, skipping the generation step | Must |
| SRS-F02.4 | The system shall allow the user to manually override any ICP field | Must |
| SRS-F02.5 | The system shall store the approved ICP as part of the project context for downstream agents | Must |

### SRS-F03: Hook Suggestion Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F03.1 | The system shall generate at least 5 hook suggestions based on the ICP and topic | Must |
| SRS-F03.2 | The system shall rank hook suggestions by predicted effectiveness (ICP alignment score) | Should |
| SRS-F03.3 | The system shall allow the user to select one hook from the suggestions | Must |
| SRS-F03.4 | The system shall allow the user to edit a selected hook before proceeding | Must |
| SRS-F03.5 | The system shall allow the user to write a custom hook instead of using suggestions | Should |

### SRS-F04: Narrative Pattern Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F04.1 | The system shall present available narrative patterns (PAS, AIDA, Story Loop, Before-After-Bridge, etc.) | Must |
| SRS-F04.2 | The system shall recommend a narrative pattern based on content goal and format | Should |
| SRS-F04.3 | The system shall allow the user to select a narrative pattern | Must |
| SRS-F04.4 | The system shall provide a brief description of each pattern when selected | Must |

### SRS-F05: Retention Technique Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F05.1 | The system shall recommend retention techniques suitable for the chosen format (pattern interrupts, open loops, visual cues for video; subheadings, bullet resets for text) | Must |
| SRS-F05.2 | The system shall allow the user to select multiple retention techniques to apply | Must |
| SRS-F05.3 | The system shall indicate where in the script each technique should be placed (e.g., "insert open loop at 25% mark") | Should |

### SRS-F06: CTA Selection Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F06.1 | The system shall suggest CTAs based on the content goal and ICP | Must |
| SRS-F06.2 | The system shall allow the user to select a CTA type (subscribe, buy, click, follow, comment, share) | Must |
| SRS-F06.3 | The system shall allow the user to customize the CTA wording | Must |
| SRS-F06.4 | The system shall suggest CTA placement within the script (end only, mid + end, soft CTA + hard CTA) | Should |

### SRS-F07: Script Generation Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F07.1 | The system shall generate a complete script draft incorporating the selected hook, narrative, retention techniques, and CTA | Must |
| SRS-F07.2 | The system shall format the script according to the selected output format | Must |
| SRS-F07.3 | The system shall include visual/structural cues in video scripts (e.g., [B-ROLL], [TEXT OVERLAY], [PAUSE]) | Should |
| SRS-F07.4 | The system shall allow the user to edit the generated script inline | Must |
| SRS-F07.5 | The system shall allow the user to regenerate the script without losing the previous version | Should |

### SRS-F08: Fact-Checking Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F08.1 | The system shall identify factual claims within the script | Must |
| SRS-F08.2 | The system shall flag claims that cannot be verified or appear questionable | Must |
| SRS-F08.3 | The system shall provide a confidence level (high/medium/low) for each flagged claim | Should |
| SRS-F08.4 | The system shall present findings as advisory — the user has final say | Must |

### SRS-F09: Readability & Typo Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F09.1 | The system shall detect spelling and grammar errors in the script | Must |
| SRS-F09.2 | The system shall compute a readability score (Flesch-Kincaid, Gunning Fog) | Must |
| SRS-F09.3 | The system shall flag sentences exceeding a configurable complexity threshold | Should |
| SRS-F09.4 | The system shall suggest corrections for detected issues | Must |

### SRS-F10: Copyright Compliance Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F10.1 | The system shall flag text segments closely resembling known copyrighted material | Must |
| SRS-F10.2 | The system shall flag the use of trademarked terms without proper context | Should |
| SRS-F10.3 | The system shall present findings as advisory warnings, not legal determinations | Must |
| SRS-F10.4 | The system shall allow the user to acknowledge and dismiss copyright warnings | Must |

### SRS-F11: Platform Policy Agent

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F11.1 | The system shall check the script against YouTube community guidelines and policies | Must |
| SRS-F11.2 | The system shall check the script against Facebook/Meta advertising policies (for Facebook format) | Should |
| SRS-F11.3 | The system shall check the script against LinkedIn content policies (for LinkedIn format) | Should |
| SRS-F11.4 | The system shall flag content that may violate platform-specific policies | Must |
| SRS-F11.5 | The system shall present findings as advisory | Must |

### SRS-F12: LLM Integration Layer

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F12.1 | The system shall support Modal as an LLM provider (OpenAI-compatible endpoint) | Must |
| SRS-F12.2 | The system shall support Groq as an LLM provider | Must |
| SRS-F12.3 | The system shall support Google Gemini as an LLM provider | Must |
| SRS-F12.4 | The system shall support Ollama as a local LLM provider | Must |
| SRS-F12.5 | The system shall allow the user to configure which LLM provider(s) to use | Must |
| SRS-F12.6 | The system shall handle rate-limit responses gracefully (queue, retry, fallback to alternate provider) | Must |
| SRS-F12.7 | The system shall not require any paid API key or subscription | Must |
| SRS-F12.8 | The system shall support Google LM Notes for enhanced note integration | Should |

### SRS-F13: Project & Export Management

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F13.1 | The system shall allow the user to create, save, and load projects (each project = one script pipeline) | Must |
| SRS-F13.2 | The system shall export final scripts as plain text | Must |
| SRS-F13.3 | The system shall export final scripts as Markdown | Must |
| SRS-F13.4 | The system shall copy final scripts to the system clipboard | Should |
| SRS-F13.5 | The system shall maintain a version history of script revisions within a project | Should |

### SRS-F14: Pipeline Control

| ID | Requirement | Priority |
|----|------------|----------|
| SRS-F14.1 | The system shall allow the user to re-run any individual agent without restarting the pipeline | Must |
| SRS-F14.2 | The system shall warn the user when re-running an agent that downstream results will be invalidated | Must |
| SRS-F14.3 | The system shall allow the user to branch a project — create a copy from any step | Should |
| SRS-F14.4 | The system shall provide a visual pipeline view showing current and completed steps | Must |

---

## 4. External Interface Requirements

### User Interfaces

| Interface | Description |
|-----------|-------------|
| **Dashboard** | Project list with status indicators (in-progress, completed); create new project action |
| **Pipeline View** | Step-by-step visual showing current step, completed steps, and future steps with sidebar navigation |
| **Agent Output Panel** | Displays agent results (ICP profile, hooks, narrative options, etc.) with edit/approve controls |
| **Script Editor** | Inline rich-text editor for reviewing and editing generated scripts |
| **Analysis Panel** | Tabbed view showing results from each analysis agent (fact-check, readability, copyright, policy) with severity indicators |
| **Settings** | LLM provider configuration, API key management, default preferences |
| **Responsive Layout** | Minimum viewport width 1024px; optimized for desktop use |

### Hardware/Software Interfaces

| Interface | Protocol | Description |
|-----------|----------|-------------|
| Modal LLM API | HTTPS (OpenAI-compatible REST) | GLM-5.1 model inference via `https://api.us-west-2.modal.direct/v1` |
| Groq API | HTTPS (REST) | LLM inference via Groq free tier |
| Google Gemini API | HTTPS (REST) | LLM inference via Google Gemini free tier |
| Ollama API | HTTP (REST) | Local LLM inference on `localhost:11434` |
| YouTube Data API | HTTPS (REST) | Video metadata and content policy context (optional) |
| Google LM Notes API | HTTPS (REST) | Note integration and context enhancement (optional) |
| Local Filesystem | File I/O | Project persistence, export files, uploaded documents |

### Communication Interfaces

| Interface | Protocol | Description |
|-----------|----------|-------------|
| Frontend ↔ Backend | HTTP/REST + WebSocket | REST for CRUD operations; WebSocket for real-time agent progress updates and streaming responses |
| Backend ↔ LLM Providers | HTTPS/REST | Synchronous and streaming API calls to LLM providers |
| Backend ↔ External APIs | HTTPS/REST | Optional integration with YouTube Data API and Google LM Notes |

---

## 5. Non-Functional Requirements

### Performance

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-P1 | Individual agent response time shall not exceed 60 seconds under normal conditions | ≤ 60s per agent |
| NFR-P2 | Full pipeline execution (all agents sequentially with user decisions) shall complete within 3 minutes of compute time | ≤ 3 min total compute |
| NFR-P3 | Page load time for the frontend shall not exceed 2 seconds | ≤ 2s initial load |
| NFR-P4 | The system shall stream LLM responses to the frontend as they are generated to reduce perceived latency | Streaming via WebSocket |
| NFR-P5 | The system shall support concurrent agent execution where dependencies allow (e.g., analysis agents in parallel) | Parallel execution |

### Security

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-S1 | All API keys shall be stored in local environment variables or a local `.env` file, never hardcoded or committed to version control | Zero hardcoded keys in source |
| NFR-S2 | Communication with cloud LLM providers shall use HTTPS/TLS encryption | TLS 1.2+ |
| NFR-S3 | User data (notes, scripts, ICP profiles) shall be stored locally with no external data transmission except to configured LLM providers | Local-only storage |
| NFR-S4 | The system shall not collect, transmit, or store usage analytics or personal data to third parties | Zero telemetry |
| NFR-S5 | LLM provider API keys shall be masked in the settings UI | Masked display |

### Reliability & Availability

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-R1 | The system shall handle LLM provider failures gracefully with automatic failover to the next configured provider | Failover within 10s |
| NFR-R2 | The system shall persist project state after each agent completion, enabling recovery after unexpected shutdowns | Auto-save per step |
| NFR-R3 | The system shall implement retry logic with exponential backoff for transient LLM API failures (max 3 retries) | Max 3 retries |
| NFR-R4 | The system shall not lose user input data due to agent failures — all user-provided content shall be persisted before processing | Pre-execution persistence |

### Scalability

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-SC1 | The system shall be designed for single-user local operation; concurrent multi-user access is not required for v1 | Single user |
| NFR-SC2 | The architecture shall be modular enough to support future multi-user deployment without fundamental restructuring | Agent-based modularity |
| NFR-SC3 | The system shall support adding new LLM providers without modifying agent logic (adapter pattern) | Provider-agnostic agent layer |

### Maintainability

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-M1 | Each agent shall be implemented as an independent, interchangeable module following Pydantic AI patterns | Independent agent modules |
| NFR-M2 | The system shall use structured Pydantic models for all agent inputs and outputs to ensure type safety and validation | Pydantic validation on all I/O |
| NFR-M3 | API endpoints shall follow REST conventions with OpenAPI documentation auto-generated by FastAPI | Auto-generated API docs |
| NFR-M4 | The frontend shall use Shadcn/UI component composition for consistent, maintainable UI patterns | Component-based architecture |
| NFR-M5 | The system shall include a logging framework for debugging agent execution and LLM interactions | Structured logging |

---

## 6. Constraints & Compliance

| ID | Constraint | Detail |
|----|-----------|--------|
| C-1 | **Technology Stack** | Backend: Python 3.11+, FastAPI, Pydantic, Pydantic AI; Frontend: Next.js, Shadcn/UI, Tailwind CSS |
| C-2 | **LLM Providers** | Modal (GLM-5.1, OpenAI-compatible), Groq, Google Gemini, Ollama (local) — free tiers only |
| C-3 | **Budget** | $0 — no paid services, APIs, or hosting |
| C-4 | **Platform** | macOS (must), Windows/Linux (should) |
| C-5 | **Data Residency** | All user data stored locally; no cloud persistence; data sent to LLM providers is subject to their respective privacy policies |
| C-6 | **Copyright Disclaimer** | Copyright and policy analysis findings are advisory only — the system does not provide legal determinations |
| C-7 | **Single User** | v1 is designed for single-user local operation; no authentication or multi-tenancy |
| C-8 | **Node.js** | Node.js 20+ required for Next.js frontend |
| C-9 | **Python** | Python 3.11+ required for FastAPI backend |
