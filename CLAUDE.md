# CLAUDE.md — Session Context

## Project

**GoodReadsDigest** — A web app that analyzes Goodreads reviews for a given book, surfacing sentiment patterns, common phrases, and key concepts so readers can quickly understand what reviewers think without reading hundreds of reviews.

## Tech Stack

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript
- **Scraping:** Playwright + BeautifulSoup4
- **Sentiment:** VADER (vaderSentiment)
- **Phrase extraction:** spaCy + scikit-learn TF-IDF
- **Theme identification:** scikit-learn NMF
- **Data access:** Web scraping (Goodreads API is retired)
- **Database:** None for PoC (in-memory processing)
- **Platform:** Web app, run locally for PoC

## Current Status

**Phase:** 3 — Technical Design & Work Planning (In Progress — spike remaining)
**Next:** Execute SPIKE-1 and SPIKE-2 to validate Goodreads scraping, then move to Phase 4.

Phases 1-2 are complete. Phase 3 design and backlog are done; the Goodreads scraping spike is the last deliverable.

## Key Documents

| Document | Status | Purpose |
|----------|--------|---------|
| `DEV_PROCESS.md` | Active | Development process, phase checklists, current status |
| `CONCEPT.md` | Complete | Core functionality, PoC scope, out-of-scope, user flow, decisions |
| `CHAT_LOG.md` | Active | Full conversation history — update after each session |
| `BRANCHING_STRATEGY.md` | Complete | Feature branching off `main` |
| `TECH_DESIGN.md` | Complete | Architecture, library choices, project structure, data model, risks |
| `BACKLOG.md` | Active | Epics: SPIKE, SCRAPER, ANALYSIS, API, UI — all work items for Phases 3-5 |

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
