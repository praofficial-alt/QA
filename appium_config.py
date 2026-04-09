"""Appium capabilities and driver options (Android / UiAutomator2).

Imports are lazy so ``pytest -m "not appium"`` works without Appium installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from appium.options.android import UiAutomator2Options


def android_settings_options() -> "UiAutomator2Options":
    """Smoke: launch Android Settings (replace with your app under test)."""
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.set_capability("appium:appPackage", "com.android.settings")
    options.set_capability("appium:appActivity", ".Settings")
    options.set_capability("appium:noReset", True)
    options.set_capability("appium:autoGrantPermissions", True)
    return options


def android_apk_options(apk_path: str) -> "UiAutomator2Options":
    """Launch a local ``.apk`` (UiAutomator2). Use with Appium 2 server URL without ``/wd/hub``."""
    import os
    from pathlib import Path

    from appium.options.android import UiAutomator2Options

    p = Path(apk_path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"APK not found: {p}")

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.app = str(p)
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:noReset", False)
    device = os.environ.get("APPIUM_DEVICE_NAME", "Android").strip()
    if device:
        options.set_capability("appium:deviceName", device)
    return options
