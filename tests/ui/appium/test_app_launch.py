"""
Install/launch a real Android ``.apk`` via Appium.

This matches the *intent* of a raw ``webdriver.Remote(..., caps)`` test, but uses:

- **Appium 2** + **UiAutomator2Options** (same as the rest of this repo)
- Server URL from ``APPIUM_SERVER_URL`` (default ``http://127.0.0.1:4723``) — **not** ``/wd/hub`` (Appium 1)

Skipped unless ``APPIUM_APP`` points to an existing file so CI and clones without an APK stay green.
Do not commit large ``.apk`` files; pass path via env or CI artifact.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from utils.config import get_appium_server_url


def _skip_appium_common() -> None:
    if os.environ.get("SKIP_APPIUM_TESTS") == "1":
        pytest.skip("SKIP_APPIUM_TESTS=1 (local runs without emulator)")


@pytest.fixture
def driver_apk():
    _skip_appium_common()
    try:
        import appium_config
        from appium import webdriver
    except ImportError as e:
        pytest.skip(
            "Appium is not installed. Run: pip install -r requirements-appium.txt "
            f"(or use Python 3.12 if install fails on 3.13). ({e})"
        )

    raw = os.environ.get("APPIUM_APP", "").strip()
    if not raw:
        pytest.skip(
            "Set APPIUM_APP to the path of your .apk (e.g. android_superup_uat_0704.apk)."
        )
    apk = Path(raw).expanduser()
    if not apk.is_file():
        pytest.skip(f"APPIUM_APP not found: {apk}")

    url = get_appium_server_url()
    options = appium_config.android_apk_options(str(apk))
    drv = webdriver.Remote(url, options=options)
    try:
        yield drv
    finally:
        drv.quit()


@pytest.mark.appium
@pytest.mark.regression
def test_app_launch(driver_apk) -> None:
    assert driver_apk.session_id
    size = driver_apk.get_window_size()
    assert size.get("width", 0) > 0
