"""Smoke tests — extend with Playwright + your QA app."""

import os

import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "https://example.com").rstrip("/")


def test_ci_pipeline_wiring(base_url: str) -> None:
    assert base_url.startswith("http"), "Set BASE_URL / QA_BASE_URL for real runs"


def test_playwright_available(page) -> None:
    """Uses pytest-playwright; replace with real UI flows."""
    page.goto("https://example.com")
    assert page.title()
