"""Cross-cutting pytest hooks for ``tests/``."""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip Business Standard tests on GitHub-hosted CI unless explicitly enabled.

    ``www.business-standard.com`` sits behind Akamai; datacenter IPs (including
    ``github-hosted`` runners) typically get HTTP 403, so UI/API checks cannot
    succeed in the default QA Pipeline. Run those tests locally, or set repo
    variable ``RUN_BUSINESS_STANDARD_CI`` to ``1`` only if traffic is allowlisted.
    """
    if os.environ.get("CI") != "true":
        return
    if os.environ.get("RUN_BUSINESS_STANDARD_CI") == "1":
        return

    reason = (
        "business-standard.com blocks GitHub-hosted runners (HTTP 403 from CDN/WAF). "
        "Run locally with BASE_URL=https://www.business-standard.com or set Actions "
        "variable RUN_BUSINESS_STANDARD_CI=1 if your runners are allowlisted."
    )
    skip_mark = pytest.mark.skip(reason=reason)
    for item in items:
        if item.get_closest_marker("business_standard"):
            item.add_marker(skip_mark)
