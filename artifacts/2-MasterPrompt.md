# The AI Project Discovery & Spec-Driven Design Master Prompt

## Analysis, Breakdown & Enhancement Suggestions

**Version:** 1.1 (Annotated)
**Date:** June 2026

---

## 1. What This Prompt Does

This is a **7-phase, role-stacked mega-prompt** that transforms a raw project idea into a complete, implementation-ready documentation package. It instructs an AI to act simultaneously as:

> Senior Business Analyst · Enterprise Solution Architect · Technical Product Manager · Software Architect · DevOps Architect · Security Architect · AI Engineering Lead

Rather than asking for a single document, the prompt **chains 7 sequential phases**, each gated by the previous, and produces **9 specification artifacts** that collectively drive both human engineers and AI coding assistants.

---

## 2. Prompt Structure — Phase by Phase

```
PHASE 1 → PHASE 2 → PHASE 3 → PHASE 4 → PHASE 5 → PHASE 6 → PHASE 7
Discovery    BRD     Arch Q&A   5 Docs    Plan      AI Prompt  Mgmt
```

### Phase 1 — Requirements Discovery

**Instruction:** Ask interactive questions. Do NOT generate documents yet. Group questions by category. Only ask highest-priority unanswered questions.

**Categories covered:**

- Business Information (goals, stakeholders, budget, timeline)
- Functional Requirements (features, roles, workflows, integrations)
- Non-Functional Requirements (scalability, security, compliance, performance)
- AI Requirements (LLM, RAG, agents, fine-tuning, evaluation)
- Deployment Requirements (cloud, on-premise, DR, backup)

**Output:** A complete set of answered requirements — no artifact yet.

---

### Phase 2 — BRD Generation

**Instruction:** Generate `/artifacts/BRD.md` using professional enterprise-grade formatting.

**Sections mandated:**
Executive Summary · Business Objectives · Scope (In/Out) · Stakeholders · User Personas · Functional Requirements · Non-Functional Requirements · Assumptions · Risks · Dependencies · Acceptance Criteria · Success Metrics · Roadmap

**Output:** `BRD.md`

---

### Phase 3 — Architecture Discovery

**Instruction:** Ask interactive architecture questions. Cover style, frontend, backend, database, AI components, infrastructure, security, observability, CI/CD.

**Decisions forced:**

- Architecture style (monolith → microservices → serverless)
- Framework selection (frontend + backend)
- API style (REST / GraphQL / gRPC)
- Database type (SQL / NoSQL / Vector / Time Series)
- LLM + embedding model + vector DB choices
- Auth / secrets / SSO / MFA
- Logging / monitoring / tracing / alerting
- Git strategy + CI/CD tooling

**Output:** A complete set of answered architecture decisions — no artifact yet.

---

### Phase 4 — System Design Documents (5 artifacts)

**Instruction:** Generate 5 markdown files with Mermaid diagrams wherever possible.

| Artifact                  | Key Contents                                                                                                          |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `SystemArchitecture.md` | Context · Container · Component · Deployment · Data Flow · Integration · Security · HA · Scalability diagrams |
| `DatabaseDesign.md`     | ERD · Table definitions · Index strategy · Partitioning · Retention · Mermaid ER diagrams                        |
| `API_Specification.md`  | All endpoints · Request/Response · Validation · Auth · Error handling · OpenAPI-compatible                       |
| `SecurityDesign.md`     | Threat model · STRIDE · Security controls · IAM · Encryption · Audit logging · Compliance                       |
| `DevOpsDesign.md`       | CI/CD architecture · Environments · Deployment · Rollback · Monitoring · Logging · DR                           |
| `TestStrategy.md`       | Unit · Integration · E2E · Performance · Security · UAT strategies                                               |

**Output:** 6 artifacts (SystemArchitecture + 5 supporting docs)

---

### Phase 5 — Project Execution Plan

**Instruction:** Generate `/artifacts/ExecutionPlan.md` with full implementation roadmap.

**Required elements:**
Milestones · Epics · Features · Tasks · Dependencies · Risks · Resource Requirements · Estimated Effort · Delivery Sequence · Critical Path

**Output:** `ExecutionPlan.md`

---

### Phase 6 — AI Coding Assistant Implementation Prompt

**Instruction:** Generate `/artifacts/AI_Implementation_Prompt.md` optimised for Cursor, Claude Code, Cline, Roo Code, Windsurf, GitHub Copilot Agent, OpenAI Codex.

**Required sections:**
Project Context · Referenced Documents · Development Rules · Coding Standards · Architecture Constraints · Implementation Phases · Validation Gates · Testing Requirements · Deliverables · Definition of Done

**Output:** `AI_Implementation_Prompt.md`

---

### Phase 7 — Artifact Management

**Instruction:** Maintain consistency across all artifacts. When information is missing, ask questions and update impacted documents. Never assume critical requirements.

**Ongoing rules:**

- All outputs as markdown files
- Maintain `/artifacts/` directory structure
- Cross-update when any artifact changes
- Never assume — always validate

---

## 3. Full Artifact Output Map

```
/artifacts/
├── BRD.md                      ← Phase 2  (197 lines)
├── SystemArchitecture.md       ← Phase 4  (309 lines)
├── DatabaseDesign.md           ← Phase 4  (239 lines)
├── API_Specification.md        ← Phase 4  (304 lines)
├── SecurityDesign.md           ← Phase 4  (171 lines)
├── DevOpsDesign.md             ← Phase 4  (288 lines)
├── TestStrategy.md             ← Phase 4  (280 lines)
├── ExecutionPlan.md            ← Phase 5  (154 lines)
└── AI_Implementation_Prompt.md ← Phase 6  (275 lines)

Total: 9 files · 2,217 lines
```

---

## 4. What Makes This Prompt Powerful

| Strength                           | Why It Works                                                                                         |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Role stacking**            | 7 expert roles in one session eliminates handoff gaps between BA, architect, security, DevOps        |
| **Sequential gating**        | Each phase requires the previous — no architecture before requirements, no code before architecture |
| **Interactive discovery**    | Phases 1 and 3 ask questions instead of assuming — prevents the most common failure mode            |
| **Mermaid-first diagrams**   | Machine-readable diagrams that render in GitHub, Notion, and VS Code — not static images            |
| **AI-coding-tool optimised** | Phase 6 output is specifically structured as system context for Cursor/Claude Code/Cline             |
| **Living document system**   | Phase 7 enforces consistency — changing one artifact triggers updates to all impacted ones          |
| **Security-by-design**       | SecurityDesign.md is Phase 4 — security is specified before a single line of code                   |

---

## 5. Enhancement Suggestions

The following improvements would make the prompt more robust, more precise, and better suited to production-grade AI-assisted development.

---

### 5.1 Add an Explicit Validation Gate Between Each Phase

**Current:** Phases flow implicitly — the AI moves to the next phase after completing the current one.

**Enhancement:** Add a mandatory sign-off instruction between each phase:

```markdown
## PHASE GATE RULE (add to prompt)
After completing each phase, output:
---
✅ PHASE [N] COMPLETE
Artifacts produced: [list]
Pending decisions: [list any unresolved items]
⏸ WAITING FOR HUMAN APPROVAL before proceeding to Phase [N+1]
---
Do NOT proceed to the next phase until the user explicitly says "approved" or "proceed".
```

**Why:** Prevents the AI from making silent assumptions when requirements are ambiguous. Gives the team a checkpoint to course-correct before downstream artifacts are generated.

---

### 5.2 Add an ADR (Architecture Decision Record) Artifact

**Current:** Architecture decisions are embedded in SystemArchitecture.md but not explicitly tracked as decisions.

**Enhancement:** Add to Phase 4:

```markdown
/artifacts/ADR.md
## Architecture Decision Records

For each major decision, document:
- ADR-001: Title
- Status: Proposed | Accepted | Deprecated | Superseded
- Context: Why this decision was needed
- Decision: What was decided
- Rationale: Why this option over alternatives
- Consequences: What becomes easier/harder
- Alternatives considered: [list with reasons rejected]
```

**Why:** ADRs make the reasoning behind technical choices explicit. When the team revisits a decision 3 months later, they know WHY LiteLLM was chosen over a custom router — and whether those reasons still apply.

---

### 5.3 Explicit Token Budget / Context Window Guidance

**Current:** No instruction on how to handle long requirements or large existing codebases.

**Enhancement:** Add to the prompt header:

```markdown
## CONTEXT MANAGEMENT RULES
- If requirements exceed what fits in one session, produce a REQUIREMENTS_SUMMARY.md
  (max 500 words) at the end of Phase 1 that future sessions can load as compressed context.
- Reference artifacts by filename, not by re-pasting their content, in subsequent phases.
- If a single artifact would exceed 500 lines, split into sub-documents:
  SystemArchitecture_Overview.md + SystemArchitecture_Diagrams.md
```

**Why:** For large projects, artifact files can exceed context window limits when loaded together into Cursor or Claude Code. This guidance prevents truncation failures.

---

### 5.4 Data Flow & Privacy Classification Step to Phase 1

**Current:** Privacy and compliance are covered in NFRs (Phase 1) and SecurityDesign (Phase 4), but data classification is not explicitly elicited.

**Enhancement:** Add to Phase 1 questions:

```markdown
## Data Classification Questions (add to Phase 1)
- What data does the system store, process, or transmit?
- Does any data qualify as PII, PHI, PCI, or government-classified?
- Which jurisdictions apply (GDPR, CCPA, HIPAA, PDPA)?
- What is the data retention requirement per data type?
- Who is permitted to access each data category?
```

**Why:** Data classification in Phase 1 propagates into SecurityDesign, DatabaseDesign (retention policies), and API_Specification (what fields to redact). Without it, security and DB docs are incomplete.

---

### 5.5 "Proof of Concept" Fast-Track Mode

**Current:** The prompt always produces the full 9-artifact set — appropriate for production projects, but heavyweight for exploratory POCs.

**Enhancement:** Add a mode selector at the top:

```markdown
## PROJECT MODE (add to prompt preamble)
Before starting Phase 1, ask:
"Is this project a (1) Production System, (2) Proof of Concept, or (3) Research Spike?"

- Production → full 7-phase process, all 9 artifacts
- POC        → Phase 1 (lite) + SystemArchitecture (overview only) + ExecutionPlan (2-week scope)
- Spike      → Phase 1 (3 questions max) + a single SPIKE_FINDINGS.md
```

**Why:** Applying the full 7-phase process to a 2-day spike wastes effort. The mode selector makes the prompt useful across the full project lifecycle, not just green-field production builds.

---

### 5.6 Strengthen the AI Coding Prompt (Phase 6) with Explicit Persona Injection

**Current:** Phase 6 specifies what the coding assistant should do but not HOW to frame itself.

**Enhancement:** Add to Phase 6 output template:

```markdown
## AI ASSISTANT PERSONA (add to AI_Implementation_Prompt.md)
You are a Senior Software Engineer implementing [project name].
You have already read and internalized:
- The business requirements (BRD.md)
- The system architecture (SystemArchitecture.md)
- The security requirements (SecurityDesign.md)
- The test strategy (TestStrategy.md)

You never guess requirements. You never invent architecture decisions.
When uncertain, you say: "This is not specified in the artifacts. Please clarify before I proceed."
You write production-ready code. You write tests alongside implementation.
You stop at every validation gate and wait for human confirmation.
```

**Why:** Persona injection significantly improves coding assistant consistency. The assistant stops "filling gaps" with assumptions and instead surfaces ambiguity explicitly.

---

### 5.7 Glossary Artifact

**Current:** Domain-specific terms (RAG, ChromaDB, LiteLLM, SSE) appear across all artifacts without a shared definition source.

**Enhancement:** Add to Phase 2 (alongside BRD):

```markdown
/artifacts/Glossary.md
## Project Glossary
| Term | Definition | First Used In |
|------|-----------|---------------|
| RAG | Retrieval-Augmented Generation — technique of grounding LLM responses in retrieved documents | BRD.md |
| SSE | Server-Sent Events — HTTP streaming protocol used for token-by-token LLM output | SystemArchitecture.md |
| ...  | ... | ... |
```

Reduces ambiguity across a multi-person team. When onboarding a new developer, the Glossary is the first document they read.

---
