"""Helpers for https://www.business-standard.com/ UI tests."""

from __future__ import annotations

import re
import time

from playwright.sync_api import Locator, Page


def try_dismiss_consent_banners(page: Page) -> None:
    """Best-effort close for CMP / cookie prompts (wording varies)."""
    patterns = (
        re.compile(r"^(accept(\s+all)?|agree|ok|i\s+understand|allow\s+all)$", re.I),
        re.compile(r"accept", re.I),
    )
    for pat in patterns:
        try:
            btn = page.get_by_role("button", name=pat).first
            if btn.is_visible(timeout=1500):
                btn.click(timeout=3000)
                return
        except Exception:
            continue


def goto_bs_home(page: Page, base: str) -> None:
    url = base.rstrip("/") + "/"
    page.goto(url, wait_until="domcontentloaded")
    try_dismiss_consent_banners(page)


def click_story_and_resolve_article_page(
    page: Page,
    story: Locator,
    *,
    timeout_s: float = 45.0,
    click_timeout_ms: int = 15_000,
) -> Page:
    """
    Click a home-page story link and return the page that shows the article.

    Handles ``target=_blank`` (new tab) and same-tab navigations.
    """
    home = (page.url or "").rstrip("/")
    story.click(timeout=click_timeout_ms)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        pages = list(page.context.pages)
        if len(pages) >= 2:
            for p in pages:
                if p is page:
                    continue
                try:
                    u = (p.url or "").rstrip("/")
                except Exception:
                    continue
                if not u or u.startswith("about:") or u.startswith("chrome"):
                    continue
                if u != home and "business-standard.com" in u.lower():
                    p.wait_for_load_state("domcontentloaded", timeout=30_000)
                    return p
        try:
            cur = (page.url or "").rstrip("/")
        except Exception:
            cur = ""
        if cur and cur != home:
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
            return page
        time.sleep(0.12)
    raise AssertionError(
        f"No article navigation or new tab after story click (home was {home!r}, "
        f"still {page.url!r}, tabs={len(page.context.pages)})"
    )
