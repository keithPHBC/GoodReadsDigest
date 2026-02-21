"""Common phrase extraction using spaCy noun chunks and scikit-learn TF-IDF."""

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

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
class PhraseResult:
    """A common phrase with its frequency."""
    phrase: str
    count: int


def extract_phrases(review_texts: list[str], top_n: int = 20) -> list[PhraseResult]:
    """Extract the most common and distinctive phrases from reviews.

    Combines spaCy noun chunk extraction with TF-IDF scoring to find
    phrases that are both frequent and meaningful.
    """
    if not review_texts:
        return []

    # Stage 1: Extract noun chunks via spaCy
    noun_chunks = _extract_noun_chunks(review_texts)

    # Stage 2: Get TF-IDF scored n-grams
    tfidf_phrases = _extract_tfidf_phrases(review_texts)

    # Combine and rank
    combined = _combine_and_rank(noun_chunks, tfidf_phrases, top_n)

    return combined


def _extract_noun_chunks(review_texts: list[str]) -> Counter:
    """Extract and count noun chunks across all reviews."""
    chunk_counts: Counter = Counter()

    for text in review_texts:
        doc = _nlp(text)
        for chunk in doc.noun_chunks:
            # Normalize: lowercase, strip determiners
            phrase = _clean_phrase(chunk.text)
            if not phrase:
                continue
            words = phrase.split()
            # Filter single stopwords and require multi-word phrases
            if len(words) < MIN_PHRASE_WORDS:
                continue
            if all(w in _STOPWORDS for w in words):
                continue
            chunk_counts[phrase] += 1

    # Filter by minimum occurrences
    return Counter({p: c for p, c in chunk_counts.items() if c >= MIN_OCCURRENCES})


def _clean_phrase(phrase: str) -> str:
    """Normalize a phrase: lowercase, strip leading determiners and whitespace."""
    phrase = phrase.lower().strip()
    # Remove leading articles/determiners
    phrase = re.sub(r"^(the|a|an|this|that|these|those|my|his|her|its|our|their|some|any)\s+", "", phrase)
    # Remove extra whitespace
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
        max_df=0.8,  # Ignore phrases in >80% of reviews (too common)
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(review_texts)
    except ValueError:
        # Not enough data for TF-IDF
        return []

    feature_names = vectorizer.get_feature_names_out()

    # Sum TF-IDF scores across all documents for each phrase
    scores = tfidf_matrix.sum(axis=0).A1
    phrase_scores = list(zip(feature_names, scores))
    phrase_scores.sort(key=lambda x: x[1], reverse=True)

    return phrase_scores


def _combine_and_rank(
    noun_chunks: Counter,
    tfidf_phrases: list[tuple[str, float]],
    top_n: int,
) -> list[PhraseResult]:
    """Combine noun chunk counts and TF-IDF scores into a ranked list."""
    # Start with noun chunks (frequency-based)
    results: dict[str, int] = {}

    for phrase, count in noun_chunks.most_common(top_n * 2):
        results[phrase] = count

    # Add TF-IDF phrases that aren't already captured
    for phrase, score in tfidf_phrases[:top_n * 2]:
        if phrase not in results and len(phrase.split()) >= MIN_PHRASE_WORDS:
            # Estimate count from TF-IDF score (rough approximation)
            results[phrase] = max(MIN_OCCURRENCES, int(score * 2))

    # Sort by count descending, take top N
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

    return [PhraseResult(phrase=p, count=c) for p, c in sorted_results[:top_n]]
