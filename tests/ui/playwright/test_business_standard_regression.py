"""Regression suite for https://www.business-standard.com/ (Playwright)."""

from __future__ import annotations

import pytest

from utils.bs_playwright import (
    click_story_and_resolve_article_page,
    goto_bs_home,
    try_dismiss_consent_banners,
)


@pytest.mark.business_standard
@pytest.mark.regression
def test_bs_markets_landing_loads(page, bs_base_url: str) -> None:
    url = f"{bs_base_url}/markets"
    resp = page.goto(url, wait_until="domcontentloaded")
    try_dismiss_consent_banners(page)
    assert resp is not None and resp.ok
    title_l = (page.title() or "").lower()
    url_l = page.url.lower()
    assert (
        "market" in title_l or "/markets" in url_l or "business" in title_l
    ), f"Unexpected markets landing title/url: title={title_l!r} url={url_l!r}"


@pytest.mark.business_standard
@pytest.mark.regression
def test_bs_opinion_section_loads(page, bs_base_url: str) -> None:
    url = f"{bs_base_url}/opinion"
    resp = page.goto(url, wait_until="domcontentloaded")
    try_dismiss_consent_banners(page)
    assert resp is not None and resp.ok
    title = (page.title() or "").lower()
    assert "opinion" in title or "business" in title


@pytest.mark.business_standard
@pytest.mark.regression
def test_bs_open_first_home_story(page, bs_base_url: str) -> None:
    goto_bs_home(page, bs_base_url)
    home = (page.url or "").rstrip("/")
    candidates = page.locator('main a[href*=".html"], article a[href*=".html"]')
    if candidates.count() == 0:
        candidates = page.locator('a[href*="business-standard.com"][href*=".html"]')
    story = candidates.first
    story.wait_for(state="visible", timeout=20_000)
    article_page = click_story_and_resolve_article_page(
        page, story, timeout_s=90.0, click_timeout_ms=20_000
    )
    heading = article_page.locator("h1").first
    assert heading.is_visible(timeout=25_000)


@pytest.mark.business_standard
@pytest.mark.regression
def test_bs_footer_or_site_attribution(page, bs_base_url: str) -> None:
    goto_bs_home(page, bs_base_url)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    footer = page.locator("footer")
    if footer.count():
        text = footer.inner_text(timeout=10_000).lower()
        assert "business" in text or "standard" in text or "copyright" in text
    else:
        body = page.locator("body").inner_text(timeout=10_000).lower()
        assert "business standard" in body or "business-standard" in body
