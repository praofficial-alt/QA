"""Smoke suite for https://www.business-standard.com/ (Playwright)."""

from __future__ import annotations

import pytest

from utils.bs_playwright import goto_bs_home


@pytest.mark.business_standard
@pytest.mark.smoke
def test_bs_home_http_ok(page, bs_base_url: str) -> None:
    resp = page.goto(bs_base_url + "/", wait_until="domcontentloaded")
    assert resp is not None and resp.ok, f"Home should return 2xx, got {getattr(resp, 'status', None)}"


@pytest.mark.business_standard
@pytest.mark.smoke
def test_bs_home_title_and_branding(page, bs_base_url: str) -> None:
    goto_bs_home(page, bs_base_url)
    title = page.title() or ""
    html = page.content().lower()
    assert "business-standard.com" in html or "business standard" in title.lower(), (
        f"Expected BS branding in page or title; title={title!r}"
    )


@pytest.mark.business_standard
@pytest.mark.smoke
def test_bs_home_main_content_links(page, bs_base_url: str) -> None:
    goto_bs_home(page, bs_base_url)
    main = page.locator("main")
    scope = main.first if main.count() else page.locator("body")
    links = scope.get_by_role("link")
    assert links.count() >= 3, "Expected multiple story/navigation links on home"


@pytest.mark.business_standard
@pytest.mark.smoke
def test_bs_primary_navigation_visible(page, bs_base_url: str) -> None:
    goto_bs_home(page, bs_base_url)
    nav = page.locator("nav").first
    assert nav.is_visible(timeout=15_000), "Expected visible header/nav"
