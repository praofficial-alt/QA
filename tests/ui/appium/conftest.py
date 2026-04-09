from __future__ import annotations

import os

import pytest

from utils.config import get_appium_server_url


def _skip_if_disabled() -> None:
    if os.environ.get("SKIP_APPIUM_TESTS") == "1":
        pytest.skip("SKIP_APPIUM_TESTS=1 (local runs without emulator)")


@pytest.fixture
def driver():
    _skip_if_disabled()
    try:
        import appium_config
        from appium import webdriver
    except ImportError as e:
        pytest.skip(
            "Appium is not installed. Run: pip install -r requirements-appium.txt "
            f"(or use Python 3.12 if install fails on 3.13). ({e})"
        )

    url = get_appium_server_url()
    options = appium_config.android_settings_options()
    drv = webdriver.Remote(url, options=options)
    try:
        yield drv
    finally:
        drv.quit()
