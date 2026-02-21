# GoodReadsDigest

Analyze Goodreads reviews for a given book, surfacing sentiment patterns, common phrases, and key concepts so readers can quickly understand what people love, hate, and talk about — without reading hundreds of reviews.

## Status

**Proof-of-concept** — in active development. See `DEV_PROCESS.md` for current phase and progress.

## Tech Stack

- **Backend:** Python 3.13 + FastAPI
- **Frontend:** React + TypeScript (Phase 5)
- **Scraping:** Playwright + BeautifulSoup4
- **NLP:** VADER (sentiment), spaCy (phrase extraction), scikit-learn (theme identification)

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend, Phase 5)

## Setup

### Backend

```bash
# Create virtual environment
cd backend
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Frontend

_Coming in Phase 5._

## Running

### Backend API server

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Available endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/books/search?q={query}` | Search for books by title |
| `POST` | `/api/analysis` | Analyze reviews for a book |

### Running the scraping spike

```bash
cd backend
source .venv/bin/activate
python spike/spike_scrape.py
```

## Project Structure

```
GoodReadsDigest/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routers/             # API endpoints
│   │   ├── scraper/             # Goodreads scraper
│   │   ├── analysis/            # NLP pipeline
│   │   └── models/              # Pydantic schemas
│   ├── spike/                   # Scraping spike scripts
│   └── requirements.txt
├── frontend/                    # React + TypeScript (Phase 5)
├── CONCEPT.md                   # Product concept and scope
├── TECH_DESIGN.md               # Architecture and technical decisions
├── BACKLOG.md                   # Work items and progress
├── DEV_PROCESS.md               # Development process and status
└── CHAT_LOG.md                  # Development conversation history
```

## License

TBD
