# AGENTS.md — Linta Project Coordination

> Canonical reference for AI agents and human contributors working on the Linta Linux distribution.
> The full specification lives in [README.md](README.md). This document governs *how* we build it.

---

## Project Identity

- **Name:** Linta
- **Type:** Fedora-derived Linux distribution
- **Target:** Developers and technical power users
- **Philosophy:** Lean by design. Ship infrastructure, not opinions about user workflow.
- **Profiles:** KDE Plasma, Niri, Combined, Bare

---

## Repository Structure

```
├── README.md              Canonical specification (do NOT restructure without lead approval)
├── AGENTS.md              This file — project coordination rules
├── docs/                  Roadmap, ADRs, design docs
├── build/
│   ├── kickstart/         Per-profile kickstart (.ks) files
│   ├── packages/          Package manifests (what RPMs go in each profile)
│   ├── iso/               ISO build scripts (lorax / livemedia-creator)
│   └── testing/           Automated test definitions
├── packages/              Custom Linta software (each subdir = one RPM)
│   ├── lintactl/          Main CLI tool
│   ├── linta-nvidia/      NVIDIA setup tool
│   ├── linta-welcome/     First-boot welcome app (Qt)
│   ├── linta-flatpak-manager/  Flatpak GUI (Qt)
│   ├── linta-keybindings/ Searchable keybinding reference
│   └── linta-snapshots/   Btrfs snapshot management
├── themes/                Visual identity
│   ├── kde/               KDE Plasma global theme
│   ├── niri/              Niri rice presets (rice-1 through rice-4)
│   ├── sddm/             SDDM login theme
│   ├── plymouth/          Boot splash
│   └── wallpapers/
├── configs/               Default dotfiles and system configs shipped with Linta
│   ├── zsh/               zshrc, p10k config, oh-my-zsh plugin list
│   ├── helix/             Helix editor defaults
│   ├── niri/              Niri compositor config
│   └── system/            System-level configs (firewalld, fstrim, btrfs, etc.)
├── installer/             TUI (ncurses) installer
└── scripts/               Dev/build helper scripts
```

---

## Architecture Rules

These are non-negotiable. Violating any of these requires explicit approval from the project lead.

1. **Fedora lineage.** All packages are RPMs. The build system inherits Fedora's tooling (mock, koji, lorax). Do not introduce alien package formats.
2. **Btrfs is load-bearing.** The transactional package manager, snapshot rollback, and backup strategy all depend on Btrfs. Never assume ext4 or XFS.
3. **Wayland only.** Niri profile has zero X11/Xwayland. KDE profile ships Xwayland as a compat shim only. Never add X11-only dependencies.
4. **Four profiles, always.** Every feature, config, and package manifest must declare which profiles it applies to: `[KDE]`, `[Niri]`, `[Combined]`, `[Bare]`, or `[All]`. The Combined profile is the union of KDE and Niri. The Bare profile has no GUI.
5. **SELinux enforcing.** Upstream Fedora policies. Do not write code that requires SELinux to be disabled or permissive.
6. **systemd native.** Use systemd units, timers, and tmpfiles. Do not introduce cron, SysV init scripts, or non-systemd service managers.
7. **No telemetry. Ever.** Zero data collection, zero phone-home, zero analytics. No opt-in. No opt-out. This is a hard constraint on every component.

---

## Code Conventions

### Languages

| Component type | Language | Notes |
|---|---|---|
| CLI tools (`lintactl`, `linta-nvidia`) | Python 3 | Fedora ships Python; fast iteration; use `argparse` or `click` |
| GUI apps (welcome, flatpak manager, keybindings) | Python + PyQt6 | Consistent stack; Qt for KDE visual consistency |
| System glue scripts | POSIX sh or Bash | Keep minimal; prefer systemd units over scripts |
| Configs | Native format | Use each tool's native config format (TOML, KDL, INI, etc.) |
| Packaging | RPM spec files | One `.spec` per package in `packages/<name>/` |

### Style

- Python: follow PEP 8, use type hints, target Python 3.12+
- Shell: `set -euo pipefail` in all bash scripts; quote all variables
- No vendored dependencies — all deps must be available as Fedora RPMs or PyPI packages buildable into RPMs
- Every `packages/<name>/` directory must contain: source code, an RPM `.spec` file, and a `README.md` explaining what it does

### Naming

- Package names: `linta-<component>` (e.g., `linta-nvidia`, `linta-welcome`)
- CLI tool binary: `lintactl`
- Theme names: `linta-theme-<variant>` (e.g., `linta-theme-kde`, `linta-theme-niri-rice1`)
- Config packages: `linta-config-<component>` (e.g., `linta-config-zsh`)

---

## Profile Awareness

Every commit, PR, and design decision must state which profiles are affected.

| Profile | Display server | Desktop | Xwayland | GUI apps |
|---|---|---|---|---|
| KDE | Wayland | KDE Plasma | Available | Full KDE + distro tools |
| Niri | Wayland | Niri compositor | **Not available** | Minimal: fuzzel, custom bar, distro tools |
| Combined | Wayland | KDE + Niri (switchable via SDDM) | Per-session | Union of KDE and Niri |
| Bare | None | TTY only | N/A | None |

**Combined = KDE ∪ Niri.** If something is in KDE or Niri, it is in Combined. Never add Combined-only packages.

**Bare is TTY-only.** It gets the dev toolchain, shell, helix, and system tools. No display manager, no compositor, no GUI apps.

---

## Theming Rules

- Each Niri rice is a **complete, coordinated visual preset**: status bar, terminal colors, notification styling, wallpaper, lock screen, launcher theme, color palette. No partial rices.
- The KDE theme is a **complete Plasma global theme**: color scheme, icon set, wallpaper, Kvantum/Breeze style, SDDM theme — all coordinated.
- Wallpapers are per-theme, not a standalone pack.
- Quality bar for Niri rices: polished enough for r/unixporn front page. If it looks like a default config with a changed wallpaper, it's not done.
- The SDDM theme and Plymouth theme must visually belong to the same identity family.

---

## Testing Requirements

- All custom tools (`lintactl`, `linta-nvidia`, etc.) must have unit tests
- Package manifests must be validated: every listed package must exist in Fedora repos or be built by us
- Kickstart files must be syntax-valid and testable in a VM
- Theme packages must install cleanly and activate without errors
- ISO builds must boot in QEMU/KVM before any release

---

## Forbidden Patterns

Do NOT:

- Add telemetry, analytics, or usage tracking of any kind
- Add syslog or syslog-ng — journald only
- Add X11-only applications or libraries to the Niri profile
- Introduce AUR-style community repos or Copr personal repos
- Ship dotfile management opinions (stow, chezmoi, etc.) — that's user territory
- Install Bluetooth or CUPS by default — they go in repos, not base
- Add Docker or Podman to the base install
- Ship an SSH server — only the client
- Hardcode paths that assume ext4 or non-Btrfs filesystems
- Add cron jobs — use systemd timers
- Bundle fonts on the ISO — fonts are installed by the first-boot font wizard from repos

---

## Workflow for AI Agents

### Before starting work

1. Read this file (`AGENTS.md`) and [README.md](README.md)
2. Check [docs/roadmap.md](docs/roadmap.md) for current phase and priorities
3. Identify which profiles your work affects

### When writing code

1. State the target profile(s) in your commit/PR description
2. Follow the language and style conventions above
3. Place files in the correct directory per the repo structure
4. Add an RPM `.spec` file for any new package

### When making decisions

1. Check if the decision is already made in README.md (Appendix A has 75 decisions)
2. If it's an open item (README.md §15), propose a resolution and document it in `docs/decisions/`
3. If it contradicts the spec, stop and flag it — do not silently override

### Commit messages

Format: `<area>: <what changed>`

Examples:
- `lintactl: add theme-switch subcommand`
- `build/packages: add niri profile package manifest`
- `themes/niri: rice-1 initial color palette and bar config`
- `configs/zsh: default zshrc with oh-my-zsh and p10k`

---

## Open Items

The following decisions from README.md §15 are still unresolved. When working near these areas, flag them rather than making assumptions:

- Release codename theme (Debian-style thematic names — theme not chosen)
- Final motto wording (direction: "Lean by design.")
- Niri rice visual designs (3-4 complete palettes needed)
- KDE custom theme visual direction
- File manager options for the first-boot chooser
- Email client final pick (Claws Mail vs Geary vs other)
- Memorable hostname word lists (adjective + noun)
- Automated testing gate implementation (openQA vs custom CI)
