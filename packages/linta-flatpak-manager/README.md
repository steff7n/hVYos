# linta-flatpak-manager

**Profiles:** [KDE], [Niri], [Combined]

Custom Flatpak management GUI for Linta Linux. Provides a distro-branded interface for browsing Flathub, installing and removing Flatpak applications, updating packages, and viewing permissions.

## Features

- **Installed** — List installed Flatpak applications with permissions view and removal
- **Browse** — Search and browse Flathub applications for installation
- **Updates** — View available updates and update all with one click
- **Search** — Filter applications across all tabs
- **Permissions** — View `flatpak info --show-permissions` output per app
- **Linta theme** — Dark palette (bg #1e1e2e, accent #00bcd4, text #cdd6f4)

## Spec Reference

- **README.md §2.3** — Flatpak integration: custom GUI, Flathub preconfigured, permissions management
- **README.md §9.3** — Flatpak Manager as part of distro-specific tooling

## Requirements

- Python 3.12+
- PyQt6
- flatpak (with Flathub remote configured)

## Building

```bash
rpmbuild -ba linta-flatpak-manager.spec
```
