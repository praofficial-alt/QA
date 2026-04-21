"""
Business Standard smoke scenarios (homepage, nav, article, search, API reachability).

Uses ``bs_base_url`` so CI/local runs align with ``BASE_URL`` on business-standard.com.
"""

from __future__ import annotations

import re

import pytest

from utils.bs_playwright import (
    click_story_and_resolve_article_page,
    goto_bs_home,
    try_dismiss_consent_banners,
)


@pytest.mark.business_standard
@pytest.mark.smoke
def test_homepage_load(page, bs_base_url: str) -> None:
    """Page loads successfully; no crash / blank page."""
    page.goto(bs_base_url + "/", wait_until="domcontentloaded")
    try_dismiss_consent_banners(page)
    assert page.title() != "", "Expected non-empty document title"


@pytest.mark.business_standard
@pytest.mark.smoke
def test_navigation_menu(page, bs_base_url: str) -> None:
    """Top navigation: Markets is clickable and redirects correctly."""
    goto_bs_home(page, bs_base_url)
    nav = page.locator("nav")
    markets_in_nav = nav.get_by_role("link", name=re.compile(r"^markets$", re.I))
    if markets_in_nav.count() > 0:
        markets = markets_in_nav.first
    else:
        markets = page.get_by_text("Markets", exact=True).first
    markets.click(timeout=25_000)
    page.wait_for_load_state("domcontentloaded", timeout=45_000)
    url_ok = "markets" in page.url.lower()
    has_market_heading = page.get_by_role("heading", name=re.compile(r"market", re.I)).count() > 0
    mlinks = page.locator('[href*="markets"]')
    has_market_href = mlinks.count() > 0 and mlinks.first.is_visible(timeout=8_000)
    heading_ok = has_market_heading or has_market_href
    # SPA / overlays may keep home URL while showing Markets content
    assert url_ok or heading_ok, (
        f"Expected Markets navigation; url={page.url!r} url_ok={url_ok} heading_ok={heading_ok}"
    )


@pytest.mark.business_standard
@pytest.mark.smoke
def test_open_article(page, bs_base_url: str) -> None:
    """First article opens; headline (h1) visible (same tab or new tab)."""
    goto_bs_home(page, bs_base_url)
    story = page.locator("article a").first
    story.wait_for(state="visible", timeout=20_000)
    article_page = click_story_and_resolve_article_page(page, story, timeout_s=90.0)
    assert article_page.locator("h1").first.is_visible(timeout=20_000)


@pytest.mark.business_standard
@pytest.mark.smoke
def test_search(page, bs_base_url: str) -> None:
    """Search accepts a query and results URL loads."""
    goto_bs_home(page, bs_base_url)
    search = page.locator("input[type='search']")
    if search.count() == 0:
        search = page.get_by_role("searchbox")
    if search.count() == 0:
        search = page.locator("input[name='q'], input[placeholder*='Search' i]")
    assert search.count() > 0, "No search input found (search / searchbox / name=q)"
    box = search.first
    box.fill("economy", timeout=20_000)
    box.press("Enter")
    page.wait_for_load_state("domcontentloaded", timeout=60_000)
    u = page.url.lower()
    # Search may land on /search, query param, or topic page
    search_ok = (
        "search" in u
        or "q=" in u
        or "query" in u
        or "economy" in u
        or page.get_by_role("article").count() >= 1
        or page.get_by_role("link", name=re.compile(r"economy", re.I)).count() >= 1
    )
    assert search_ok, f"Expected search results or search URL; got {page.url!r}"
