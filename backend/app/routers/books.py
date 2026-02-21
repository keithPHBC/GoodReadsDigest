from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import BookSearchResult
from app.scraper.goodreads import search_books

router = APIRouter()


@router.get("/books/search", response_model=list[BookSearchResult])
async def search_books_endpoint(q: str = Query(..., min_length=1, description="Book search query")):
    """Search for books on Goodreads by title."""
    try:
        results = await search_books(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
