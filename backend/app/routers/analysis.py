from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalysisRequest, AnalysisResponse

router = APIRouter()


@router.post("/analysis", response_model=AnalysisResponse)
async def analyze_book(request: AnalysisRequest):
    """Fetch and analyze reviews for a book."""
    # TODO: Wire up to scraper + analysis pipeline (API-3)
    raise HTTPException(status_code=501, detail="Analysis not yet implemented")
