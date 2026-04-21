import os
import re

import pytest

from utils.config import get_base_url


@pytest.fixture(scope="session")
def base_url() -> str:
    return get_base_url()


@pytest.fixture(autouse=True)
def _playwright_timeouts(page) -> None:
    """Slow news sites: allow override via PLAYWRIGHT_TIMEOUT_MS (default 60s)."""
    ms = int(os.environ.get("PLAYWRIGHT_TIMEOUT_MS", "60000"))
    page.set_default_timeout(ms)
    page.set_default_navigation_timeout(ms)


@pytest.fixture
def bs_base_url(base_url: str) -> str:
    """business_standard tests expect BASE_URL on business-standard.com."""
    normalized = re.sub(r"^https?://(www\.)?", "", base_url.rstrip("/"), flags=re.I)
    if "business-standard.com" not in normalized.lower():
        pytest.skip(
            "business_standard tests require BASE_URL on business-standard.com "
            f"(got {base_url!r})"
        )
    return base_url.rstrip("/")
