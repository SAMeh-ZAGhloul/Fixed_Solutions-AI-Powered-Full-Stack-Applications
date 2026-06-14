# The AI Project Discovery & Spec-Driven Design Master Prompt

## Analysis, Breakdown & Enhancement Suggestions

**Version:** 1.1
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
├── BRD.md                      ← Phase 2 
├── SystemArchitecture.md       ← Phase 4  
├── DatabaseDesign.md           ← Phase 4  
├── API_Specification.md        ← Phase 4  
├── SecurityDesign.md           ← Phase 4  
├── DevOpsDesign.md             ← Phase 4  
├── TestStrategy.md             ← Phase 4  
├── ExecutionPlan.md            ← Phase 5  
└── AI_Implementation_Prompt.md ← Phase 6  

Total: 9 files 
```

---
