# Software Development Process: Idea to Proof-of-Concept

## Phase 1: Brainstorm & Discovery

**Goal:** Generate and explore ideas without filtering.

- [x] Define constraints upfront (platform, tech stack, scope limits)
- [x] Brainstorm core product concepts (problem space, target users, value proposition)
- [x] Identify the "core workflow" — what does the user do repeatedly?
- [x] List reference products / inspirations
- [x] Write a 1-2 sentence elevator pitch for top candidates

**Output:** A short list of candidate ideas with elevator pitches.

---

## Phase 2: Concept Selection & Definition

**Goal:** Pick one idea and define it clearly enough to build.

- [x] Evaluate candidates against constraints (feasibility, scope, usefulness)
- [x] Select one concept
- [x] Define the core functionality in concrete terms
- [x] Identify the minimum set of features for a usable proof-of-concept
- [x] List what is explicitly OUT of scope for the PoC
- [x] Sketch the user flow (input → processing → output)

**Output:** A concept document (`CONCEPT.md`) with functionality definition, PoC feature list, and scope boundaries.

---

## Phase 3: Technical Design & Work Planning

**Goal:** Make implementation decisions and break the work into deliverable items.

- [x] Choose framework/libraries and justify the choice
- [x] Define the project structure
- [x] Identify core systems needed (data access, business logic, UI, etc.)
- [x] Plan the data model (entities, state shape)
- [x] Identify the riskiest technical unknowns
- [x] Prototype the riskiest unknown first (spike) — SPIKE-1 passed, SPIKE-2 partial (see BACKLOG.md)
- [x] Create the product backlog (see Work Item Structure below)

**Output:**
- A technical design doc (`TECH_DESIGN.md`) and a working spike for the biggest risk.
- A product backlog (`BACKLOG.md`) with epics and work items covering Phases 4–5.

---

## Phase 4: Core Functionality Prototype

**Goal:** Get the core workflow functional with minimal UI/polish.

Work is driven by backlog items from the relevant epics.

- [ ] Implement the core functionality — nothing else
- [ ] Use placeholder or minimal UI (plain text, basic layout, no styling)
- [ ] Make it interactive (user input → visible response)
- [ ] Test: Does the core workflow *work* and *feel useful* with zero polish?
- [ ] Iterate on usability based on testing

**Output:** A runnable build where the core functionality works and can be evaluated.

---

## Phase 5: Proof-of-Concept Build

**Goal:** Expand the prototype into something that demonstrates the full idea.

Work is driven by backlog items from the relevant epics.

- [ ] Add remaining PoC-scoped features
- [ ] Implement basic user flow (start → use → complete task → repeat)
- [ ] Add minimal UI (navigation, status indicators, basic layout — whatever applies)
- [ ] Basic error handling and user feedback
- [ ] Bug fixing pass
- [ ] Final testing and evaluation

**Output:** A usable proof-of-concept that answers: "Is this product worth developing further?"

---

## Work Item Structure

All implementation work (Phases 4–5) is organized into **epics** and **work items** following agile conventions.

### Epic

A thematic grouping of related work items that delivers a meaningful slice of functionality.

```
### Epic: [EPIC-ID] — [Title]

**Goal:** [What this epic achieves]
**Phase:** [4 or 5]
**Status:** [Not Started | In Progress | Done]
```

### Work Item

Each work item lives under an epic and follows this template:

```
#### [EPIC-ID]-[NUM]: [Title]

**Type:** [Feature | Spike | Bug | Chore]
**Status:** [To Do | In Progress | Done]
**Priority:** [Must Have | Should Have | Nice to Have]

**Description:**
[What needs to be built and why. Enough context that someone could pick this up cold.]

**Acceptance Criteria:**
- [ ] [Specific, testable condition that must be true when this item is done]
- [ ] [Another condition]
- [ ] ...

**Notes:**
[Optional. Dependencies, open questions, technical considerations.]
```

### Field Definitions

| Field | Purpose |
|-------|---------|
| **Type** | *Feature* = new functionality. *Spike* = research/prototype to reduce uncertainty. *Bug* = defect fix. *Chore* = tech debt, refactoring, tooling. |
| **Priority** | *Must Have* = PoC is broken without it. *Should Have* = important but PoC is usable without it. *Nice to Have* = only if time allows. |
| **Acceptance Criteria** | The definition of done. Each criterion is a concrete, verifiable statement. If all boxes are checked, the item is complete. |

### Backlog Rules

1. Every work item belongs to exactly one epic.
2. Work items are small enough to complete in a single focused session.
3. Acceptance criteria are written before implementation begins.
4. Items are worked in priority order (Must Have → Should Have → Nice to Have).
5. New items discovered during implementation get added to the backlog, not silently built.

---

## Supporting Documents

These documents should be created alongside the process and maintained throughout development:

| Document | Purpose | Created In |
|----------|---------|------------|
| `CONCEPT.md` | Product concept, PoC scope, scope boundaries, concept decision log | Phase 2 |
| `TECH_DESIGN.md` | Framework choice, project structure, data model, technical decision log | Phase 3 |
| `BACKLOG.md` | Epics and work items with acceptance criteria | Phase 3 |
| `BRANCHING_STRATEGY.md` | Git workflow and branch naming conventions | Phase 3 |
| `TEST_LOG.md` | Timestamped testing observations linked to work items and commits | Phase 4 |
| `CHAT_LOG.md` | Timestamped record of development conversations and decisions | Phase 1 |
| `CLAUDE.md` | Auto-loaded session context for cross-session continuity | Phase 3 |

---

## Process Rules

1. **Stay in phase.** Don't jump ahead. Each phase has a clear output — produce it before moving on.
2. **Scope is sacred.** If it's not on the PoC feature list, it doesn't go in.
3. **Test early.** The core functionality prototype (Phase 4) is the most important checkpoint. If it's not useful with minimal UI, polish won't save it.
4. **Kill bad ideas fast.** It's fine to go back to Phase 2 and pick a different concept if the prototype doesn't work.
5. **Track decisions.** When a decision is made (in conversation, PR review, or testing), record it in the decision log of the relevant document before the PR is opened. Concept/scope decisions go in `CONCEPT.md`, technical decisions in `TECH_DESIGN.md`, process decisions in `DEV_PROCESS.md`.
6. **Work from the backlog.** In Phases 4–5, all work is tracked as work items. No untracked work.
7. **Log every test session.** After each test session, record observations and actions in `TEST_LOG.md` before opening the PR. Link to work items and commits.
8. **Update current status.** Update the Current Status section in this doc when completing a work item or transitioning between phases.
9. **One work item per PR.** Keep work items small and self-contained enough that each one is independently testable and mergeable.

---

## Current Status

**Phase:** 3 — Technical Design & Work Planning
**Status:** Complete

### Phase History

| Phase | Status | Date |
|-------|--------|------|
| 1 — Brainstorm & Discovery | Complete | 2026-02-20 |
| 2 — Concept Selection & Definition | Complete | 2026-02-20 |
| 3 — Technical Design & Work Planning | Complete | 2026-02-21 |
