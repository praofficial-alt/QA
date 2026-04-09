"""Paths and environment-backed settings."""

from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_base_url() -> str:
    return os.environ.get("BASE_URL", "https://example.com").rstrip("/")


def get_appium_server_url() -> str:
    return os.environ.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")


def reports_dir() -> Path:
    return project_root() / "reports"
