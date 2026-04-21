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
    box.fill("economy", timeout=15_000)
    box.press("Enter")
    page.wait_for_load_state("domcontentloaded", timeout=45_000)
    assert "search" in page.url.lower(), f"Expected search in URL, got {page.url!r}"
