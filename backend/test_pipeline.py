"""End-to-end test of the GoodReadsDigest pipeline.

Usage:
    python test_pipeline.py [book_query] [max_reviews]

Examples:
    python test_pipeline.py                          # Defaults: "The Great Gatsby", 30 reviews
    python test_pipeline.py "Project Hail Mary"      # Custom book, 30 reviews
    python test_pipeline.py "Dune" 50                # Custom book, 50 reviews
"""

import asyncio
import sys
import time

from app.scraper.goodreads import search_books, fetch_reviews
from app.analysis.sentiment import analyze_sentiment
from app.analysis.phrases import extract_phrases
from app.analysis.themes import identify_themes


async def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "The Great Gatsby"
    max_reviews = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    print("=" * 60)
    print("GoodReadsDigest — Pipeline Test")
    print("=" * 60)

    # Step 1: Search
    print(f"\n[1/5] Searching for: {query}")
    t0 = time.time()
    results = await search_books(query)
    print(f"      Found {len(results)} results ({time.time() - t0:.1f}s)")

    if not results:
        print("      No results found. Exiting.")
        return

    for i, book in enumerate(results[:5]):
        marker = " <--" if i == 0 else ""
        print(f"      [{i+1}] {book.title} by {book.author}{marker}")

    selected = results[0]
    print(f"\n      Selected: {selected.title} (ID: {selected.id})")

    # Step 2: Fetch reviews
    print(f"\n[2/5] Fetching up to {max_reviews} reviews...")
    t0 = time.time()
    reviews, book_info = await fetch_reviews(selected.id, max_reviews=max_reviews)
    elapsed = time.time() - t0
    print(f"      Fetched {len(reviews)} reviews ({elapsed:.1f}s)")

    ratings_count = sum(1 for r in reviews if r.rating is not None)
    print(f"      Ratings captured: {ratings_count}/{len(reviews)}")

    if not reviews:
        print("      No reviews fetched. Exiting.")
        return

    texts = [r.text for r in reviews]

    # Step 3: Sentiment analysis
    print(f"\n[3/5] Analyzing sentiment...")
    t0 = time.time()
    sentiment = analyze_sentiment(texts)
    print(f"      Done ({time.time() - t0:.1f}s)")
    print(f"      Positive: {sentiment.positive_count} ({sentiment.positive_pct}%)")
    print(f"      Negative: {sentiment.negative_count} ({sentiment.negative_pct}%)")
    print(f"      Neutral:  {sentiment.neutral_count} ({sentiment.neutral_pct}%)")

    # Step 4: Phrase extraction
    print(f"\n[4/5] Extracting common phrases...")
    t0 = time.time()
    phrases = extract_phrases(texts, top_n=15)
    print(f"      Done ({time.time() - t0:.1f}s)")
    print(f"      Top phrases:")
    for p in phrases[:10]:
        print(f"        {p.count:3d}x  {p.phrase}")

    # Step 5: Theme identification
    print(f"\n[5/5] Identifying themes with sentiment correlation...")
    t0 = time.time()
    theme_result = identify_themes(sentiment.reviews)
    print(f"      Done ({time.time() - t0:.1f}s)")
    print(f"      Found {len(theme_result.themes)} themes:")

    for theme in theme_result.themes:
        print(f"\n      --- {theme.name} ({theme.review_count} reviews) ---")
        print(f"      Sentiment: +{theme.positive_pct}% / -{theme.negative_pct}% / ~{theme.neutral_pct}%")
        for snippet in theme.snippets:
            label = {"positive": "+", "negative": "-", "neutral": "~"}[snippet.sentiment]
            print(f"        [{label}] {snippet.text[:100]}{'...' if len(snippet.text) > 100 else ''}")

    # Summary
    print(f"\n{'=' * 60}")
    print("PIPELINE TEST COMPLETE")
    print(f"{'=' * 60}")
    print(f"Book:     {book_info.title} by {book_info.author}")
    print(f"Reviews:  {len(reviews)}")
    print(f"Sentiment: +{sentiment.positive_pct}% / -{sentiment.negative_pct}% / ~{sentiment.neutral_pct}%")
    print(f"Phrases:  {len(phrases)}")
    print(f"Themes:   {len(theme_result.themes)}")


if __name__ == "__main__":
    asyncio.run(main())
