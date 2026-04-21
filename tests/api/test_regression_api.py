"""API-level regression checks (stdlib only; no Postman dependency)."""

from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest

from utils.config import get_base_url


@pytest.mark.regression
def test_base_url_returns_success_status() -> None:
    """GET base URL must return HTTP 2xx (follows redirects)."""
    base = get_base_url()
    req = Request(
        base,
        method="GET",
        headers={"User-Agent": "QA-regression/1.0"},
    )
    try:
        with urlopen(req, timeout=30) as resp:
            assert 200 <= resp.status < 300, f"Unexpected status {resp.status} for {base}"
    except HTTPError as e:
        pytest.fail(f"HTTP error for {base}: {e.code} {e.reason}")
    except URLError as e:
        pytest.fail(f"Could not reach {base}: {e.reason}")
