# GoodReadsDigest — Concept Document

## Elevator Pitch

GoodReadsDigest analyzes Goodreads reviews for a given book, surfacing sentiment patterns, common phrases, and key concepts so readers can quickly understand what people love, hate, and talk about — without reading hundreds of reviews.

---

## Problem Space

Goodreads books can have hundreds or thousands of reviews. Readers who want to understand the general reception of a book face a tedious process of scrolling through reviews, mentally tallying opinions, and trying to spot patterns. There's no easy way to get a structured, at-a-glance summary of what reviewers collectively think.

## Target Users

Readers who want a quick, structured understanding of a book's reception before committing time to reading it (or to validate their own experience after reading).

---

## Core Functionality

1. **Book Search** — User enters a book title, system returns matching books from Goodreads.
2. **Review Fetching** — Scrape reviews for the selected book (capped at N reviews for PoC, e.g., 50–100 — TBD based on scraping feasibility).
3. **Star Rating Filter** — Optionally narrow reviews to a specific star rating before analysis.
4. **Sentiment Analysis** — Classify sentiment across reviews (positive/negative/neutral, with frequency counts).
5. **Common Phrase Extraction** — Identify frequently recurring phrases across the review set.
6. **Concept/Theme Identification with Sentiment Correlation** — Extract key topics and themes, with each theme showing:
   - A sentiment breakdown (e.g., "Pacing — 70% negative, 30% positive")
   - Representative review snippets illustrating the sentiment
7. **Results Display** — Present all findings in a single results view.

---

## PoC Feature List

These are the minimum features required for a usable proof-of-concept:

- [ ] Book search by title
- [ ] Select a book from search results
- [ ] Optional star rating filter
- [ ] Fetch up to N reviews (cap TBD based on scraping feasibility)
- [ ] Sentiment breakdown with counts (positive/negative/neutral)
- [ ] Top common phrases with frequency
- [ ] Top concepts/themes with sentiment correlation and representative snippets
- [ ] Single results page displaying all analysis
- [ ] Ability to go back and search again

---

## Out of Scope (PoC)

The following are explicitly **not** part of the proof-of-concept:

- User accounts / authentication
- Saving past analyses or history
- Comparing multiple books side-by-side
- Export (PDF, CSV, etc.)
- Custom analysis parameters / tuning
- Mobile-responsive design
- Deployment / hosting infrastructure
- Caching or persistence of scraped data
- Full cross-referencing (linking themes back to individual reviews)

---

## User Flow

```
Search for book → Select from results → (Optional) Pick star rating filter
    → System fetches reviews → System analyzes reviews
    → Results page: sentiments, phrases, themes with correlated sentiment + snippets
    → User can go back and search again
```

---

## Constraints

| Constraint | Value |
|-----------|-------|
| Platform | Web app, run locally for PoC |
| Backend | Python + FastAPI |
| Frontend | React + TypeScript |
| NLP | Python ecosystem (specific library TBD in Phase 3) |
| Data access | Web scraping (Goodreads API retired) |
| Database | None for PoC (in-memory processing) |
| Scope | Single user, local only |

---

## Future Considerations

Promising features to explore after the PoC is validated:

- **Author or series-level analysis** — Aggregate and analyze reviews across all books by an author or within a series, surfacing patterns in reception over time or across works.
- **Full cross-referencing** — Link each identified theme back to the individual reviews that contributed, allowing users to drill down from a theme to the source material.

---

## Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| D1 | Web app run locally (not desktop-first) | Zero refactoring to deploy later; no OS-level access needed; localhost is functionally a desktop experience | 2026-02-20 |
| D2 | Python + FastAPI backend | Best NLP ecosystem; FastAPI is lightweight and async | 2026-02-20 |
| D3 | React + TypeScript frontend | User preference; strong typing; widely supported | 2026-02-20 |
| D4 | Web scraping for Goodreads data | Goodreads API has been retired | 2026-02-20 |
| D5 | No database for PoC | Keep it simple; in-memory processing sufficient for PoC | 2026-02-20 |
| D6 | Correlate sentiment with themes | Richer output; each theme shows sentiment breakdown + representative snippets | 2026-02-20 |
| D7 | Theme-level sentiment + snippets for PoC, full cross-referencing deferred | Start with useful output, add drill-down capability later | 2026-02-20 |
