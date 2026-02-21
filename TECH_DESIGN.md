# GoodReadsDigest — Technical Design

## Architecture Overview

Web application with a Python backend (FastAPI) and React + TypeScript frontend, run locally for the PoC. The backend handles Goodreads scraping and NLP analysis; the frontend provides the search and results UI.

---

## Technology Choices

| Component | Choice | Justification |
|-----------|--------|---------------|
| Backend framework | **FastAPI** | Lightweight, async-native, automatic OpenAPI docs, Pydantic integration for data validation |
| Frontend framework | **React + TypeScript** | User preference; strong typing; large ecosystem; easy to extend later |
| Web scraping | **Playwright + BeautifulSoup4** | Goodreads is a React SPA with Cloudflare/DataDome protection — browser automation is required. Playwright handles JS rendering and stealth; BeautifulSoup parses the rendered HTML |
| Sentiment analysis | **VADER (vaderSentiment)** | Purpose-built for review/opinion text; no training data needed; fast and lightweight; outperforms TextBlob on informal review text |
| Phrase extraction | **spaCy (noun chunks) + scikit-learn (TF-IDF n-grams)** | spaCy provides linguistically meaningful phrases per review; scikit-learn TF-IDF surfaces the most distinctive phrases across the corpus |
| Theme identification | **scikit-learn (NMF with TF-IDF)** | Fast, deterministic, interpretable topics; no extra dependencies; NMF produces more coherent topics than LDA on shorter documents like reviews |
| Data validation | **Pydantic** | Included with FastAPI; defines request/response schemas |
| Database | **None (PoC)** | In-memory processing only; no persistence needed for PoC |

### Future Upgrade Path

- **BERTopic / KeyBERT** for higher-quality theme and keyphrase extraction (requires PyTorch — deferred to post-PoC)
- **Database (SQLite or PostgreSQL)** for caching scraped reviews and analysis results
- **Redis** for job queuing if analysis becomes long-running

---

## Project Structure

```
GoodReadsDigest/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routers/
│   │   │   ├── books.py         # Book search endpoint
│   │   │   └── analysis.py      # Review analysis endpoint
│   │   ├── scraper/
│   │   │   └── goodreads.py     # Playwright-based Goodreads scraper
│   │   ├── analysis/
│   │   │   ├── sentiment.py     # VADER sentiment analysis
│   │   │   ├── phrases.py       # Phrase extraction (spaCy + TF-IDF)
│   │   │   └── themes.py        # Theme identification (NMF/LDA)
│   │   └── models/
│   │       └── schemas.py       # Pydantic request/response models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── BookSearch.tsx    # Search input and results list
│   │   │   ├── RatingFilter.tsx  # Star rating filter selector
│   │   │   └── ResultsView.tsx   # Analysis results display
│   │   └── types/
│   │       └── index.ts         # TypeScript type definitions
│   ├── package.json
│   └── tsconfig.json
├── CLAUDE.md
├── CONCEPT.md
├── DEV_PROCESS.md
├── CHAT_LOG.md
├── BRANCHING_STRATEGY.md
└── BACKLOG.md
```

---

## Core Systems

### 1. Scraper (`backend/app/scraper/goodreads.py`)

Handles all interaction with Goodreads using Playwright for browser automation.

**Responsibilities:**
- Search for books by title via `goodreads.com/search?q={query}`
- Navigate to a book's review page
- Apply star rating filter via UI interaction
- Paginate through reviews by clicking "Show More" button
- Extract review text, rating, and reviewer info from rendered HTML
- Handle anti-bot measures (random delays, stealth settings)

**Constraints:**
- Max ~300 reviews per book (Goodreads limit: 10 pages x 30 reviews)
- Random delays of 3-8 seconds between actions to avoid detection
- React class names are obfuscated and may change — selectors need to be maintainable

### 2. Analysis Pipeline (`backend/app/analysis/`)

Three-stage analysis pipeline that processes scraped reviews.

**Stage 1 — Sentiment Analysis (`sentiment.py`)**
- Uses VADER to score each review (compound, positive, negative, neutral)
- Classifies each review as positive/negative/neutral based on compound score thresholds
- Produces overall sentiment distribution across all reviews

**Stage 2 — Phrase Extraction (`phrases.py`)**
- Uses spaCy noun chunk extraction for linguistically meaningful phrases
- Uses scikit-learn TF-IDF with n-gram range (2,3) for corpus-level distinctive phrases
- Ranks phrases by frequency and returns top N

**Stage 3 — Theme Identification with Sentiment Correlation (`themes.py`)**
- Uses scikit-learn TF-IDF vectorizer to build document-term matrix
- Applies NMF (Non-negative Matrix Factorization) to identify topic clusters
- Assigns each review a dominant topic
- Correlates VADER sentiment scores with topic assignments
- Selects representative snippets per theme per sentiment polarity

### 3. API Layer (`backend/app/routers/`)

FastAPI routers exposing two main endpoints.

**`GET /api/books/search?q={query}`**
- Triggers Goodreads search
- Returns list of matching books

**`POST /api/analysis`**
- Accepts book ID and optional star rating filter
- Triggers scraping → analysis pipeline
- Returns full analysis results

### 4. Frontend (`frontend/src/`)

React + TypeScript SPA with three main views/components.

**BookSearch** — Search input with autocomplete/results list. User selects a book.
**RatingFilter** — Optional star rating filter (1-5 stars or "All").
**ResultsView** — Displays analysis results: overall sentiment, common phrases, and themes with correlated sentiment and snippets.

---

## Data Model

### API Types

```typescript
// Book search result
interface BookSearchResult {
  id: string;
  title: string;
  author: string;
  imageUrl: string;
  url: string;
}

// Analysis request
interface AnalysisRequest {
  bookId: string;
  starRating?: 1 | 2 | 3 | 4 | 5;
}

// Analysis response
interface AnalysisResponse {
  book: {
    title: string;
    author: string;
  };
  reviewCount: number;
  overallSentiment: {
    positive: number;
    negative: number;
    neutral: number;
  };
  commonPhrases: Array<{
    phrase: string;
    count: number;
  }>;
  themes: Array<{
    name: string;
    sentiment: {
      positive: number;
      negative: number;
      neutral: number;
    };
    snippets: Array<{
      text: string;
      sentiment: "positive" | "negative" | "neutral";
    }>;
  }>;
}
```

### Backend Pydantic Models

The same shapes defined as Pydantic models in `backend/app/models/schemas.py` for request validation and response serialization.

---

## Riskiest Technical Unknowns

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Goodreads anti-bot measures block scraping** | Cannot fetch reviews at all — project is dead | Phase 3 spike: build minimal scraper and test against live Goodreads. Fallback: use Apify managed scraping service, or pivot to alternative data source (Hardcover API, Open Library) |
| **Obfuscated/changing CSS selectors** | Scraper breaks silently | Use data-testid attributes where available; fall back to structural selectors; add scraper health checks |
| **NMF topic quality on small review sets** | Themes are incoherent or unhelpful | Tune number of topics; set minimum review threshold; fall back to keyword extraction if corpus too small |
| **Scraping speed** | Analysis takes too long for good UX | Add loading indicators; consider background processing; cap review count |

---

## Spike Plan

**Objective:** Validate that we can reliably scrape Goodreads reviews using Playwright.

**Scope:**
1. Install Playwright and launch a headless browser
2. Navigate to a known book page on Goodreads
3. Extract at least 30 reviews (one page worth) with text and rating
4. Test star rating filtering via UI interaction
5. Test pagination (click "Show More" at least once)

**Success criteria:**
- Can fetch review text and star rating for 30+ reviews from a single book
- Star rating filter produces filtered results
- No CAPTCHA or blocking encountered with reasonable delays

**Failure plan:**
- If blocked: investigate Playwright stealth plugins, proxy options, or Apify as managed alternative
- If Goodreads structure is too fragile: evaluate Hardcover API as alternative data source

---

## Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| T1 | Playwright + BeautifulSoup for scraping | Goodreads is a React SPA with anti-bot protection; browser automation required | 2026-02-21 |
| T2 | VADER for sentiment analysis | Purpose-built for review text; no training data; lightweight | 2026-02-21 |
| T3 | spaCy + scikit-learn TF-IDF for phrase extraction | Linguistic noun chunks + corpus-level TF-IDF for distinctive phrases | 2026-02-21 |
| T4 | scikit-learn NMF for theme identification | Fast, deterministic, interpretable; better than LDA on short docs | 2026-02-21 |
| T5 | No database for PoC | In-memory processing sufficient; add persistence later | 2026-02-21 |
| T6 | Spike on Goodreads scraping first | Highest-risk unknown; if scraping fails, project needs to pivot | 2026-02-21 |
