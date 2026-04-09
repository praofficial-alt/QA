"""
Defaults for pytest-playwright.

Override via env: ``PLAYWRIGHT_BROWSER``, ``PLAYWRIGHT_TIMEOUT_MS``, ``BASE_URL``.
"""

from __future__ import annotations

import os

DEFAULT_BROWSER = os.environ.get("PLAYWRIGHT_BROWSER", "chromium")
DEFAULT_TIMEOUT_MS = int(os.environ.get("PLAYWRIGHT_TIMEOUT_MS", "30000"))
