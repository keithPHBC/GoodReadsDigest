from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import BookSearchResult

router = APIRouter()


@router.get("/books/search", response_model=list[BookSearchResult])
async def search_books(q: str = Query(..., min_length=1, description="Book search query")):
    """Search for books on Goodreads by title."""
    # TODO: Wire up to scraper (SCRAPER-1)
    raise HTTPException(status_code=501, detail="Book search not yet implemented")
