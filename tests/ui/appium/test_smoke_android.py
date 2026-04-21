"""Android smoke tests (Appium). Run in CI ``appium-android`` job."""

import pytest


@pytest.mark.appium
@pytest.mark.regression
def test_android_settings_package(driver) -> None:
    """Opens Settings and asserts we are on the expected package."""
    assert driver.current_package == "com.android.settings"
