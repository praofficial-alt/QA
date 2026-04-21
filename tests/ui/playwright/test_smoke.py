"""Web smoke tests (Playwright)."""

import pytest


@pytest.mark.regression
def test_ci_pipeline_wiring(base_url: str) -> None:
    assert base_url.startswith("http"), "Set BASE_URL / QA_BASE_URL for real runs"


@pytest.mark.regression
def test_playwright_available(page, base_url: str) -> None:
    """Uses pytest-playwright; replace with real UI flows."""
    page.goto(base_url)
    assert page.title()