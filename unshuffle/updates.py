from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import sys
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .core.constants import APP_VERSION

DEFAULT_UPDATE_FEED_URL = "https://api.github.com/repos/calloga/unshuffle/releases/latest"
UPDATE_FEED_ENV = "UNSHUFFLE_UPDATE_FEED_URL"


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    url: str
    download_url: str = ""
    title: str = ""
    notes: str = ""


def configured_update_feed_url() -> str:
    return os.environ.get(UPDATE_FEED_ENV, "").strip() or DEFAULT_UPDATE_FEED_URL


def fetch_update_info(feed_url: str | None = None, *, timeout: float = 5.0) -> UpdateInfo | None:
    url = (feed_url or configured_update_feed_url()).strip()
    if not url:
        return None
    request = Request(url, headers={"Accept": "application/json", "User-Agent": f"Unshuffle/{APP_VERSION}"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return parse_update_info(payload)


def parse_update_info(payload: dict[str, Any]) -> UpdateInfo | None:
    version = _clean_version(str(payload.get("version") or payload.get("tag_name") or payload.get("name") or ""))
    if not version:
        return None

    release_url = str(payload.get("url") or payload.get("html_url") or payload.get("release_url") or "").strip()
    download_url = str(payload.get("download_url") or payload.get("installer_url") or "").strip()
    if not download_url:
        download_url = _download_url_from_assets(payload.get("assets"))
    if not release_url:
        release_url = download_url
    if not release_url and not download_url:
        return None

    return UpdateInfo(
        version=version,
        url=release_url,
        download_url=download_url,
        title=str(payload.get("title") or payload.get("name") or "").strip(),
        notes=str(payload.get("notes") or payload.get("body") or "").strip(),
    )


def is_newer_version(candidate: str, current: str = APP_VERSION) -> bool:
    candidate_parts = _version_parts(candidate)
    current_parts = _version_parts(current)
    if not candidate_parts or not current_parts:
        return False
    width = max(len(candidate_parts), len(current_parts))
    candidate_parts.extend([0] * (width - len(candidate_parts)))
    current_parts.extend([0] * (width - len(current_parts)))
    return candidate_parts > current_parts


def _download_url_from_assets(assets: Any) -> str:
    if not isinstance(assets, list):
        return ""
    preferred = _preferred_asset_suffixes(sys.platform)
    platform_match = ""
    installer_match = ""
    fallback = ""
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        url = str(asset.get("browser_download_url") or asset.get("download_url") or "").strip()
        name = str(asset.get("name") or "").lower()
        if not url:
            continue
        if not fallback:
            fallback = url
        if _matches_suffix(name, preferred):
            if _looks_like_installer(name):
                return url
            if not platform_match:
                platform_match = url
        if not installer_match and _looks_like_installer_asset(name):
            installer_match = url
    return platform_match or installer_match or fallback


def _preferred_asset_suffixes(platform_name: str) -> tuple[str, ...]:
    if platform_name == "win32":
        return (".exe", ".msi")
    if platform_name == "darwin":
        return (".pkg", ".dmg", ".zip")
    if platform_name.startswith("linux"):
        return (".deb", ".rpm", ".appimage", ".tar.gz", ".tgz")
    return (".exe", ".msi", ".pkg", ".dmg", ".deb", ".rpm", ".appimage", ".tar.gz", ".tgz", ".zip")


def _matches_suffix(name: str, suffixes: tuple[str, ...]) -> bool:
    return any(name.endswith(suffix) for suffix in suffixes)


def _looks_like_installer(name: str) -> bool:
    return any(token in name for token in ("setup", "installer", "install", "unshuffle"))


def _looks_like_installer_asset(name: str) -> bool:
    return _matches_suffix(
        name,
        (".exe", ".msi", ".pkg", ".dmg", ".deb", ".rpm", ".appimage", ".tar.gz", ".tgz", ".zip"),
    )


def _clean_version(value: str) -> str:
    value = value.strip()
    if value.lower().startswith("v"):
        value = value[1:]
    match = re.search(r"\d+(?:\.\d+){0,3}", value)
    return match.group(0) if match else ""


def _version_parts(value: str) -> list[int]:
    cleaned = _clean_version(value)
    if not cleaned:
        return []
    return [int(part) for part in cleaned.split(".")]
