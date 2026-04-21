"""
Login E2E (Playwright).

This repo uses **pytest-playwright** (`page` fixture), not `sync_playwright()` in the test body.
That gives you: browser install reuse in CI, traces, video, parallel workers, and one pattern
across all UI tests.

Enable a real login run with env vars (local or CI). If disabled, the test is skipped so
`https://example.com` smoke runs stay green.
"""

from __future__ import annotations

import os

import pytest

_LOGIN_ON = os.environ.get("E2E_LOGIN_ENABLED", "").strip() == "1"


def _login_env() -> dict[str, str]:
    user = os.environ.get("E2E_USERNAME", "").strip()
    pwd = os.environ.get("E2E_PASSWORD", "").strip()
    if not user or not pwd:
        pytest.skip("E2E_LOGIN_ENABLED=1 requires E2E_USERNAME and E2E_PASSWORD.")
    return {
        "user": user,
        "password": pwd,
        "path": os.environ.get("E2E_LOGIN_PATH", "/login").strip() or "/login",
        "user_sel": os.environ.get("E2E_USER_SELECTOR", "#username"),
        "pass_sel": os.environ.get("E2E_PASS_SELECTOR", "#password"),
        "submit_sel": os.environ.get("E2E_SUBMIT_SELECTOR", "#login"),
        "title_contains": os.environ.get("E2E_EXPECT_TITLE_CONTAINS", "Dashboard"),
    }


@pytest.mark.regression
@pytest.mark.skipif(
    not _LOGIN_ON,
    reason="Optional login E2E: set E2E_LOGIN_ENABLED=1, E2E_USERNAME, E2E_PASSWORD (see README).",
)
def test_login(page, base_url: str) -> None:
    cfg = _login_env()
    url = f"{base_url.rstrip('/')}{cfg['path']}"
    page.goto(url)
    page.fill(cfg["user_sel"], cfg["user"])
    page.fill(cfg["pass_sel"], cfg["password"])
    page.click(cfg["submit_sel"])
    assert cfg["title_contains"] in (page.title() or "")
