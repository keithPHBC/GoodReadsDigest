"""Common phrase extraction with sentiment correlation.

Uses spaCy noun chunks and scikit-learn TF-IDF for phrase extraction,
then correlates each phrase with sentiment from VADER analysis.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

from app.analysis.sentiment import ReviewSentiment

_nlp = spacy.load("en_core_web_sm")

# Phrases with fewer words than this are filtered out
MIN_PHRASE_WORDS = 2
# Minimum number of occurrences to be considered "common"
MIN_OCCURRENCES = 2


def _load_stopwords() -> set[str]:
    """Load Voyant Tools (Taporware) English stopwords list."""
    stopwords_path = Path(__file__).parent / "stopwords_en.txt"
    words = set()
    with open(stopwords_path) as f:
        for line in f:
            word = line.strip().lower()
            # Skip empty lines, punctuation-only entries, and numbers
            if word and word.isalpha():
                words.add(word)
    return words


_STOPWORDS = _load_stopwords()


@dataclass
class PhraseSnippet:
    """A representative review snippet for a phrase."""
    text: str
    sentiment: str  # "positive", "negative", or "neutral"


@dataclass
class PhraseWithSentiment:
    """A common phrase with frequency, sentiment breakdown, and snippets."""
    phrase: str
    count: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    snippets: list[PhraseSnippet] = field(default_factory=list)


def extract_phrases_with_sentiment(
    review_sentiments: list[ReviewSentiment],
    top_n: int = 15,
    snippets_per_sentiment: int = 1,
    max_snippet_length: int = 300,
) -> list[PhraseWithSentiment]:
    """Extract common phrases and correlate each with sentiment.

    For each identified phrase, finds all reviews containing it,
    computes sentiment distribution, and selects representative snippets.
    """
    if not review_sentiments:
        return []

    texts = [r.text for r in review_sentiments]

    # Extract ranked phrases
    ranked_phrases = _extract_ranked_phrases(texts, top_n)

    if not ranked_phrases:
        return []

    # Correlate each phrase with sentiment
    results: list[PhraseWithSentiment] = []

    for phrase, count in ranked_phrases:
        # Find reviews containing this phrase
        matching = [
            r for r in review_sentiments
            if phrase in r.text.lower()
        ]

        if not matching:
            continue

        # Compute sentiment distribution
        total = len(matching)
        pos = sum(1 for r in matching if r.label == "positive")
        neg = sum(1 for r in matching if r.label == "negative")
        neu = sum(1 for r in matching if r.label == "neutral")

        # Select representative snippets
        snippets = _select_snippets(matching, phrase, snippets_per_sentiment, max_snippet_length)

        results.append(PhraseWithSentiment(
            phrase=phrase,
            count=count,
            positive_pct=round(pos / total * 100, 1),
            negative_pct=round(neg / total * 100, 1),
            neutral_pct=round(neu / total * 100, 1),
            snippets=snippets,
        ))

    return results


def _select_snippets(
    reviews: list[ReviewSentiment],
    phrase: str,
    per_sentiment: int,
    max_length: int,
) -> list[PhraseSnippet]:
    """Select representative snippets containing the phrase, one per sentiment."""
    snippets: list[PhraseSnippet] = []

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

        # Sort by strength of sentiment
        group.sort(key=lambda r: abs(r.compound), reverse=True)

        for r in group[:per_sentiment]:
            # Try to extract a snippet centered around the phrase
            text = _extract_snippet_around_phrase(r.text, phrase, max_length)
            snippets.append(PhraseSnippet(text=text, sentiment=label))

    return snippets


def _extract_snippet_around_phrase(text: str, phrase: str, max_length: int) -> str:
    """Extract a snippet from the review centered around the phrase."""
    lower = text.lower()
    idx = lower.find(phrase)

    if idx == -1 or len(text) <= max_length:
        # Phrase not found or text is short enough — return truncated text
        snippet = text[:max_length]
    else:
        # Center the snippet around the phrase
        half = max_length // 2
        start = max(0, idx - half)
        end = min(len(text), idx + len(phrase) + half)

        # Adjust if near boundaries
        if start == 0:
            end = min(len(text), max_length)
        elif end == len(text):
            start = max(0, len(text) - max_length)

        snippet = text[start:end]

        # Add ellipsis indicators
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

    return snippet


# --- Core phrase extraction (unchanged logic) ---

def _extract_ranked_phrases(review_texts: list[str], top_n: int) -> list[tuple[str, int]]:
    """Extract and rank phrases by frequency."""
    noun_chunks = _extract_noun_chunks(review_texts)
    tfidf_phrases = _extract_tfidf_phrases(review_texts)
    return _combine_and_rank(noun_chunks, tfidf_phrases, top_n)


def _extract_noun_chunks(review_texts: list[str]) -> Counter:
    """Extract and count noun chunks across all reviews."""
    chunk_counts: Counter = Counter()

    for text in review_texts:
        doc = _nlp(text)
        for chunk in doc.noun_chunks:
            phrase = _clean_phrase(chunk.text)
            if not phrase:
                continue
            words = phrase.split()
            if len(words) < MIN_PHRASE_WORDS:
                continue
            if all(w in _STOPWORDS for w in words):
                continue
            chunk_counts[phrase] += 1

    return Counter({p: c for p, c in chunk_counts.items() if c >= MIN_OCCURRENCES})


def _clean_phrase(phrase: str) -> str:
    """Normalize a phrase: lowercase, strip leading determiners and whitespace."""
    phrase = phrase.lower().strip()
    phrase = re.sub(r"^(the|a|an|this|that|these|those|my|his|her|its|our|their|some|any)\s+", "", phrase)
    phrase = re.sub(r"\s+", " ", phrase).strip()
    return phrase


def _extract_tfidf_phrases(review_texts: list[str]) -> list[tuple[str, float]]:
    """Extract distinctive 2-3 word phrases using TF-IDF."""
    if len(review_texts) < 2:
        return []

    vectorizer = TfidfVectorizer(
        ngram_range=(2, 3),
        max_features=200,
        stop_words="english",
        min_df=MIN_OCCURRENCES,
        max_df=0.8,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(review_texts)
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    phrase_scores = list(zip(feature_names, scores))
    phrase_scores.sort(key=lambda x: x[1], reverse=True)

    return phrase_scores


def _combine_and_rank(
    noun_chunks: Counter,
    tfidf_phrases: list[tuple[str, float]],
    top_n: int,
) -> list[tuple[str, int]]:
    """Combine noun chunk counts and TF-IDF scores into a ranked list."""
    results: dict[str, int] = {}

    for phrase, count in noun_chunks.most_common(top_n * 2):
        results[phrase] = count

    for phrase, score in tfidf_phrases[:top_n * 2]:
        if phrase not in results and len(phrase.split()) >= MIN_PHRASE_WORDS:
            results[phrase] = max(MIN_OCCURRENCES, int(score * 2))

    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return sorted_results[:top_n]
