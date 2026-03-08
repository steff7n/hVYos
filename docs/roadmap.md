# Linta Linux — Development Roadmap

Phased development plan for the Linta Linux distribution. Each phase builds on the previous and delivers concrete artifacts. Status reflects current project state as of roadmap creation.

---

## Phase 0 — Scaffolding

**Status:** Complete

### Description

Establish project structure, coordination rules, and foundational assets. Includes directory tree, AGENTS.md, git initialization, README updates, and initial package manifests.

### Deliverables

- Directory tree aligned with AGENTS.md
- AGENTS.md (AI agent and contributor coordination rules)
- .gitignore
- Package manifests per profile
- This roadmap document

### Dependencies

None

---

## Phase 1 — Build Foundation

**Status:** Complete

### Description

Refine package manifests, create kickstart files for all four profiles (KDE, Niri, Combined, Bare), and implement a basic ISO build pipeline using lorax/livemedia-creator.

### Deliverables

- Working kickstart files for all profiles
- Validated package lists
- Script that builds a bootable ISO

### Dependencies

Phase 0

---

## Phase 2 — Core System Tools

**Status:** Complete

### Description

Implement lintactl CLI (Python) with theme switching, profile info, font wizard re-run, and distro version display. Build linta-snapshots for Btrfs: pre-transaction snapshots, weekly scheduled snapshots, GRUB menu integration for last 5 snapshots, and snapshot browsing CLI. Ship default configs: zsh (oh-my-zsh + Powerlevel10k), helix editor, and system configs (firewalld defaults, fstrim.timer, btrfs maintenance, package cache pruning timer).

### Deliverables

- Working lintactl with RPM spec
- linta-snapshots with RPM spec
- Config packages (linta-config-zsh, linta-config-helix, linta-config-system)

### Dependencies

Phase 1 (needs bootable ISO to test against)

---

## Phase 3 — NVIDIA Tool

**Status:** Complete

### Description

Implement linta-nvidia: GPU detection, proprietary driver installation via RPM Fusion + akmod, DKMS config, Wayland compatibility flags (GBM backend), prime-run/prime-offload for hybrid laptops, Xwayland NVIDIA quirks (KDE profile), and status output.

### Deliverables

- Working linta-nvidia with RPM spec
- Tested on NVIDIA hardware or in passthrough VM

### Dependencies

Phase 2

---

## Phase 4 — Visual Identity

**Status:** Complete

### Description

Create KDE Plasma global theme (1 custom theme: color scheme, icon set, wallpaper, Kvantum style, coordinated with SDDM). Design 3–4 complete Niri rice presets, each with: status bar config via Waybar fork, terminal colors, notification styling, wallpaper, swaylock-effects appearance, fuzzel theming, and unified color palette. Implement SDDM login theme (distro-branded, coordinated with overall identity). Add Plymouth boot splash (minimal branded splash with progress indicator). Provide wallpapers (one per theme preset).

### Deliverables

- Installable theme packages with RPM specs

### Dependencies

Phase 2 (needs lintactl theme-switch to test switching)

---

## Phase 5 — First-Boot Experience

**Status:** Complete

### Description

Implement linta-welcome: Qt-based (PyQt6) welcome application shown on first boot. Include terminal emulator chooser with visual previews (WezTerm default; options: WezTerm, Tilix, Terminator, Alacritty, Kitty, foot, Ghostty). Add file manager chooser with visual previews. Implement font wizard with 4 preset tiers (Comprehensive, Standard, Per-Locale, Bare Minimum) plus manual toggle. Provide theme picker (select rice preset or KDE theme). Add timezone/locale confirmation. Include quick tips overlay.

### Deliverables

- Working linta-welcome with RPM spec
- systemd unit for first-boot trigger

### Dependencies

Phase 4 (needs themes to select from), Phase 2 (needs lintactl)

---

## Phase 6 — Flatpak Manager

**Status:** In Progress

### Description

Implement linta-flatpak-manager: Qt-based (PyQt6) GUI for Flatpak management. Browse and search Flathub, install/update/remove packages, manage permissions. Visual consistency with distro theme.

### Deliverables

- Working app with RPM spec

### Dependencies

Phase 4 (needs theme for styling)

---

## Phase 7 — Keybinding Reference

**Status:** In Progress

### Description

Implement linta-keybindings: searchable, filterable overlay showing all keybindings. Reads from KDE config (on Plasma) or Niri config (on Niri). Rofi-style overlay, keyboard-navigable, themed. Activated by a dedicated hotkey.

### Deliverables

- Working tool with RPM spec

### Dependencies

Phase 4 (needs theme)

---

## Phase 8 — TUI Installer

**Status:** In Progress

### Description

Implement ncurses-based text installer (Devuan-style). Profile selection (KDE, Niri, Combined, Bare). Hostname generation (memorable: adjective-noun, editable). Locale selection, timezone, disk encryption (LUKS2 opt-in). Disk partitioning with Btrfs subvolume setup (@ for /, @home for /home).

### Deliverables

- Working installer that can produce a functional Linta system

### Dependencies

Phase 5 (installer hands off to first-boot welcome app)

---

## Phase 9 — Documentation

**Status:** Not Started

### Description

Produce official docs: installation guide, first-boot walkthrough, NVIDIA setup, Btrfs snapshot management, Flatpak usage, Niri configuration, theme switching, lintactl reference. Polished, curated, core-team maintained (not a wiki).

### Deliverables

- Complete documentation set

### Dependencies

Phase 8 (all features exist to document)

---

## Phase 10 — Testing & CI

**Status:** Not Started

### Description

Implement automated testing gate (openQA or custom CI). ISO build pipeline automation. Package validation (every manifest entry exists in repos). Boot testing in QEMU/KVM.

### Deliverables

- CI pipeline
- Test suite
- Automated ISO builds

### Dependencies

Phase 9 (everything is built and documented)

---

## Milestone ISO Target

The first milestone ISO (e.g., **25.1**) requires **Phases 0–8** to be complete:

- Phases 0–2: Project and build infrastructure, core tools
- Phase 3: NVIDIA support (optional but deliverable)
- Phase 4: Visual identity and themes
- Phase 5: First-boot experience
- Phases 6–7: Flatpak manager and keybinding reference
- Phase 8: TUI installer

**Phases 9–10** (Documentation and Testing & CI) are ongoing parallel tracks that continue after the milestone ISO and support subsequent releases.
