from unittest import mock

from unshuffle.updates import is_newer_version, parse_update_info


def test_update_info_parses_github_latest_release_assets():
    with mock.patch("unshuffle.updates.sys.platform", "win32"):
        info = parse_update_info(
            {
                "tag_name": "v1.0.1",
                "html_url": "https://github.com/calloga/unshuffle/releases/tag/v1.0.1",
                "assets": [
                    {
                        "name": "unshuffle_1.0.1_amd64.deb",
                        "browser_download_url": "https://example.test/unshuffle.deb",
                    },
                    {
                        "name": "UnshuffleWinSetup.exe",
                        "browser_download_url": "https://example.test/UnshuffleWinSetup.exe",
                    },
                ],
                "body": "Bug fixes.",
            }
        )

    assert info is not None
    assert info.version == "1.0.1"
    assert info.url == "https://github.com/calloga/unshuffle/releases/tag/v1.0.1"
    assert info.download_url == "https://example.test/UnshuffleWinSetup.exe"
    assert info.notes == "Bug fixes."


def test_update_info_prefers_macos_asset_on_macos():
    with mock.patch("unshuffle.updates.sys.platform", "darwin"):
        info = parse_update_info(_release_with_cross_platform_assets())

    assert info is not None
    assert info.download_url == "https://example.test/Unshuffle-macos.pkg"


def test_update_info_prefers_linux_asset_on_linux():
    with mock.patch("unshuffle.updates.sys.platform", "linux"):
        info = parse_update_info(_release_with_cross_platform_assets())

    assert info is not None
    assert info.download_url == "https://example.test/unshuffle_1.0.1_amd64.deb"


def test_update_info_prefers_windows_asset_on_windows():
    with mock.patch("unshuffle.updates.sys.platform", "win32"):
        info = parse_update_info(_release_with_cross_platform_assets())

    assert info is not None
    assert info.download_url == "https://example.test/UnshuffleWinSetup.exe"


def test_update_info_parses_simple_manifest():
    info = parse_update_info(
        {
            "version": "1.2.0",
            "url": "https://example.test/releases/1.2.0",
            "download_url": "https://example.test/UnshuffleSetup-1.2.0.exe",
        }
    )

    assert info is not None
    assert info.version == "1.2.0"
    assert info.url == "https://example.test/releases/1.2.0"
    assert info.download_url == "https://example.test/UnshuffleSetup-1.2.0.exe"


def test_version_comparison_uses_numeric_segments():
    assert is_newer_version("v1.0.1", "1.0.0")
    assert is_newer_version("1.10.0", "1.2.9")
    assert not is_newer_version("1.0.0", "1.0.0")
    assert not is_newer_version("1.0.0", "1.0.1")
    assert not is_newer_version("not-a-version", "1.0.0")


def _release_with_cross_platform_assets():
    return {
        "tag_name": "v1.0.1",
        "html_url": "https://github.com/calloga/unshuffle/releases/tag/v1.0.1",
        "assets": [
            {
                "name": "UnshuffleWinSetup.exe",
                "browser_download_url": "https://example.test/UnshuffleWinSetup.exe",
            },
            {
                "name": "Unshuffle-macos.pkg",
                "browser_download_url": "https://example.test/Unshuffle-macos.pkg",
            },
            {
                "name": "unshuffle_1.0.1_amd64.deb",
                "browser_download_url": "https://example.test/unshuffle_1.0.1_amd64.deb",
            },
        ],
    }
