"""Theme identification with sentiment correlation using scikit-learn NMF."""

from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

from app.analysis.sentiment import ReviewSentiment


@dataclass
class ThemeSnippet:
    """A representative review snippet for a theme."""
    text: str
    sentiment: str  # "positive", "negative", or "neutral"


@dataclass
class IdentifiedTheme:
    """A theme with sentiment breakdown and representative snippets."""
    name: str
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    review_count: int
    snippets: list[ThemeSnippet] = field(default_factory=list)


@dataclass
class ThemeResult:
    """Result of theme identification across all reviews."""
    themes: list[IdentifiedTheme]


def identify_themes(
    review_sentiments: list[ReviewSentiment],
    n_topics: int | None = None,
    snippets_per_sentiment: int = 2,
    max_snippet_length: int = 300,
) -> ThemeResult:
    """Identify themes across reviews and correlate with sentiment.

    Uses TF-IDF + NMF to discover topic clusters, then correlates each
    theme with sentiment scores and selects representative snippets.

    Args:
        review_sentiments: Reviews with pre-computed sentiment labels.
        n_topics: Number of topics to extract. Auto-determined if None.
        snippets_per_sentiment: Number of snippets per sentiment per theme.
        max_snippet_length: Max character length for snippets.
    """
    texts = [r.text for r in review_sentiments]

    if len(texts) < 5:
        return ThemeResult(themes=[])

    # Auto-determine topic count based on corpus size
    if n_topics is None:
        n_topics = _auto_topic_count(len(texts))

    # Build TF-IDF matrix
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words="english",
        min_df=2,
        max_df=0.85,
        ngram_range=(1, 2),
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return ThemeResult(themes=[])

    # If we have fewer features than topics, reduce topic count
    n_features = tfidf_matrix.shape[1]
    if n_features < n_topics:
        n_topics = max(2, n_features // 2)

    # Apply NMF
    nmf = NMF(n_components=n_topics, random_state=42, max_iter=300)
    try:
        doc_topics = nmf.fit_transform(tfidf_matrix)
    except ValueError:
        return ThemeResult(themes=[])

    feature_names = vectorizer.get_feature_names_out()

    # Assign each review to its dominant topic
    dominant_topics = np.argmax(doc_topics, axis=1)

    # Build themes
    themes: list[IdentifiedTheme] = []

    for topic_idx in range(n_topics):
        # Get top terms for this topic
        top_term_indices = nmf.components_[topic_idx].argsort()[-5:][::-1]
        top_terms = [feature_names[i] for i in top_term_indices]
        theme_name = " / ".join(top_terms[:3])

        # Find reviews assigned to this topic
        topic_review_indices = [i for i, t in enumerate(dominant_topics) if t == topic_idx]

        if not topic_review_indices:
            continue

        # Compute sentiment distribution for this topic
        topic_sentiments = [review_sentiments[i] for i in topic_review_indices]
        pos = sum(1 for r in topic_sentiments if r.label == "positive")
        neg = sum(1 for r in topic_sentiments if r.label == "negative")
        neu = sum(1 for r in topic_sentiments if r.label == "neutral")
        total = len(topic_sentiments)

        # Select representative snippets
        snippets = _select_snippets(
            topic_sentiments, snippets_per_sentiment, max_snippet_length
        )

        themes.append(IdentifiedTheme(
            name=theme_name,
            positive_pct=round(pos / total * 100, 1),
            negative_pct=round(neg / total * 100, 1),
            neutral_pct=round(neu / total * 100, 1),
            review_count=total,
            snippets=snippets,
        ))

    # Sort themes by review count (most discussed first)
    themes.sort(key=lambda t: t.review_count, reverse=True)

    return ThemeResult(themes=themes)


def _auto_topic_count(n_reviews: int) -> int:
    """Determine number of topics based on corpus size."""
    if n_reviews < 10:
        return 3
    elif n_reviews < 30:
        return 4
    elif n_reviews < 60:
        return 5
    elif n_reviews < 100:
        return 6
    return 8


def _select_snippets(
    reviews: list[ReviewSentiment],
    per_sentiment: int,
    max_length: int,
) -> list[ThemeSnippet]:
    """Select representative snippets for each sentiment polarity.

    Picks reviews with the strongest sentiment scores as representatives.
    """
    snippets: list[ThemeSnippet] = []

    # Group by sentiment label
    by_label: dict[str, list[ReviewSentiment]] = {
        "positive": [],
        "negative": [],
        "neutral": [],
    }
    for r in reviews:
        by_label[r.label].append(r)

    for label in ("positive", "negative", "neutral"):
        group = by_label[label]
        if not group:
            continue

        # Sort by strength of sentiment (abs compound score)
        group.sort(key=lambda r: abs(r.compound), reverse=True)

        for r in group[:per_sentiment]:
            text = r.text[:max_length]
            if len(r.text) > max_length:
                # Truncate at last sentence boundary or word
                last_period = text.rfind(".")
                last_space = text.rfind(" ")
                cut = last_period if last_period > max_length // 2 else last_space
                if cut > 0:
                    text = text[:cut + 1]
                text = text.rstrip() + "..."

            snippets.append(ThemeSnippet(text=text, sentiment=label))

    return snippets
