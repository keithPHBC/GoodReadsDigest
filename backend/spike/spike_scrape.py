"""
SPIKE-1 & SPIKE-2: Goodreads Scraping Spike

Validates that we can:
1. Navigate to a Goodreads book page and extract reviews (SPIKE-1)
2. Filter by star rating and paginate (SPIKE-2)
"""

import asyncio
import json
import random
import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def random_delay(min_sec=3, max_sec=8):
    """Random delay to avoid detection."""
    delay = random.uniform(min_sec, max_sec)
    print(f"  [delay] Waiting {delay:.1f}s...")
    await asyncio.sleep(delay)


async def dismiss_modals(page):
    """Dismiss any sign-up or cookie modals that block interaction."""
    print("Checking for modals to dismiss...")
    # Close sign-up modal
    close_selectors = [
        'button[aria-label="Close"]',
        'button[aria-label="close"]',
        'button[aria-label="Dismiss"]',
        '.modal__close',
        '[data-testid="modal-close"]',
        'button.gr-iconButton[aria-label="Close"]',
    ]
    for selector in close_selectors:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                print(f"  Dismissed modal via: {selector}")
                await asyncio.sleep(1)
                return True
        except Exception:
            continue

    # Try pressing Escape
    try:
        await page.keyboard.press("Escape")
        print("  Pressed Escape to dismiss modal")
        await asyncio.sleep(1)
    except Exception:
        pass

    return False


async def spike_1_scrape_reviews(page, book_url):
    """SPIKE-1: Navigate to a book page and extract first page of reviews."""
    print(f"\n{'='*60}")
    print("SPIKE-1: Scrape first page of reviews")
    print(f"{'='*60}")
    print(f"Navigating to: {book_url}")

    await page.goto(book_url, wait_until="domcontentloaded")
    await random_delay(3, 5)

    # Dismiss any modals
    await dismiss_modals(page)
    await random_delay(1, 2)

    # Wait for reviews to load
    print("Waiting for reviews section to load...")
    try:
        await page.wait_for_selector('.ReviewCard', timeout=15000)
        print("Review cards found!")
    except Exception:
        print("Could not find .ReviewCard, waiting a bit longer...")
        await asyncio.sleep(5)

    # Scroll down to load reviews section fully
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await asyncio.sleep(2)

    # Get page HTML and parse
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Extract reviews
    review_cards = soup.select('.ReviewCard')
    print(f"Found {len(review_cards)} review cards")

    reviews = []
    for i, card in enumerate(review_cards):
        review = extract_review(card, i + 1)
        if review:
            reviews.append(review)

    if not reviews:
        print("\nNo reviews extracted. Dumping page structure for debugging...")
        dump_page_structure(soup)

    return reviews


def extract_review(card, index):
    """Extract review text and rating from a review card element."""
    review = {"index": index, "text": None, "rating": None}

    # Extract star rating from ShelfStatus section or star display
    # Look for the star rating - usually displayed as filled/unfilled stars with aria-labels
    star_spans = card.select('.RatingStars .RatingStar')
    if star_spans:
        filled = 0
        for star in star_spans:
            aria = star.get("aria-label", "")
            classes = " ".join(star.get("class", []))
            if "RatingStar--small" in classes and ("full" in aria.lower() or "fill" in classes.lower()):
                filled += 1
        if filled > 0:
            review["rating"] = filled

    # Alternative: look for aria-label like "Rating 4 out of 5"
    if not review["rating"]:
        rating_el = card.select_one('[aria-label*="Rating"][aria-label*="out of"]')
        if rating_el:
            label = rating_el.get("aria-label", "")
            parts = label.split()
            for j, word in enumerate(parts):
                if word == "Rating" and j + 1 < len(parts):
                    try:
                        review["rating"] = int(parts[j + 1])
                    except ValueError:
                        pass
                    break

    # Alternative: look for star rating in the ShelfStatus area
    if not review["rating"]:
        shelf = card.select_one('.ShelfStatus')
        if shelf:
            # Count star SVGs or star elements
            stars = shelf.select('span[data-testid*="star"], .Icon--star')
            if stars:
                review["rating"] = len(stars)

    # Extract review text
    # Look for the Formatted/TruncatedContent section
    text_el = card.select_one('.ReviewText__content .Formatted')
    if text_el:
        review["text"] = text_el.get_text(strip=True)[:500]

    if not review["text"]:
        text_el = card.select_one('.TruncatedContent .Formatted')
        if text_el:
            review["text"] = text_el.get_text(strip=True)[:500]

    # Fallback: find the largest text block
    if not review["text"]:
        all_text = card.find_all(['span', 'div', 'p'])
        candidates = [(el, len(el.get_text(strip=True))) for el in all_text]
        candidates.sort(key=lambda x: x[1], reverse=True)
        for el, length in candidates:
            if length > 50:
                review["text"] = el.get_text(strip=True)[:500]
                break

    if review["text"]:
        return review
    return None


def dump_page_structure(soup):
    """Dump relevant page structure for debugging."""
    review_elements = soup.find_all(attrs={"class": lambda c: c and "review" in str(c).lower()})
    print(f"\nElements with 'review' in class: {len(review_elements)}")
    for el in review_elements[:5]:
        tag = el.name
        classes = el.get("class", [])
        text = el.get_text(strip=True)[:100]
        print(f"  <{tag} class='{' '.join(classes)}'> {text}...")

    testid_elements = soup.find_all(attrs={"data-testid": True})
    testids = set()
    for el in testid_elements:
        testids.add(el.get("data-testid"))
    print(f"\ndata-testid values ({len(testids)}):")
    for tid in sorted(testids):
        print(f"  {tid}")


async def spike_2_filter_and_paginate(page):
    """SPIKE-2: Test star rating filtering and pagination."""
    print(f"\n{'='*60}")
    print("SPIKE-2: Star rating filter and pagination")
    print(f"{'='*60}")

    # Dismiss any modals that may have reappeared
    await dismiss_modals(page)

    # --- Test pagination ---
    print("\n--- Testing Pagination ---")

    # Scroll to reviews section first
    await page.evaluate("""
        const reviews = document.querySelector('.ReviewCard');
        if (reviews) reviews.scrollIntoView({ behavior: 'smooth', block: 'center' });
    """)
    await random_delay(2, 3)

    load_more_found = False
    try:
        # Look for "Show more reviews" button specifically
        show_more = page.locator('button:has-text("Show more reviews"), button:has-text("Show more")').first
        if await show_more.is_visible(timeout=5000):
            print("Found 'Show more' button")
            await show_more.scroll_into_view_if_needed()
            await random_delay(1, 2)
            await show_more.click()
            print("Clicked 'Show more'! Waiting for new reviews...")
            await random_delay(5, 8)

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select('.ReviewCard')
            print(f"Reviews after clicking Show More: {len(cards)}")
            load_more_found = True
    except Exception as e:
        print(f"Show more button interaction failed: {e}")

    if not load_more_found:
        print("Trying scroll-based loading...")
        # Get current count
        html_before = await page.content()
        count_before = len(BeautifulSoup(html_before, "html.parser").select('.ReviewCard'))

        # Scroll to bottom of page a few times
        for i in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        html_after = await page.content()
        count_after = len(BeautifulSoup(html_after, "html.parser").select('.ReviewCard'))
        print(f"Reviews before scroll: {count_before}, after scroll: {count_after}")
        if count_after > count_before:
            load_more_found = True
            print("Scroll-based pagination worked!")

    # --- Test star rating filter ---
    print("\n--- Testing Star Rating Filter ---")

    # Take a screenshot to see current state
    await page.screenshot(path="/home/deck/src/claude/GoodReadsDigest/backend/spike/spike_before_filter.png")

    # Look for the filter area near reviews
    filter_found = False

    # On the new Goodreads, filters might be dropdown or buttons near the review section
    # Try clicking "Filters" text/button
    try:
        filters_btn = page.locator('button:has-text("Filters"), button:has-text("filters")').first
        if await filters_btn.is_visible(timeout=3000):
            await filters_btn.scroll_into_view_if_needed()
            await random_delay(1, 2)
            await filters_btn.click()
            print("Clicked Filters button")
            await random_delay(2, 3)
            filter_found = True
    except Exception:
        pass

    # Try star rating links/buttons (sometimes displayed as "5 stars (1,234)")
    if not filter_found:
        try:
            star_buttons = page.locator('button:has-text("star"), a:has-text("star")')
            count = await star_buttons.count()
            if count > 0:
                print(f"Found {count} star-related buttons/links")
                for i in range(min(count, 5)):
                    text = await star_buttons.nth(i).text_content()
                    print(f"  [{i}] {text.strip()[:60]}")
                filter_found = True
        except Exception:
            pass

    # Try looking for the rating histogram bars (clickable on some versions)
    if not filter_found:
        try:
            hist_bars = page.locator('.RatingsHistogram__bar, [data-testid*="ratingBar"], a[href*="rating"]')
            count = await hist_bars.count()
            if count > 0:
                print(f"Found {count} histogram bar elements")
                filter_found = True
                # Try clicking the 5-star bar
                await hist_bars.first.click()
                print("Clicked first histogram bar")
                await random_delay(3, 5)
        except Exception:
            pass

    if not filter_found:
        print("Could not find star rating filter UI. Taking debug screenshot...")

    # Final screenshot
    await page.screenshot(path="/home/deck/src/claude/GoodReadsDigest/backend/spike/spike_screenshot.png")
    print("Screenshots saved")

    return load_more_found, filter_found


async def main():
    print("GoodReadsDigest — Scraping Spike")
    print("=" * 60)

    book_url = "https://www.goodreads.com/book/show/4671.The_Great_Gatsby"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )

        page = await context.new_page()

        # SPIKE-1: Scrape first page
        reviews = await spike_1_scrape_reviews(page, book_url)

        print(f"\n--- SPIKE-1 Results ---")
        print(f"Total reviews extracted: {len(reviews)}")
        ratings_found = sum(1 for r in reviews if r["rating"] is not None)
        print(f"Reviews with ratings: {ratings_found}/{len(reviews)}")

        for r in reviews[:5]:
            print(f"\n  Review #{r['index']}:")
            print(f"    Rating: {r['rating']} stars")
            text_preview = r['text'][:150] + "..." if r['text'] and len(r['text']) > 150 else r['text']
            print(f"    Text: {text_preview}")

        if len(reviews) >= 10:
            print(f"\n✓ SPIKE-1 PASSED: Extracted {len(reviews)} reviews")
        else:
            print(f"\n✗ SPIKE-1 NEEDS INVESTIGATION: Only {len(reviews)} reviews")

        # SPIKE-2: Filter and paginate
        if reviews:
            load_more_ok, filter_ok = await spike_2_filter_and_paginate(page)
            print(f"\n--- SPIKE-2 Results ---")
            print(f"  Pagination: {'✓ Working' if load_more_ok else '✗ Not working'}")
            print(f"  Star filter: {'✓ Found' if filter_ok else '✗ Not found'}")

            if load_more_ok and filter_ok:
                print("\n✓ SPIKE-2 PASSED")
            elif load_more_ok or filter_ok:
                print("\n~ SPIKE-2 PARTIAL: Some features working")
            else:
                print("\n✗ SPIKE-2 NEEDS INVESTIGATION")
        else:
            print("\nSkipping SPIKE-2 (SPIKE-1 failed)")

        await browser.close()

    # Summary
    print(f"\n{'='*60}")
    print("SPIKE SUMMARY")
    print(f"{'='*60}")
    print(f"Reviews extracted: {len(reviews)}")
    print(f"Ratings captured: {ratings_found}/{len(reviews)}")
    print(f"Core scraping feasibility: {'CONFIRMED' if len(reviews) >= 10 else 'AT RISK'}")


if __name__ == "__main__":
    asyncio.run(main())
