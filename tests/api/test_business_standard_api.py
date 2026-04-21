"""HTTP smoke/regression for business-standard.com (Playwright request API).

Plain ``urllib`` often gets HTTP 403 from this host; Playwright uses the same
TLS stack as the browser tests and is accepted.
"""

from __future__ import annotations

from urllib.parse import urljoin

import pytest
from playwright.sync_api import sync_playwright

from utils.config import get_base_url

# Browser-like headers reduce HTTP 403 from CDNs when using the Playwright request API.
_BS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _require_bs_host() -> str:
    base = get_base_url().rstrip("/")
    if "business-standard.com" not in base.lower():
        pytest.skip("business_standard API tests expect BASE_URL on business-standard.com")
    return base


@pytest.mark.business_standard
@pytest.mark.smoke
def test_bs_api_home_returns_200() -> None:
    base = _require_bs_host()
    with sync_playwright() as p:
        ctx = p.request.new_context(extra_http_headers=_BS_HEADERS)
        try:
            resp = ctx.get(base + "/", timeout=60_000)
            try:
                assert resp.ok, f"GET home: {resp.status} — {resp.text()[:400]!r}"
            finally:
                resp.dispose()
        finally:
            ctx.dispose()


@pytest.mark.business_standard
@pytest.mark.regression
def test_bs_api_markets_path_returns_200() -> None:
    base = _require_bs_host()
    url = urljoin(base + "/", "markets")
    with sync_playwright() as p:
        ctx = p.request.new_context(extra_http_headers=_BS_HEADERS)
        try:
            resp = ctx.get(url, timeout=60_000)
            try:
                assert resp.ok, f"GET markets: {resp.status} — {resp.text()[:400]!r}"
            finally:
                resp.dispose()
        finally:
            ctx.dispose()
