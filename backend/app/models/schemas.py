from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class StarRating(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


# --- Book Search ---

class BookSearchResult(BaseModel):
    id: str
    title: str
    author: str
    image_url: str = ""
    url: str


# --- Analysis Request ---

class AnalysisRequest(BaseModel):
    book_id: str
    star_rating: Optional[StarRating] = None


# --- Analysis Response ---

class SentimentBreakdown(BaseModel):
    positive: float
    negative: float
    neutral: float


class ReviewSnippet(BaseModel):
    text: str
    sentiment: str  # "positive", "negative", or "neutral"


class PhraseSentiment(BaseModel):
    phrase: str
    count: int
    sentiment: SentimentBreakdown
    snippets: list[ReviewSnippet]


class AnalysisResponse(BaseModel):
    book: BookSearchResult
    review_count: int
    overall_sentiment: SentimentBreakdown
    phrases: list[PhraseSentiment]
