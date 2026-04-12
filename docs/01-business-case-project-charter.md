# Business Case & Project Charter – Scripts Writer

## Part 1: Business Case (The Why)

### Executive Summary

Scripts Writer is an agentic AI application designed to help content creators — primarily screenwriters, marketers, and educators — produce high-converting, retention-optimized scripts for videos (VSLs, YouTube, tutorials) and written marketing posts (Facebook, LinkedIn, blogs). The application guides users through a structured workflow: from collecting notes and defining an Ideal Customer Profile (ICP), through hook/narrative/retention/CTA selection, to automated script analysis (fact-checking, readability, copyright compliance, platform policy adherence). By using free-tier LLMs and APIs, the project delivers professional copywriting capabilities at zero infrastructure cost.

### Problem Statement

Creating scripts and marketing content that actually convert is a multi-disciplinary challenge. Writers must simultaneously:

- Understand their audience deeply (ICP)
- Choose compelling hooks that stop the scroll
- Structure narratives using proven patterns
- Embed retention techniques to keep audiences engaged
- Place effective calls to action
- Ensure factual accuracy, readability, copyright compliance, and platform policy adherence

Creators often have existing research, audience notes, and content stored in Google Drive or NotebookLM notebooks that could enrich their scripts, but no tool integrates these sources into the creative pipeline. Most creators approach this ad hoc, resulting in scripts that underperform on retention, conversion, or compliance. Existing AI writing tools generate generic content without the strategic scaffolding needed for high-performing scripts. There is no free, self-hosted tool that orchestrates this entire pipeline agenticly.

### Strategic Alignment

This project aligns with the following strategic goals:

| Goal | Alignment |
|------|-----------|
| Democratize professional copywriting tools | Built entirely on free LLMs/APIs — no paywall barriers |
| Reduce time-to-production for content creators | Agentic workflow automates analysis and suggestions |
| Ensure content compliance and quality | Built-in fact-checking, copyright, and policy analysis |
| Serve the developer/tech creator niche | First-class support for software-related content niches |
| Maintain lean, solo-developer operations | Zero-cost infra, self-hosted, no vendor lock-in |
| Leverage existing research and notes | NotebookLM/Google Drive integration lets creators bring their accumulated knowledge into the pipeline |

### Cost-Benefit Analysis

**Costs:**

| Category | Estimated Cost | Notes |
|----------|---------------|-------|
| Development time | ~0 (solo, no deadline) | Opportunity cost only |
| LLM API usage | $0 | Free-tier LLMs (e.g., Ollama local, Groq free tier, Google Gemini free tier) |
| Hosting | $0 | Local-first; optional free-tier cloud (e.g., Vercel, Railway free tier) |
| Infrastructure | $0 | Self-hosted, no paid SaaS |

**Benefits:**

| Benefit | Type | Impact |
|---------|------|--------|
| Higher CTA conversion rates on scripts | Tangible | Direct revenue/sales impact for users |
| Improved audience retention metrics | Tangible | Better platform algorithm ranking |
| Reduced compliance risk (copyright, platform bans) | Tangible | Avoids lost revenue from takedowns |
| Faster script production cycle | Intangible | 3–5x faster from brief to final script |
| Structured learning for students | Intangible | Transferable copywriting methodology |

**ROI:** Infinite on monetary investment (zero cost). ROI measured in time saved and conversion lift.

---

## Part 2: Project Charter (The What & How)

### Project Purpose & Objectives

**Purpose:** Build a free, agentic AI application that guides content creators through a structured, multi-step workflow to produce high-converting, compliant video scripts and marketing posts.

**SMART Objectives:**

1. **Specific:** Deliver an agentic workflow engine that takes user notes + ICP as input and outputs a polished, analyzed script.
2. **Measurable:** Reduce average script production time from 4+ hours to under 30 minutes (draft + analysis).
3. **Achievable:** Built by a solo developer using free-tier LLMs and open-source tools.
4. **Relevant:** Directly addresses the conversion and retention problems content creators face.
5. **Time-bound:** No external deadline; internal milestone-driven progression.

### Scope & Boundaries

**In Scope:**

- Note collection and organization module
- ICP analysis agent
- Hook suggestion and selection agent
- Narrative/pattern selection agent
- Retention technique recommendation agent
- CTA selection and optimization agent
- Script generation engine (video scripts + written marketing posts)
- Script analysis module (fact-checking, readability, copyright, YouTube policies)
- Support for output formats: VSL scripts, YouTube video scripts, tutorials, Facebook posts, LinkedIn posts, blog posts
- Free-tier LLM integration (local + cloud free tiers)
- Google NotebookLM integration for enriching agent context with existing research and notes
- Local-first, self-hosted deployment

**Out of Scope:**

- Video/audio production or editing
- Social media scheduling or publishing
- User authentication and multi-tenant SaaS platform
- Paid/premium LLM API tiers
- Mobile application (initial release)
- Real-time collaboration features

### Key Stakeholders

| Role | Name/Group | Responsibility |
|------|-----------|----------------|
| Project Sponsor & Developer | Solo Developer | Architecture, development, testing, deployment |
| Primary Users | Developer's students (software developers/engineers) | UAT, feedback, early adoption |
| Secondary Users | General content creators | Broader community feedback |
| Technical Advisor | Solo Developer (dual role) | Tech stack decisions, LLM selection |

### Milestone Schedule

| Phase | Milestone | Deliverable |
|-------|-----------|-------------|
| Phase 1 | Core Workflow Engine | Agentic pipeline: Notes → ICP → Hook → Narrative → Retention → CTA → Script |
| Phase 2 | NotebookLM Integration | Google NotebookLM/Drive context attachment for all creative steps |
| Phase 3 | Script Analysis Module | Fact-check, readability, copyright, policy compliance agents |
| Phase 4 | Output Format Support | VSL, YouTube, tutorial, Facebook, LinkedIn, blog templates |
| Phase 5 | LLM Integration Layer | Free-tier LLM adapter (local Ollama + cloud free tiers) |
| Phase 6 | Polish & Documentation | UI/CLI refinement, user guide, self-hosting docs |

### Budget Estimate

| Category | Amount |
|----------|--------|
| Development | $0 (solo, no salary allocation) |
| LLM/API costs | $0 (free tiers only) |
| Hosting | $0 (local-first) |
| Tooling | $0 (open-source) |
| **Total** | **$0** |

### Initial Risk Log

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R1 | Free-tier LLM rate limits slow down agentic pipeline | High | Medium | Implement request queuing; support multiple free-tier providers for failover |
| R2 | LLM output quality inconsistent across providers | Medium | High | Prompt engineering standards; output validation agents; human-in-the-loop review step |
| R3 | Copyright/policy analysis produces false positives | Medium | Medium | Present analysis as advisory, not authoritative; allow user override |
| R4 | Scope creep from adding more output formats | Medium | Low | Strict format backlog prioritization; community-driven feature requests |
| R5 | Solo developer burnout / motivation loss | Medium | High | No external deadlines; milestone-based pacing; ship MVP first |
| R6 | Google NotebookLM API changes or rate limits | Low | Medium | Use official Google Cloud API; graceful degradation when unavailable; manual notes input as fallback |

### Success Criteria

1. A user can go from raw notes + ICP description to a complete, analyzed script in under 30 minutes.
2. Generated scripts pass all 4 analysis checks (fact-check, readability, copyright, policy) with < 10% false positive rate.
3. The application runs entirely on free-tier infrastructure with no mandatory paid services.
4. At least 3 output formats are supported (VSL, YouTube, blog/marketing post).
5. The agentic workflow is modular — each agent can be used independently or as part of the full pipeline.
