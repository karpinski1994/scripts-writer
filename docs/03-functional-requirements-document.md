# Functional Requirements Document – Scripts Writer

## Functional Overview

Scripts Writer is an agentic AI application that orchestrates a multi-step creative pipeline. Each step is handled by a specialized agent that processes inputs, produces outputs, and passes results to the next agent. The user acts as a director — providing initial notes, making selections at decision points, and approving the final output. The system enforces a structured methodology while remaining flexible enough to accommodate different content formats and creative styles.

The core workflow follows this sequence:

```
Notes & Context → ICP Analysis → Hook Selection → Narrative Pattern → Retention Techniques → CTA Selection → Script Generation → Analysis (Fact-check, Readability, Copyright, Policy) → Export
```

## User Personas & Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Creator** (Primary) | Authenticated user who initiates and directs the script writing process | Full access: create projects, run all agents, edit all inputs/outputs, export scripts |
| **Viewer** (Future) | Read-only access to previously generated scripts | View exported scripts only; no agent execution |

> **Note:** In v1, there is a single user role (Creator). Multi-user and role-based access are out of scope.

## User Stories

| ID | User Story |
|----|-----------|
| US-1 | As a Creator, I want to enter my raw notes and topic context so that the agents have grounded material to work with |
| US-2 | As a Creator, I want the system to analyze my notes and generate an ICP profile so that my script is tailored to the right audience |
| US-2a | As a Creator, I want the system to analyze my notes and let me to upload an ICP profile so that my script is tailored to the right audience |
| US-3 | As a Creator, I want to review and edit the ICP (uploaded or generated) before proceeding so that I maintain control over audience targeting |
| US-4 | As a Creator, I want the system to suggest multiple hooks based on my ICP so that I can choose the most compelling opening |
| US-5 | As a Creator, I want to select a narrative pattern (PAS, AIDA, Story Loop, etc.) so that my script follows a proven conversion structure |
| US-6 | As a Creator, I want the system to recommend retention techniques for my chosen format so that my audience stays engaged |
| US-7 | As a Creator, I want to select and customize my CTA so that it drives the specific action I need |
| US-8 | As a Creator, I want the system to generate a complete script draft combining all my selections so that I have a starting point to refine |
| US-9 | As a Creator, I want the system to fact-check my script so that I don't publish misinformation |
| US-10 | As a Creator, I want the system to check my script for typos and readability so that it's professional quality |
| US-11 | As a Creator, I want the system to flag potential copyright issues so that I avoid legal risk |
| US-12 | As a Creator, I want the system to check my script against platform policies so that my content doesn't get removed |
| US-13 | As a Creator, I want to choose my output format (VSL, YouTube, tutorial, Facebook, LinkedIn, blog) so that the script matches the target platform |
| US-14 | As a Creator, I want to re-run individual agents without restarting the whole pipeline so that I can iterate on specific parts |
| US-15 | As a Creator, I want to export my final script in multiple formats (plain text, markdown, clipboard) so that I can use it in my workflow |
| US-16 | As a Creator, I want to attach a Google NotebookLM notebook to my project so that agents can use my existing research and notes |
| US-17 | As a Creator, I want to query my NotebookLM notebook for specific insights before running an agent so that the agent output is grounded in my research |
| US-18 | As a Creator, I want to attach NotebookLM context to any creative step (ICP, Hook, Narrative, Retention, CTA, Writer) so that each agent can benefit from relevant research |

## Functional Requirements

### FR-1: Note & Context Collection

| ID | Requirement | Priority |
|----|------------|----------|
| FR-1.1 | The system shall provide an input interface for raw notes (freeform text) | Must |
| FR-1.1.1 | The system shall provide an upload interface to upload text files (icp, notes, etc.) | Must |
| FR-1.2 | The system shall allow the user to specify the topic or subject of the content | Must |
| FR-1.3 | The system shall allow the user to specify the target format (VSL, YouTube, tutorial, Facebook, LinkedIn, blog) | Must |
| FR-1.4 | The system shall allow the user to specify the content goal (sell, educate, entertain, build authority) | Should |
| FR-1.5 | The system shall persist notes and context per project so the user can resume later | Must |
| FR-1.6 | The system shall allow the user to attach existing ICP data from upload or NotebookLM if available, skipping the ICP agent | Should |

### FR-2: ICP Analysis Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-2.1 | The system shall analyze raw notes (optionally enriched by NotebookLM context) and generate an ICP profile including demographics, psychographics, pain points, and desires | Must |
| FR-2.2 | The system shall present the generated ICP to the user for review and editing before proceeding | Must |
| FR-2.3 | The system shall allow the user to manually override any ICP field | Must |
| FR-2.4 | The system shall store the approved ICP as part of the project context for downstream agents | Must |

### FR-3: Hook Suggestion Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-3.1 | The system shall generate at least 5 hook suggestions based on the ICP and topic | Must |
| FR-3.2 | The system shall rank hook suggestions by predicted effectiveness (based on ICP alignment) | Should |
| FR-3.3 | The system shall allow the user to select one hook from the suggestions | Must |
| FR-3.4 | The system shall allow the user to edit a selected hook before proceeding | Must |
| FR-3.5 | The system shall allow the user to write a custom hook instead of using suggestions | Should |

### FR-4: Narrative Pattern Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-4.1 | The system shall present available narrative patterns (PAS, AIDA, Story Loop, Before-After-Bridge, etc.) | Must |
| FR-4.2 | The system shall recommend a narrative pattern based on content goal and format | Should |
| FR-4.3 | The system shall allow the user to select a narrative pattern | Must |
| FR-4.4 | The system shall provide a brief description of each pattern when selected | Must |

### FR-5: Retention Technique Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-5.1 | The system shall recommend retention techniques suitable for the chosen format (e.g., pattern interrupts, open loops, visual cues for video; subheadings, bullet resets for text) | Must |
| FR-5.2 | The system shall allow the user to select multiple retention techniques to apply | Must |
| FR-5.3 | The system shall indicate where in the script each technique should be placed (e.g., "insert open loop at 25% mark") | Should |

### FR-6: CTA Selection Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-6.1 | The system shall suggest CTAs based on the content goal and ICP | Must |
| FR-6.2 | The system shall allow the user to select a CTA type (subscribe, buy, click, follow, comment, share) | Must |
| FR-6.3 | The system shall allow the user to customize the CTA wording | Must |
| FR-6.4 | The system shall suggest CTA placement within the script (end only, mid + end, soft CTA + hard CTA) | Should |

### FR-7: Script Generation Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-7.1 | The system shall generate a complete script draft incorporating the selected hook, narrative, retention techniques, and CTA | Must |
| FR-7.2 | The system shall format the script according to the selected output format (VSL, YouTube, tutorial, Facebook, LinkedIn, blog) | Must |
| FR-7.3 | The system shall include visual/structural cues in video scripts (e.g., [B-ROLL], [TEXT OVERLAY], [PAUSE]) | Should |
| FR-7.4 | The system shall allow the user to edit the generated script inline | Must |
| FR-7.5 | The system shall allow the user to regenerate the script with different selections without losing the previous version | Should |


### FR-8: Fact-Checking Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-8.1 | The system shall identify factual claims within the script | Must |
| FR-8.2 | The system shall flag claims that cannot be verified or appear questionable | Must |
| FR-8.3 | The system shall provide a confidence level (high/medium/low) for each flagged claim | Should |
| FR-8.4 | The system shall present findings as advisory, not authoritative — the user has final say | Must |

### FR-9: Readability & Typo Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-9.1 | The system shall detect spelling and grammar errors in the script | Must |
| FR-9.2 | The system shall compute a readability score (e.g., Flesch-Kincaid, Gunning Fog) appropriate to the target audience | Must |
| FR-9.3 | The system shall flag sentences that exceed a configurable complexity threshold | Should |
| FR-9.4 | The system shall suggest corrections for detected issues | Must |

### FR-10: Copyright Compliance Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-10.1 | The system shall flag text segments that closely resemble known copyrighted material | Must |
| FR-10.2 | The system shall flag the use of trademarked terms without proper context | Should |
| FR-10.3 | The system shall present findings as advisory warnings, not legal determinations | Must |
| FR-10.4 | The system shall allow the user to acknowledge and dismiss copyright warnings | Must |

### FR-11: Platform Policy Agent

| ID | Requirement | Priority |
|----|------------|----------|
| FR-11.1 | The system shall check the script against YouTube community guidelines and policies | Must |
| FR-11.2 | The system shall check the script against Facebook/Meta advertising policies (for Facebook format) | Should |
| FR-11.3 | The system shall check the script against LinkedIn content policies (for LinkedIn format) | Should |
| FR-11.4 | The system shall flag content that may violate platform-specific policies (e.g., deceptive practices, misleading claims) | Must |
| FR-11.5 | The system shall present findings as advisory — platform enforcement is outside the system's control | Must |

### FR-12: LLM Integration Layer

| ID | Requirement | Priority |
|----|------------|----------|
| FR-12.1 | The system shall support at least one local LLM provider (e.g., Ollama) | Must |
| FR-12.2 | The system shall support at least one free-tier cloud LLM provider (e.g., Groq, Google Gemini) | Must |
| FR-12.3 | The system shall allow the user to configure which LLM provider(s) to use | Must |
| FR-12.4 | The system shall handle rate-limit responses gracefully (queue, retry, or fallback to alternate provider) | Must |
| FR-12.5 | The system shall not require any paid API key or subscription | Must |

### FR-13: Project & Export Management

| ID | Requirement | Priority |
|----|------------|----------|
| FR-13.1 | The system shall allow the user to create, save, and load projects (each project = one script pipeline) | Must |
| FR-13.2 | The system shall export final scripts as plain text | Must |
| FR-13.3 | The system shall export final scripts as Markdown | Must |
| FR-13.4 | The system shall copy final scripts to the system clipboard | Should |
| FR-13.5 | The system shall maintain a version history of script revisions within a project | Should |

### FR-15: NotebookLM Integration

| ID | Requirement | Priority |
|----|------------|----------|
| FR-15.1 | The system shall allow the user to connect a Google NotebookLM notebook to a project | Must |
| FR-15.2 | The system shall allow the user to attach NotebookLM context to any creative pipeline step before running the agent | Must |
| FR-15.3 | The system shall query the NotebookLM notebook for insights relevant to the current step type (ICP profiling, hook ideas, narrative summaries, retention techniques, CTA wording, script generation) | Should |
| FR-15.4 | The system shall present NotebookLM-sourced context alongside agent output for review | Should |
| FR-15.5 | The system shall degrade gracefully if NotebookLM is unavailable — agents proceed with raw notes only | Must |
| FR-15.6 | The system shall allow the user to disconnect a notebook from a project | Should |

## Workflow & Logic

### Main Pipeline Flow

```
Step 1: User creates a new project
Step 2: User enters notes, topic, target format, content goal
Step 3: System runs ICP Agent → presents ICP for user review
Step 4: User approves/edits ICP
Step 5: System runs Hook Agent → presents ranked hook suggestions
Step 6: User selects/edits hook
Step 7: System runs Narrative Agent → presents pattern options with recommendations
Step 8: User selects narrative pattern
Step 9: System runs Retention Agent → presents technique suggestions
Step 10: User selects retention techniques
Step 11: System runs CTA Agent → presents CTA suggestions
Step 12: User selects/customizes CTA
Step 13: System runs Writer Agent → generates script draft
Step 14: User reviews/edits script
Step 15: System runs Analysis Agents (fact-check, readability, copyright, policy) in parallel
Step 16: System presents analysis results with advisory flags
Step 17: User acknowledges findings, makes revisions if needed
Step 18: User exports final script
```

### Re-run Logic

- The user can re-run any individual agent from any step without restarting the pipeline
- Re-running an agent invalidates downstream results (the user is warned before proceeding)
- The user can branch a project — create a copy from any step to explore different selections

## Data Requirements

### Input Data

| Data Field | Type | Required | Validation |
|-----------|------|----------|------------|
| Project name | String | Yes | Non-empty, max 100 characters |
| Raw notes | Text | Yes | Non-empty, max 10,000 characters |
| Topic/subject | String | Yes | Non-empty, max 200 characters |
| Target format | Enum | Yes | One of: VSL, YouTube, Tutorial, Facebook, LinkedIn, Blog |
| Content goal | Enum | No | One of: Sell, Educate, Entertain, Build Authority |
| Existing ICP data | Object | No | Must conform to ICP schema if provided |

### ICP Data Schema

| Field | Type | Description |
|-------|------|-------------|
| Demographics | String[] | Age range, gender, location, occupation, income |
| Psychographics | String[] | Values, interests, attitudes, lifestyle |
| Pain points | String[] | Problems the audience faces |
| Desires | String[] | Outcomes the audience wants |
| Objections | String[] | Reasons the audience might resist the CTA |
| Language style | String | Preferred tone (casual, professional, technical) |

### Output Data

| Data Field | Type | Description |
|-----------|------|-------------|
| Generated script | Text | Full script with format-appropriate structure |
| Hook text | String | Selected hook |
| Narrative pattern | String | Selected pattern name |
| Retention techniques | String[] | Selected technique names with placement notes |
| CTA text | String | Selected/customized CTA |
| ICP profile | Object | Approved ICP data |
| Analysis results | Object[] | List of findings per agent (type, severity, text, suggestion) |

## UI/UX Functional Specs

### Navigation

- **Dashboard**: List of projects with status (in-progress, completed)
- **Project View**: Step-by-step pipeline view showing current step and completed steps
- **Agent Output Panel**: Displays agent results with edit/approve controls
- **Script Editor**: Inline text editor for the generated script
- **Analysis Panel**: Tabbed view showing results from each analysis agent
- **Settings**: LLM provider configuration, preferences

### Screen Transitions

```
Dashboard → New Project → Notes Input → ICP Review → Hook Selection →
Narrative Selection → Retention Selection → CTA Selection →
Script Editor → Analysis Review → Export
```

- Each step has "Back" and "Continue" navigation
- Steps can be accessed non-linearly via the pipeline sidebar (for re-runs)
- The script editor is accessible at any point after initial generation

## Exception Handling

| Exception | Handling |
|-----------|----------|
| LLM API returns rate-limit error | Queue request with exponential backoff; if retry limit exceeded, attempt fallback provider; if no fallback available, notify user with option to wait or switch provider |
| LLM API returns invalid/malformed response | Retry with reformatted prompt (max 2 retries); if still invalid, present raw output to user with warning |
| User submits empty notes | Reject with validation message: "Notes cannot be empty" |
| User attempts to skip ICP step without providing existing ICP | Block progression with message: "Please review the ICP or provide your own before proceeding" |
| Copyright agent flags content as potentially infringing | Display advisory warning; user can acknowledge and dismiss |
| Fact-check agent cannot verify a claim | Display as "Unverifiable" with low confidence; user decides whether to keep |
| No LLM provider is configured on first run | Show setup wizard guiding user through provider configuration |
| Local LLM (Ollama) is not running | Detect connection failure; prompt user to start Ollama or switch to cloud provider |
| Script generation exceeds token limit | Split generation into sections; reassemble; notify user of chunking |
