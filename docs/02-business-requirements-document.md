# Business Requirements Document – Scripts Writer

## Project Overview

Scripts Writer is an agentic AI application that transforms raw notes and audience insights into high-converting, retention-optimized scripts for videos and marketing posts. The product enforces a structured creative methodology — ICP analysis → hook selection → narrative pattern → retention techniques → CTA optimization → compliance analysis — that professional copywriters use manually. By packaging this methodology into an autonomous, LLM-powered pipeline, Scripts Writer eliminates the ad hoc approach most creators take, producing scripts that convert, retain audiences, and pass compliance checks.

The vision is a free, self-hosted, local-first tool that any content creator can run without paid services, with particular depth for the software developer/tech creator niche.

## Business Objectives

| ID | Objective | Metric | Target |
|----|-----------|--------|--------|
| BO-1 | Reduce script production time | Time from notes to final script | < 30 minutes (from 4+ hours manual) |
| BO-2 | Increase CTA conversion rates | Click-through / action rate on CTAs | 2x improvement vs. unstructured writing |
| BO-3 | Improve audience retention | Average watch/read percentage | 15% improvement vs. baseline |
| BO-4 | Eliminate compliance violations | Copyright/policy flags per script | < 5% of published content flagged |
| BO-5 | Zero operating cost | Monthly infrastructure spend | $0 |
| BO-6 | Enable structured learning | Students who can reproduce the methodology | 80% of students apply workflow independently after 2 uses |

## Target Audience / User Personas

### Primary Persona: Tech Content Creator (The Developer-Educator)

| Attribute | Detail |
|-----------|--------|
| **Name** | "DevCreator" |
| **Role** | Software developer who creates educational/marketing content |
| **Goals** | Grow audience, sell courses/products, establish authority |
| **Pain Points** | Writes technical content that's accurate but boring; struggles with hooks and retention; doesn't know copywriting frameworks |
| **Content Types** | YouTube tutorials, VSLs for courses, LinkedIn posts, blog articles |
| **Tech Savviness** | High — comfortable with CLI, self-hosting, APIs |

### Secondary Persona: General Marketing Creator

| Attribute | Detail |
|-----------|--------|
| **Name** | "MarketingMark" |
| **Role** | Solo marketer or small business owner |
| **Goals** | Create converting video scripts and social posts without hiring copywriters |
| **Pain Points** | No copywriting training; produces generic content; fears copyright strikes and platform bans |
| **Content Types** | Facebook ads, VSLs, YouTube shorts, blog posts |
| **Tech Savviness** | Medium — can follow setup guides, prefers GUI |

### Tertiary Persona: Student Learner

| Attribute | Detail |
|-----------|--------|
| **Name** | "StudentSam" |
| **Role** | Learner in the developer's cohort/course |
| **Goals** | Learn structured copywriting methodology; practice by generating scripts |
| **Pain Points** | Overwhelmed by copywriting theory; needs guided practice |
| **Content Types** | Practice scripts, LinkedIn posts, tutorial scripts |
| **Tech Savviness** | Varies — needs clear onboarding |

## Business Process Mapping

### As-Is Process (Current Manual Workflow)

```
1. Creator opens blank document
2. Brainstorms ideas unstructured
3. Writes first draft from memory/intuition
4. Manually reviews for typos
5. Publishes without compliance check
6. Monitors performance → guesses at improvements
7. Repeats with inconsistent results
```

**Problems:** No ICP anchoring, no hook strategy, no retention engineering, no compliance verification, no systematic improvement loop.

### To-Be Process (Scripts Writer Workflow)

```
1. Creator enters raw notes + topic/context
2. [ICP Agent] Analyzes and defines Ideal Customer Profile
3. [Hook Agent] Suggests hooks tailored to ICP; creator selects
4. [Narrative Agent] Suggests narrative patterns; creator selects
5. [Retention Agent] Recommends retention techniques for chosen format
6. [CTA Agent] Suggests and optimizes call-to-action; creator selects
7. [Writer Agent] Generates full script draft based on all selections
8. [Analysis Agents] Run automated checks:
   a. Fact-checking agent
   b. Readability & typo agent
   c. Copyright compliance agent
   d. Platform policy agent (YouTube, etc.)
9. Creator reviews analysis, revises if needed
10. Exports final script in target format
```

**Improvements:** Structured methodology enforced by agents, data-driven selections, automated compliance, consistent output quality.

## High-Level Functional Needs

| ID | Capability | Business Value |
|----|-----------|----------------|
| FN-1 | **Note & Context Collection** — Capture raw notes, topic, audience, goals | Ensures scripts are grounded in creator's intent, not generic |
| FN-2 | **ICP Analysis Engine** — Analyze and define target audience characteristics | Hooks and narratives are tailored, not generic |
| FN-3 | **Hook Suggestion & Selection** — Generate and rank hooks based on ICP | First 3–5 seconds optimized for stop-the-scroll |
| FN-4 | **Narrative Pattern Selection** — Offer proven frameworks (PAS, AIDA, Story Loop, etc.) | Scripts follow conversion-optimized structures |
| FN-5 | **Retention Technique Recommendation** — Suggest pattern interrupts, open loops, etc. | Keeps audience engaged through full content |
| FN-6 | **CTA Optimization** — Suggest and optimize calls-to-action | Maximizes conversion from viewer to customer |
| FN-7 | **Multi-Format Script Generation** — VSL, YouTube, tutorial, Facebook, LinkedIn, blog | One pipeline, many output formats |
| FN-8 | **Fact-Checking Analysis** — Verify claims and data in script | Protects credibility and avoids misinformation |
| FN-9 | **Readability & Typos Analysis** — Check understandability and correctness | Ensures professional quality |
| FN-10 | **Copyright Compliance Analysis** — Flag potential copyright issues | Avoids DMCA takedowns and legal risk |
| FN-11 | **Platform Policy Analysis** — Check against YouTube, Facebook, LinkedIn policies | Avoids content removal and account penalties |
| FN-12 | **Free-Tier LLM Integration** — Run entire pipeline on $0 infrastructure | Democratizes access; no paywall |
| FN-13 | **Local-First / Self-Hosted Deployment** — Run without cloud dependency | Privacy, control, zero cost |

## Financial / Operational Constraints

| Constraint | Detail |
|-----------|--------|
| **Budget** | $0 — no paid services, APIs, or hosting |
| **Team** | Solo developer (owner, architect, developer, tester) |
| **LLM Provider** | Free-tier only — Ollama (local), Groq free tier, Google Gemini free tier, or similar |
| **Deadline** | None — milestone-driven, self-paced |
| **Infrastructure** | Local machine primarily; optional free-tier cloud for web access |
| **Regulatory** | Copyright law, platform ToS (YouTube, Facebook, LinkedIn) must be respected by the tool |
| **Legacy Systems** | None — greenfield project |
| **Scalability** | Single-user initially; not designed for concurrent multi-user SaaS |

## Glossary

| Term | Definition |
|------|-----------|
| **Agentic** | An AI system where autonomous agents perform tasks in sequence or parallel, each with a specific role |
| **ICP** | Ideal Customer Profile — a detailed description of the target audience for a piece of content |
| **Hook** | The opening of a script/post designed to capture attention in the first 3–5 seconds |
| **VSL** | Video Sales Letter — a long-form video designed to sell a product or service |
| **CTA** | Call To Action — the part of a script that directs the audience to take a specific action |
| **Retention** | The ability to keep an audience engaged throughout the content |
| **PAS** | Problem-Agitate-Solution — a copywriting framework |
| **AIDA** | Attention-Interest-Desire-Action — a copywriting framework |
| **Narrative Pattern** | A structured storytelling framework used to organize a script |
| **Open Loop** | A storytelling technique where a question or tension is introduced but resolved later |
| **Pattern Interrupt** | A technique to break audience autopilot by introducing unexpected elements |
| **LLM** | Large Language Model — an AI model capable of generating and analyzing text |
| **ToS** | Terms of Service — platform rules governing content |
| **DMCA** | Digital Millennium Copyright Act — US copyright law |
