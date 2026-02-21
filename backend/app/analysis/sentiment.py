"""Sentiment analysis using VADER."""

from dataclasses import dataclass
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

# VADER recommended thresholds
POS_THRESHOLD = 0.05
NEG_THRESHOLD = -0.05


@dataclass
class ReviewSentiment:
    """Sentiment scores for a single review."""
    text: str
    compound: float
    positive: float
    negative: float
    neutral: float
    label: str  # "positive", "negative", or "neutral"


@dataclass
class SentimentResult:
    """Aggregated sentiment analysis across all reviews."""
    reviews: list[ReviewSentiment]
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float


def classify(compound: float) -> str:
    """Classify a VADER compound score as positive, negative, or neutral."""
    if compound >= POS_THRESHOLD:
        return "positive"
    elif compound <= NEG_THRESHOLD:
        return "negative"
    return "neutral"


def analyze_sentiment(review_texts: list[str]) -> SentimentResult:
    """Analyze sentiment for a list of review texts.

    Returns per-review sentiment scores and overall distribution.
    """
    reviews: list[ReviewSentiment] = []

    for text in review_texts:
        scores = _analyzer.polarity_scores(text)
        label = classify(scores["compound"])
        reviews.append(ReviewSentiment(
            text=text,
            compound=scores["compound"],
            positive=scores["pos"],
            negative=scores["neg"],
            neutral=scores["neu"],
            label=label,
        ))

    total = len(reviews) or 1
    pos = sum(1 for r in reviews if r.label == "positive")
    neg = sum(1 for r in reviews if r.label == "negative")
    neu = sum(1 for r in reviews if r.label == "neutral")

    return SentimentResult(
        reviews=reviews,
        positive_count=pos,
        negative_count=neg,
        neutral_count=neu,
        positive_pct=round(pos / total * 100, 1),
        negative_pct=round(neg / total * 100, 1),
        neutral_pct=round(neu / total * 100, 1),
    )
