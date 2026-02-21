"""Goodreads scraper using Playwright for browser automation."""

import asyncio
import random
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

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


async def shutdown_browser():
    """Clean up browser resources."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
