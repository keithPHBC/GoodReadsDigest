"""Goodreads scraper using Playwright for browser automation."""

import asyncio
import random
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from dataclasses import dataclass

from app.models.schemas import BookSearchResult

# Module-level browser instance for reuse across requests
_browser: Browser | None = None
_playwright = None

GOODREADS_SEARCH_URL = "https://www.goodreads.com/search"
GOODREADS_BOOK_URL = "https://www.goodreads.com/book/show"


async def _random_delay(min_sec: float = 3.0, max_sec: float = 8.0):
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def get_browser() -> Browser:
    """Get or create a shared browser instance."""
    global _browser, _playwright
    if _browser is None or not _browser.is_connected():
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
    return _browser


async def _new_page() -> Page:
    """Create a new page with realistic browser context."""
    browser = await get_browser()
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
    )
    return await context.new_page()


async def _dismiss_modals(page: Page):
    """Dismiss sign-up or cookie modals."""
    close_selectors = [
        'button[aria-label="Close"]',
        'button[aria-label="close"]',
        'button[aria-label="Dismiss"]',
    ]
    for selector in close_selectors:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                await asyncio.sleep(1)
                return
        except Exception:
            continue
    try:
        await page.keyboard.press("Escape")
        await asyncio.sleep(1)
    except Exception:
        pass


async def search_books(query: str) -> list[BookSearchResult]:
    """Search for books on Goodreads by title/author."""
    page = await _new_page()
    try:
        url = f"{GOODREADS_SEARCH_URL}?q={query}"
        await page.goto(url, wait_until="domcontentloaded")
        await _random_delay(3, 5)
        await _dismiss_modals(page)

        # Wait for search results
        try:
            await page.wait_for_selector('table.tableList tr, [data-testid="searchResult"]', timeout=10000)
        except Exception:
            pass

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        results = []

        # Parse search results table
        rows = soup.select("table.tableList tr")
        for row in rows:
            book = _parse_search_row(row)
            if book:
                results.append(book)

        # Fallback: try alternative selectors if table not found
        if not results:
            cards = soup.select('[data-testid="searchResult"]')
            for card in cards:
                book = _parse_search_card(card)
                if book:
                    results.append(book)

        return results
    finally:
        await page.context.close()


def _parse_search_row(row) -> BookSearchResult | None:
    """Parse a search result from the table layout."""
    # Book link and title
    title_link = row.select_one("a.bookTitle")
    if not title_link:
        return None

    title = title_link.get_text(strip=True)
    href = title_link.get("href", "")

    # Extract book ID from href like /book/show/4671.The_Great_Gatsby
    book_id = _extract_book_id(href)
    if not book_id:
        return None

    # Author
    author_el = row.select_one("a.authorName")
    author = author_el.get_text(strip=True) if author_el else "Unknown"

    # Cover image
    img_el = row.select_one("img.bookCover, img")
    image_url = img_el.get("src", "") if img_el else ""

    return BookSearchResult(
        id=book_id,
        title=title,
        author=author,
        image_url=image_url,
        url=f"{GOODREADS_BOOK_URL}/{book_id}",
    )


def _parse_search_card(card) -> BookSearchResult | None:
    """Parse a search result from card/modern layout."""
    link = card.select_one("a[href*='/book/show/']")
    if not link:
        return None

    href = link.get("href", "")
    book_id = _extract_book_id(href)
    if not book_id:
        return None

    title = link.get_text(strip=True)

    author_el = card.select_one("a[href*='/author/']")
    author = author_el.get_text(strip=True) if author_el else "Unknown"

    img_el = card.select_one("img")
    image_url = img_el.get("src", "") if img_el else ""

    return BookSearchResult(
        id=book_id,
        title=title,
        author=author,
        image_url=image_url,
        url=f"{GOODREADS_BOOK_URL}/{book_id}",
    )


def _extract_book_id(href: str) -> str | None:
    """Extract numeric book ID from a Goodreads URL path."""
    # href like /book/show/4671.The_Great_Gatsby or /book/show/41733839-the-great-gatsby
    if "/book/show/" not in href:
        return None
    path = href.split("/book/show/")[-1]
    # Remove query params and fragments
    path = path.split("?")[0].split("#")[0].split("/")[0]
    # ID is digits before the first dot or hyphen
    book_id = ""
    for ch in path:
        if ch.isdigit():
            book_id += ch
        else:
            break
    return book_id if book_id else None


@dataclass
class ScrapedReview:
    """A single scraped review."""
    text: str
    rating: int | None


async def fetch_reviews(
    book_id: str,
    star_rating: int | None = None,
    max_reviews: int = 100,
) -> tuple[list[ScrapedReview], BookSearchResult | None]:
    """Fetch reviews for a book from Goodreads.

    Returns a tuple of (reviews, book_info). book_info is extracted from the
    book page header so the caller doesn't need a separate request.
    """
    page = await _new_page()
    try:
        url = f"{GOODREADS_BOOK_URL}/{book_id}"
        await page.goto(url, wait_until="domcontentloaded")
        await _random_delay(3, 5)
        await _dismiss_modals(page)

        # Extract book info from the page header
        book_info = await _extract_book_info(page, book_id)

        # Wait for reviews to load
        try:
            await page.wait_for_selector(".ReviewCard", timeout=15000)
        except Exception:
            await asyncio.sleep(5)

        # Apply star rating filter if requested
        if star_rating is not None:
            await _apply_star_filter(page, star_rating)

        # Paginate and collect reviews
        reviews = await _collect_reviews(page, max_reviews)

        return reviews, book_info
    finally:
        await page.context.close()


async def _extract_book_info(page: Page, book_id: str) -> BookSearchResult | None:
    """Extract book title, author, and image from the book page."""
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_el = soup.select_one('h1[data-testid="bookTitle"], h1.Text__title1')
    title = title_el.get_text(strip=True) if title_el else "Unknown"

    # Author
    author_el = soup.select_one(
        'span[data-testid="name"], .ContributorLink__name, a.ContributorLink'
    )
    author = author_el.get_text(strip=True) if author_el else "Unknown"

    # Cover image
    img_el = soup.select_one('img.ResponsiveImage, img[data-testid="coverImage"]')
    image_url = img_el.get("src", "") if img_el else ""

    return BookSearchResult(
        id=book_id,
        title=title,
        author=author,
        image_url=image_url,
        url=f"{GOODREADS_BOOK_URL}/{book_id}",
    )


async def _apply_star_filter(page: Page, star_rating: int):
    """Apply a star rating filter by clicking the histogram bar."""
    # The rating histogram bars are clickable and filter reviews
    # Try clicking the bar for the requested star rating
    histogram_selectors = [
        f'div.RatingsHistogram a[aria-label*="{star_rating} star"]',
        f'a[aria-label*="{star_rating} star"]',
        f'div.RatingsHistogram button[aria-label*="{star_rating}"]',
    ]

    for selector in histogram_selectors:
        try:
            bar = page.locator(selector).first
            if await bar.is_visible(timeout=3000):
                await bar.click()
                await _random_delay(3, 5)
                # Wait for reviews to reload
                try:
                    await page.wait_for_selector(".ReviewCard", timeout=10000)
                except Exception:
                    await asyncio.sleep(3)
                return
        except Exception:
            continue

    # Fallback: try the star text labels in the filter area
    try:
        star_label = page.locator(f'text="{star_rating} stars"').first
        if await star_label.is_visible(timeout=3000):
            await star_label.click()
            await _random_delay(3, 5)
            return
    except Exception:
        pass


async def _collect_reviews(page: Page, max_reviews: int) -> list[ScrapedReview]:
    """Collect reviews from the page, paginating as needed.

    Goodreads uses two pagination mechanisms:
    1. Book page: "More reviews and ratings" <a> link navigates to a reviews page.
    2. Reviews page: "Show more reviews" <button> replaces the current 30 reviews
       with the next 30 via GraphQL (not appending — the old reviews disappear).

    We must collect each batch before clicking for the next one.
    """
    all_reviews: list[ScrapedReview] = []
    seen_texts: set[str] = set()  # Deduplicate reviews

    # Max pagination attempts to avoid infinite loops
    max_pages = (max_reviews // 30) + 2

    def _harvest_reviews(soup):
        """Parse review cards from current page HTML, return new count."""
        cards = soup.select(".ReviewCard")
        new_count = 0
        for card in cards:
            review = _parse_review_card(card)
            if review and review.text:
                key = review.text[:100]
                if key not in seen_texts:
                    seen_texts.add(key)
                    all_reviews.append(review)
                    new_count += 1
        return new_count

    # Harvest first page
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    _harvest_reviews(soup)

    if len(all_reviews) >= max_reviews:
        return all_reviews[:max_reviews]

    # Step 1: Navigate from book page to reviews page via link
    navigated = await _navigate_to_reviews_page(page)

    if navigated:
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        new = _harvest_reviews(soup)

        if len(all_reviews) >= max_reviews:
            return all_reviews[:max_reviews]

        # Step 2: Click "Show more reviews" button repeatedly
        # Each click REPLACES the current 30 reviews with the next 30
        for _ in range(max_pages - 1):
            loaded = await _click_show_more_reviews(page)
            if not loaded:
                break

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            new = _harvest_reviews(soup)

            if new == 0 or len(all_reviews) >= max_reviews:
                break

    return all_reviews[:max_reviews]


async def _navigate_to_reviews_page(page: Page) -> bool:
    """Click 'More reviews and ratings' link to navigate to the reviews page.

    This link only appears on the book page (not on the reviews page).
    Returns True if navigation succeeded.
    """
    try:
        link = page.locator('a:has-text("More reviews and ratings")').first
        if await link.is_visible(timeout=5000):
            await link.scroll_into_view_if_needed()
            await _random_delay(2, 4)
            await link.click()
            await _random_delay(4, 7)
            await _dismiss_modals(page)
            try:
                await page.wait_for_selector(".ReviewCard", timeout=15000)
            except Exception:
                await asyncio.sleep(3)
            return True
    except Exception:
        pass

    return False


async def _click_show_more_reviews(page: Page) -> bool:
    """Click the 'Show more reviews' button on the reviews page.

    This button triggers a GraphQL call that replaces the current 30
    reviews with the next 30. Returns True if the click succeeded.
    """
    try:
        btn = page.locator('button:has-text("Show more reviews")').first
        if await btn.is_visible(timeout=5000):
            await btn.scroll_into_view_if_needed()
            await _random_delay(2, 4)
            await btn.click()
            await _random_delay(4, 7)
            await _dismiss_modals(page)
            try:
                await page.wait_for_selector(".ReviewCard", timeout=15000)
            except Exception:
                await asyncio.sleep(3)
            return True
    except Exception:
        pass

    return False


def _parse_review_card(card) -> ScrapedReview | None:
    """Extract review text and rating from a ReviewCard element."""
    rating = None
    text = None

    # Extract star rating from aria-label
    rating_el = card.select_one('[aria-label*="Rating"][aria-label*="out of"]')
    if rating_el:
        label = rating_el.get("aria-label", "")
        parts = label.split()
        for j, word in enumerate(parts):
            if word == "Rating" and j + 1 < len(parts):
                try:
                    rating = int(parts[j + 1])
                except ValueError:
                    pass
                break

    # Extract review text
    text_el = card.select_one(
        ".ReviewText__content .Formatted, .TruncatedContent .Formatted"
    )
    if text_el:
        text = text_el.get_text(strip=True)

    # Fallback: largest text block
    if not text:
        all_text = card.find_all(["span", "div", "p"])
        candidates = [(el, len(el.get_text(strip=True))) for el in all_text]
        candidates.sort(key=lambda x: x[1], reverse=True)
        for el, length in candidates:
            if length > 50:
                text = el.get_text(strip=True)
                break

    if text:
        return ScrapedReview(text=text, rating=rating)
    return None


async def shutdown_browser():
    """Clean up browser resources."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
