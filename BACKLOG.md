# GoodReadsDigest — Product Backlog

## Epic: SPIKE — Goodreads Scraping Spike

**Goal:** Validate that we can reliably scrape Goodreads reviews using Playwright before committing to the full implementation.
**Phase:** 3
**Status:** Not Started

---

#### SPIKE-1: Set up Playwright and scrape a single book page

**Type:** Spike
**Status:** To Do
**Priority:** Must Have

**Description:**
Install Playwright, launch a headless browser, navigate to a known Goodreads book page, and extract review text and star ratings from the first page of reviews (~30 reviews). This validates that we can get past Goodreads' anti-bot measures and parse their React-rendered DOM.

**Acceptance Criteria:**
- [ ] Playwright is installed and can launch a headless Chromium browser
- [ ] Script navigates to a known book's review page on Goodreads
- [ ] At least 30 reviews are extracted with both text content and star rating
- [ ] No CAPTCHA or blocking encountered with 3-8 second random delays
- [ ] Extracted data is printed/logged in a structured format

**Notes:**
Use `playwright-stealth` or equivalent if initial attempts are blocked. If Goodreads blocks all attempts, document findings and evaluate fallback options (Apify, Hardcover API).

---

#### SPIKE-2: Test star rating filtering and pagination

**Type:** Spike
**Status:** To Do
**Priority:** Must Have

**Description:**
Extend the spike to test two additional capabilities: filtering reviews by star rating using Goodreads' UI filter, and paginating through reviews by clicking the "Show More" button. Both are critical for the core workflow.

**Acceptance Criteria:**
- [ ] Script can apply a star rating filter (e.g., show only 5-star reviews) via UI interaction
- [ ] Filtered results contain only reviews matching the selected rating
- [ ] Script can click "Show More" to load additional reviews beyond the first page
- [ ] At least 60 reviews (2 pages) can be extracted from a single book

**Notes:**
Depends on SPIKE-1 succeeding. Star rating filter is in a "Filters" dropdown in the Community Reviews section. Pagination uses a button with `span[data-testid="loadMore"]`.

---

## Epic: SCRAPER — Goodreads Scraper

**Goal:** Build a reliable, reusable scraper module that can search for books and fetch reviews from Goodreads.
**Phase:** 4
**Status:** Not Started

---

#### SCRAPER-1: Implement book search

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the book search functionality in `backend/app/scraper/goodreads.py`. The scraper should accept a search query string, navigate to Goodreads search results, and return a list of matching books with their ID, title, author, cover image URL, and Goodreads URL.

**Acceptance Criteria:**
- [ ] Function accepts a search query string
- [ ] Navigates to `goodreads.com/search?q={query}` using Playwright
- [ ] Extracts book ID, title, author, image URL, and book URL from search results
- [ ] Returns a list of BookSearchResult objects
- [ ] Handles case where no results are found (returns empty list)

**Notes:**
Book ID is the numeric ID in the URL path (e.g., `4671` from `/book/show/4671.The_Great_Gatsby`).

---

#### SCRAPER-2: Implement review fetching with pagination

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the review fetching functionality. Given a book ID and optional star rating filter, navigate to the book's page, apply the filter if specified, and scrape reviews with pagination. Extract review text and star rating for each review.

**Acceptance Criteria:**
- [ ] Function accepts a book ID and optional star rating (1-5)
- [ ] Navigates to the book's review page
- [ ] Applies star rating filter if specified
- [ ] Paginates through reviews by clicking "Show More" (up to a configurable max)
- [ ] Extracts review text and star rating for each review
- [ ] Returns a list of review objects
- [ ] Implements random delays (3-8 seconds) between actions

**Notes:**
Cap at a configurable number of reviews (default 100 for PoC). Handle "...more" truncation on long reviews by clicking to expand.

---

## Epic: ANALYSIS — NLP Analysis Pipeline

**Goal:** Build the analysis pipeline that processes scraped reviews to produce sentiment, phrase, and theme analysis.
**Phase:** 4
**Status:** Not Started

---

#### ANALYSIS-1: Implement sentiment analysis

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the sentiment analysis module in `backend/app/analysis/sentiment.py`. Use VADER to score each review and classify as positive, negative, or neutral. Produce an overall sentiment distribution across all reviews.

**Acceptance Criteria:**
- [ ] Function accepts a list of review texts
- [ ] Uses VADER to compute compound, positive, negative, and neutral scores per review
- [ ] Classifies each review as positive (compound >= 0.05), negative (compound <= -0.05), or neutral
- [ ] Returns per-review sentiment and overall sentiment distribution (counts and percentages)

**Notes:**
VADER thresholds (0.05 / -0.05) are the library's recommended defaults. We can tune later.

---

#### ANALYSIS-2: Implement phrase extraction

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the phrase extraction module in `backend/app/analysis/phrases.py`. Use spaCy noun chunks and scikit-learn TF-IDF to identify the most common and distinctive phrases across the review corpus.

**Acceptance Criteria:**
- [ ] Function accepts a list of review texts
- [ ] Uses spaCy to extract noun chunks from each review
- [ ] Uses scikit-learn TfidfVectorizer with n-gram range (2,3) for corpus-level phrase analysis
- [ ] Ranks phrases by frequency / TF-IDF score
- [ ] Returns top N phrases (configurable, default 20) with counts
- [ ] Filters out low-value phrases (stopword-heavy, very short)

**Notes:**
Requires `en_core_web_sm` spaCy model. Consider combining noun chunk frequency with TF-IDF scoring for best results.

---

#### ANALYSIS-3: Implement theme identification with sentiment correlation

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the theme identification module in `backend/app/analysis/themes.py`. Use scikit-learn NMF with TF-IDF to discover topics/themes across reviews. Correlate each theme with sentiment scores from ANALYSIS-1 and select representative snippets.

**Acceptance Criteria:**
- [ ] Function accepts a list of review texts and their sentiment scores
- [ ] Builds TF-IDF matrix and applies NMF to identify N topics (configurable, default 5-8)
- [ ] Assigns each review a dominant topic
- [ ] Names each topic using its top terms
- [ ] Computes sentiment distribution per topic (positive/negative/neutral percentages)
- [ ] Selects 2-3 representative review snippets per topic per sentiment polarity
- [ ] Returns themed analysis with sentiment correlation and snippets

**Notes:**
NMF is preferred over LDA for short documents. Number of topics may need tuning based on review count — consider fewer topics for smaller corpora.

---

## Epic: API — Backend API Layer

**Goal:** Expose the scraper and analysis pipeline via FastAPI endpoints.
**Phase:** 4
**Status:** Not Started

---

#### API-1: Set up FastAPI project structure and Pydantic models

**Type:** Chore
**Status:** To Do
**Priority:** Must Have

**Description:**
Set up the backend project structure, install dependencies, create the FastAPI app entry point, and define Pydantic models for all request/response schemas as specified in `TECH_DESIGN.md`.

**Acceptance Criteria:**
- [ ] Backend project structure matches `TECH_DESIGN.md`
- [ ] `requirements.txt` includes all dependencies (fastapi, uvicorn, playwright, beautifulsoup4, vaderSentiment, spacy, scikit-learn, pandas)
- [ ] FastAPI app starts and serves a health check endpoint
- [ ] Pydantic models defined for BookSearchResult, AnalysisRequest, AnalysisResponse, and nested types
- [ ] CORS configured to allow requests from the frontend dev server

**Notes:**
This is a setup chore that unblocks all other API and integration work.

---

#### API-2: Implement book search endpoint

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Create the `GET /api/books/search` endpoint in `backend/app/routers/books.py`. It should accept a query parameter, call the scraper's book search function, and return results as BookSearchResult objects.

**Acceptance Criteria:**
- [ ] `GET /api/books/search?q={query}` endpoint exists
- [ ] Calls the Goodreads scraper book search function
- [ ] Returns a JSON array of BookSearchResult objects
- [ ] Returns empty array for no results
- [ ] Returns appropriate error response if scraping fails

**Notes:**
Depends on SCRAPER-1.

---

#### API-3: Implement analysis endpoint

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Create the `POST /api/analysis` endpoint in `backend/app/routers/analysis.py`. It should accept a book ID and optional star rating, trigger the scraping and analysis pipeline, and return the full analysis results.

**Acceptance Criteria:**
- [ ] `POST /api/analysis` endpoint exists
- [ ] Accepts JSON body with bookId (required) and starRating (optional, 1-5)
- [ ] Triggers review scraping for the specified book
- [ ] Runs the full analysis pipeline (sentiment → phrases → themes)
- [ ] Returns a complete AnalysisResponse object
- [ ] Returns appropriate error response if scraping or analysis fails
- [ ] Includes review count in response

**Notes:**
Depends on SCRAPER-2, ANALYSIS-1, ANALYSIS-2, ANALYSIS-3. This is the integration point that ties everything together. Analysis will take time due to scraping delays — consider returning a loading status or using async processing.

---

## Epic: UI — Frontend User Interface

**Goal:** Build the React + TypeScript frontend that allows users to search for books and view analysis results.
**Phase:** 5
**Status:** Not Started

---

#### UI-1: Set up React + TypeScript project

**Type:** Chore
**Status:** To Do
**Priority:** Must Have

**Description:**
Initialize the frontend project with React + TypeScript. Set up the development server, configure proxy to backend, and create the basic app shell with routing/navigation between search and results views.

**Acceptance Criteria:**
- [ ] React + TypeScript project initialized (Vite or Create React App)
- [ ] Dev server starts and renders a basic page
- [ ] API proxy configured to forward `/api` requests to the backend
- [ ] TypeScript types defined in `types/index.ts` matching the API schemas
- [ ] Basic app shell with placeholder components

**Notes:**
Prefer Vite for faster dev server and builds.

---

#### UI-2: Implement book search component

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the BookSearch component. User enters a book title, the component calls the search API, and displays matching results. User clicks a result to select it.

**Acceptance Criteria:**
- [ ] Search input field with submit button or enter-to-search
- [ ] Calls `GET /api/books/search?q={query}` on submit
- [ ] Displays list of matching books (title, author, cover image)
- [ ] User can click a book to select it
- [ ] Loading state shown while searching
- [ ] "No results found" message when appropriate

**Notes:**
Depends on API-2.

---

#### UI-3: Implement rating filter component

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the RatingFilter component. After selecting a book, user can optionally choose a star rating (1-5) to filter reviews, or choose "All" for no filter. Selecting a filter (or "All") triggers the analysis.

**Acceptance Criteria:**
- [ ] Displays star rating options: All, 1, 2, 3, 4, 5
- [ ] Defaults to "All" (no filter)
- [ ] User can select a rating to filter by
- [ ] Selection triggers the analysis API call
- [ ] Visually indicates selected filter

**Notes:**
Keep this simple — buttons or a dropdown. No need for star icons in the PoC.

---

#### UI-4: Implement results view component

**Type:** Feature
**Status:** To Do
**Priority:** Must Have

**Description:**
Build the ResultsView component. Displays the full analysis results: overall sentiment distribution, common phrases, and themes with correlated sentiment and representative snippets.

**Acceptance Criteria:**
- [ ] Displays overall sentiment breakdown (positive/negative/neutral counts and percentages)
- [ ] Displays common phrases ranked by frequency
- [ ] Displays identified themes, each showing:
  - Theme name (derived from top terms)
  - Sentiment breakdown for that theme
  - Representative review snippets with sentiment labels
- [ ] Loading state shown while analysis is running (scraping + NLP takes time)
- [ ] Error state if analysis fails
- [ ] "Back to search" option to start over

**Notes:**
Depends on API-3. Analysis may take 30-60+ seconds due to scraping delays — the loading state is important. Consider showing a progress message.

---

#### UI-5: Basic error handling and user feedback

**Type:** Feature
**Status:** Should Have
**Priority:** Should Have

**Description:**
Add basic error handling and user feedback across the app. Handle API errors gracefully, show meaningful messages, and ensure the user is never stuck on a broken screen.

**Acceptance Criteria:**
- [ ] API errors show a user-friendly message (not raw error text)
- [ ] Network failures are caught and displayed
- [ ] User can retry or go back to search from any error state
- [ ] Long-running analysis shows progress indication or estimated wait message

**Notes:**
This is a polish pass on error states. Keep it minimal for PoC.
