"""
Business Standard smoke scenarios (homepage, nav, article, search, API reachability).

Uses ``bs_base_url`` so CI/local runs align with ``BASE_URL`` on business-standard.com.
"""

from __future__ import annotations

import re

import pytest
import requests

from utils.bs_playwright import (
    click_story_and_resolve_article_page,
    goto_bs_home,
    try_dismiss_consent_banners,
)
from utils.config import get_base_url

# Plain ``requests`` often gets 403 from this host without browser-like headers.
_BS_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


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
    markets.click(timeout=20_000)
    page.wait_for_load_state("domcontentloaded")
    assert "markets" in page.url.lower(), f"Unexpected URL after Markets click: {page.url!r}"


@pytest.mark.business_standard
@pytest.mark.smoke
def test_open_article(page, bs_base_url: str) -> None:
    """First article opens; headline (h1) visible (same tab or new tab)."""
    goto_bs_home(page, bs_base_url)
    story = page.locator("article a").first
    story.wait_for(state="visible", timeout=20_000)
    article_page = click_story_and_resolve_article_page(page, story)
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
    box.fill("economy", timeout=15_000)
    box.press("Enter")
    page.wait_for_load_state("domcontentloaded", timeout=45_000)
    assert "search" in page.url.lower(), f"Expected search in URL, got {page.url!r}"


@pytest.mark.business_standard
@pytest.mark.smoke
def test_api_health() -> None:
    """Home URL responds HTTP 200 (backend reachable; no hard downtime)."""
    base = get_base_url().rstrip("/")
    if "business-standard.com" not in base.lower():
        pytest.skip("Set BASE_URL to business-standard.com for this smoke suite")
    url = base + "/"
    response = requests.get(url, headers=_BS_REQUEST_HEADERS, timeout=45)
    assert response.status_code == 200, f"GET {url!r} returned {response.status_code}"
