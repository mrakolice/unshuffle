# Changelog

## 1.0.1 - 2026-06-22

- Fix PyInstaller packaging dependency for `backports` namespace packages (resolving Linux launch crash).
- Package missing GUI theme stylesheet files in PyInstaller binary output.
- Reduce C++ extractor maximum audio decoding cap from 60s to 20s to prevent excessive CPU/memory usage.
- Centralize scan concurrency limits and introduce bounded task submission queueing to resolve macOS userspace watchdog panics.
- Add MAC address and hostname fallback comparisons to engine lock negotiation to prevent false-positive lock blocks after reboots or DHCP renames.
- Add checkable "High Performance Scan" option under the Library menu and Launcher to toggle low-resource scan worker limits.
- Fix scan monitor window background rendering white by enabling `Qt.WA_StyledBackground`.
- Fix launcher folder registration when multiple folders are processed.

## 1.0.0 - 2026-06-11

- First public release of Unshuffle.
