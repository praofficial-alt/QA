"""Web regression suite (Playwright). Run with: pytest -m regression"""

from __future__ import annotations

import pytest


@pytest.mark.regression
def test_home_navigation_response_ok(page, base_url: str) -> None:
    """Home/load URL returns a successful HTTP status."""
    response = page.goto(base_url, wait_until="domcontentloaded")
    assert response is not None, f"No response navigating to {base_url}"
    assert response.ok, f"Expected 2xx for {base_url}, got {response.status}"


@pytest.mark.regression
def test_home_page_has_visible_body(page, base_url: str) -> None:
    """Document renders a non-empty body (catches blank/error shells)."""
    page.goto(base_url, wait_until="load")
    body = page.locator("body")
    text = body.inner_text(timeout=30_000).strip()
    assert text, "Expected non-empty body text"


@pytest.mark.regression
def test_viewport_and_document_ready(page, base_url: str) -> None:
    """Browser viewport is usable after load."""
    page.goto(base_url, wait_until="domcontentloaded")
    viewport = page.viewport_size
    assert viewport is not None
    assert viewport["width"] > 0 and viewport["height"] > 0
    ready = page.evaluate("document.readyState")
    assert ready in ("interactive", "complete")
