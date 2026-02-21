# CLAUDE.md — Session Context

## Project

**GoodReadsDigest** — A web app that analyzes Goodreads reviews for a given book, surfacing sentiment patterns, common phrases, and key concepts so readers can quickly understand what reviewers think without reading hundreds of reviews.

## Tech Stack

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript
- **NLP:** Python ecosystem (specific library TBD in Phase 3)
- **Data access:** Web scraping (Goodreads API is retired)
- **Database:** None for PoC (in-memory processing)
- **Platform:** Web app, run locally for PoC

## Current Status

**Phase:** 2 — Concept Selection & Definition (Complete)
**Next:** Phase 3 — Technical Design & Work Planning

Phases 1 and 2 are complete. `CONCEPT.md` defines the full PoC scope.

## Key Documents

| Document | Status | Purpose |
|----------|--------|---------|
| `DEV_PROCESS.md` | Active | Development process, phase checklists, current status |
| `CONCEPT.md` | Complete | Core functionality, PoC scope, out-of-scope, user flow, decisions |
| `CHAT_LOG.md` | Active | Full conversation history — update after each session |
| `BRANCHING_STRATEGY.md` | Complete | Feature branching off `main` |

## Process Rules (Key Reminders)

- Follow `DEV_PROCESS.md` — stay in phase, produce outputs before moving on.
- All work in Phases 4–5 is tracked in `BACKLOG.md` as work items. No untracked work.
- Use feature branches for all work (no direct commits to `main` after initial setup).
- Update `CHAT_LOG.md` with conversation history at the end of each session.
- Update `DEV_PROCESS.md` current status when completing work items or transitioning phases.
- Record decisions in the decision log of the relevant document (`CONCEPT.md` for scope, `TECH_DESIGN.md` for technical).

## Git

- **Remote:** https://github.com/keithPHBC/GoodReadsDigest
- **Branch strategy:** Feature branching — see `BRANCHING_STRATEGY.md`
- Commit regularly. One work item per branch/PR (Phases 4–5).
