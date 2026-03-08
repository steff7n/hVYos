# Linta

> *"Lean by design."*

## Overview

A Fedora-derived Linux distribution targeting developers and technical power users. Ships as a gated rolling release — packages roll continuously but must pass automated testing before reaching users — backed by transactional Btrfs snapshots for instant rollback. Periodic milestone ISOs (every 6–12 months) provide named snapshots for new installations. Offers four installation profiles — KDE Plasma, Niri (scrollable tiling Wayland compositor), Combined, and Bare — each with distinct UX philosophies and a cohesive visual identity.

This document is the canonical specification for building the distribution. It is intended to be consumed by human developers and/or AI agents as an authoritative reference.

---

## 1. Foundation & Core System

### 1.1 Base Lineage

- **Parent distribution:** Fedora Linux (fork)
- **Inherited infrastructure:** RPM packaging ecosystem, Fedora build tooling, upstream kernel and package sources
- **Divergences from upstream:** Btrfs-specific transactional package management (see §2.1), custom tooling (see §9), visual identity (see §7), gated rolling release model (see §1.4)

### 1.2 Init System

- **Init:** systemd
- **Rationale:** Industry standard, broad ecosystem support, tight integration with journald, networkd (unused — see §3.4), logind, and the broader Linux desktop stack. No ideological objection.

### 1.3 C Library

- **Default:** glibc (GNU C Library)
- **Rationale:** Inherited from Fedora. Maximum compatibility with the entire RPM package ecosystem, proprietary software, and third-party binaries. Zero recompilation overhead — all upstream Fedora packages work as-is.
- **Developer note:** Standard glibc, no modifications. This is a deliberate compatibility-first decision.

### 1.4 Release Model

- **Type:** Gated rolling release
- **Mechanism:** Packages flow continuously from upstream Fedora and are rebuilt for this distro. Before reaching users, each batch must pass automated integration testing (openQA or equivalent). Packages that fail testing are held until fixed.
- **Milestone ISOs:** Every 6–12 months, the rolling repos are snapshotted into a named milestone ISO for new installations. Existing users simply keep rolling — milestones are entry points, not upgrades.
- **Naming convention:** Debian-style codenames drawn from a thematic set (theme TBD by project lead), accompanied by sequential milestone numbers (e.g., `25.1 "Codename"`, `25.2 "Codename"`)
- **Security policy:** Security patches arrive as upstream ships them — no backporting required. The rolling model ensures users always have the latest fixes.
- **Rationale:** Btrfs transactional snapshots (§3.2) provide instant rollback if any update causes issues, eliminating the primary risk of rolling releases. A long point-release cycle would be a redundant safety mechanism that also introduces the burden of backporting security patches — unnecessary work for a small team.

### 1.5 Kernel Policy

- **Kernel selection:** Latest stable kernel, updated as part of the rolling release pipeline
- **Testing:** Kernel updates pass through the same automated testing gate as all other packages
- **Rollback:** If a kernel update causes issues, Btrfs snapshot rollback restores the previous kernel instantly
- **Configuration:** Standard kernel config, no custom scheduler patches or CPU-specific optimizations

---

## 2. Package Management

### 2.1 Package Format & Manager

- **Format:** Traditional binary packages (RPM-based, inherited from Fedora)
- **Package manager behavior:** Transactional — every operation is atomic. If any step of an install/upgrade/remove fails, the entire transaction is rolled back. No partial state.
- **Implementation:** Transactional operations backed by Btrfs snapshots. A pre-transaction snapshot is created automatically before every package operation. Failed transactions restore the previous snapshot.

### 2.2 Repository Structure

- **Official repos:** Curated, tested, maintained by the core team
- **Community packages:** NOT supported via an AUR-equivalent or Copr-style personal repos
- **Supplementary software:** Flatpak is the official mechanism for software not in the official repositories

### 2.3 Flatpak Integration

- **Runtime:** Flatpak runtime preinstalled on all profiles
- **Remote:** Flathub preconfigured and available out of the box
- **GUI frontend:** A custom, distro-branded Flatpak management application (not Discover, not GNOME Software). Must support:
  - Browsing and searching Flathub
  - Installing, updating, removing Flatpaks
  - Managing Flatpak permissions
  - Visual consistency with the distro's theme

### 2.4 Containerization & Virtualization

- **Default:** Neither Podman nor Docker preinstalled
- **Availability:** Both available in official repos for user installation
- **Rationale:** Containers are not load-bearing infrastructure for this distro's package strategy

---

## 3. System Infrastructure

### 3.1 Filesystem

- **Default:** Btrfs
- **Configuration:** Conservative — no exotic subvolume layouts, no Btrfs RAID. Standard subvolume split (`@` for `/`, `@home` for `/home`). CoW enabled. Transparent compression (zstd) enabled.
- **Rationale:** Btrfs provides native snapshot/rollback support required by the transactional package manager (§2.1) and backup strategy (§6.3)

### 3.2 Snapshot & Rollback Policy

- **Automatic snapshots:**
  - Before every package transaction (install, update, remove)
  - Weekly scheduled snapshot: every Monday at 00:00:00 UTC
- **Retention:** Last 5 snapshots accessible from the GRUB boot menu
- **Rollback mechanism:** User selects a snapshot from GRUB, boots into it. One-click rollback.
- **Snapshot browsing:** Users can browse and manage snapshots via CLI tooling

### 3.3 Logging

- **System:** journald only (no syslog forwarding)
- **Querying:** `journalctl` is the canonical log interface
- **Rotation:** systemd-journald defaults — size-limited, time-rotated

### 3.4 Network Management

- **Manager:** NetworkManager
- **Rationale:** GUI-friendly, handles Wi-Fi/VPN/Ethernet, integrates with KDE Plasma's network applet

### 3.5 Firewall

- **Default:** firewalld, enabled out of the box
- **Integration:** Works with NetworkManager zone assignment
- **Default zone:** Appropriate for desktop use (public zone with sane defaults)

### 3.6 Audio

- **Stack:** PipeWire, preinstalled and preconfigured
- **Session manager:** WirePlumber
- **Compatibility:** PulseAudio and ALSA compatibility layers active

### 3.7 Bluetooth & Printing

- **Bluetooth:** Available in official repos but NOT preinstalled
- **Printing (CUPS):** Available in official repos but NOT preinstalled
- **Rationale:** Not all hardware has Bluetooth; not all users print. Install on demand.

### 3.8 Power Management

- **Tool:** power-profiles-daemon
- **Integration:** Native KDE Plasma system tray toggle (Power/Balanced/Performance)
- **Rationale:** Minimal configuration, DE integration out of the box

### 3.9 Automatic Maintenance

The following tasks run on automated schedules:

| Task | Schedule | Notes |
|---|---|---|
| SSD TRIM | Weekly (fstrim.timer) | Enabled on SSD-equipped systems |
| Journal log rotation | Per journald defaults | Size and time limited |
| Temporary file cleanup | On boot + daily (systemd-tmpfiles) | Standard systemd behavior |
| Package cache pruning | Weekly | Remove cached packages older than 30 days |

---

## 4. Security

### 4.1 Mandatory Access Control

- **Framework:** SELinux
- **Default mode:** Enforcing, using upstream Fedora security policies
- **Rationale:** Fedora's entire security infrastructure assumes SELinux — all package scriptlets, integration testing, and upstream policy work is built around it. Inheriting this wholesale saves months of security engineering that would otherwise be spent writing AppArmor profiles from scratch. Fedora's SELinux policies are battle-tested across millions of installations.

### 4.2 User Privilege Model

- **Mechanism:** sudo
- **Configuration:** Default user created during install is added to sudo group

### 4.3 Disk Encryption

- **Mechanism:** LUKS2 full-disk encryption
- **Default:** Offered prominently during installation, but OFF by default — user opts in
- **Implementation:** Standard dm-crypt/LUKS2 with passphrase

### 4.4 SSH

- **OpenSSH server:** NOT preinstalled. No listening services by default.
- **OpenSSH client:** Preinstalled on all profiles.
- **Rationale:** This is a developer-focused distro. `git clone git@github.com:...` must work on first boot. The client opens outbound connections; the server accepts inbound ones. Only the server is a security surface. Shipping a developer distro without an SSH client would be architectural malpractice.

### 4.5 Telemetry

- **Policy:** Zero telemetry. No data collection of any kind. No opt-in. No opt-out. No phone-home. Ever.

---

## 5. Display Server & Desktop Environment

### 5.1 Display Protocol

- **Target:** Wayland exclusively on Niri profile; Wayland with Xwayland compatibility on KDE profile
- **Xwayland on Niri:** Not available. Niri is a pure Wayland environment.
- **Xwayland on KDE:** Installed as a compatibility shim for legacy applications

### 5.2 Installation Profiles

Four mutually exclusive profiles, selected during installation via TUI:

| Profile | Desktop | Xwayland | Description |
|---|---|---|---|
| **KDE** | KDE Plasma (Wayland session) | Available | Full-featured desktop with custom distro theme + Breeze |
| **Niri** | Niri compositor + custom bar | Not available | Scrollable tiling Wayland compositor with 3–4 curated "rice" presets + vanilla Niri |
| **Combined** | KDE Plasma + Niri | Per-session | Both environments installed, switchable at login via SDDM |
| **Bare** | None | N/A | TTY-only, no graphical environment, no display manager |

### 5.3 Display Manager

- **All graphical profiles:** SDDM (Qt-based, KDE-native)
- **Theming:** Custom distro-branded SDDM theme
- **Bare profile:** No display manager installed

### 5.4 Session Lock

- **KDE profile:** KDE's built-in screen locker
- **Niri profile:** swaylock-effects

---

## 6. Backup & Recovery

### 6.1 System Recovery

- **Primary mechanism:** Boot into a Btrfs snapshot from GRUB menu
- **Fallback:** Installation ISO documented as a rescue/recovery tool (chroot into mounted system, repair bootloader, etc.)
- **Dedicated recovery partition:** None — unnecessary given snapshot-based recovery

### 6.2 User Data Backup

- **Preinstalled tools:** None (no Déjà Dup, Borg, Restic, etc.)
- **Official backup method:** Btrfs send/receive
- **Documentation:** Official docs include a comprehensive guide on using `btrfs send` to snapshot and transfer user data to external drives or remote systems
- **Rationale:** The filesystem already provides the mechanism; adding another tool is redundant

---

## 7. Visual Identity & Theming

### 7.1 Design Philosophy

The distro MUST have a distinctive, instantly recognizable visual identity. This is not a reskinned Fedora. The Niri profile in particular is the flagship showcase — the thing that gets screenshotted and posted.

### 7.2 KDE Plasma Theming

- **Custom theme:** 1 original distro theme (Plasma global theme, color scheme, icon set, wallpaper, SDDM theme — all coordinated)
- **Upstream default:** Breeze also available as a one-click switch
- **Total options:** 2 complete visual presets on KDE

### 7.3 Niri Theming

- **Curated rices:** 3–4 fully coordinated visual presets, each including:
  - Custom status bar configuration and styling (see §8.3)
  - Terminal color scheme
  - Notification daemon styling
  - Wallpaper
  - Lock screen appearance
  - Application launcher theming
  - Consistent color palette across all components
- **Vanilla option:** Stock Niri defaults also available
- **Total options:** 4–5 complete visual presets on Niri
- **Quality bar:** Each rice must be at the level of a polished r/unixporn post. The goal is that users would struggle to replicate the look through manual configuration.

### 7.4 Boot Splash

- **Style:** Minimal branded splash — distro logo with a subtle progress indicator
- **Implementation:** Plymouth theme, coordinated with the overall visual identity

### 7.5 Wallpaper

- **Default:** A single, high-quality, distro-branded wallpaper per profile/theme preset
- **No wallpaper pack:** Wallpapers are tied to theme presets, not shipped as a standalone collection

---

## 8. Default Applications & Tools

### 8.1 Application Selection Philosophy

The distro ships a developer toolchain and system infrastructure. Application-layer software (office suites, media players, email clients, PDF viewers) is the user's choice, installed from repos or Flatpak. The base system is opinionated about *how the OS works*, agnostic about *what the user does with it*.

### 8.2 Preinstalled Applications (All Profiles)

| Category | Application | Notes |
|---|---|---|
| **Shell** | zsh + oh-my-zsh + Powerlevel10k | Default shell for all users. oh-my-zsh `extract` plugin enabled by default. |
| **Editor (terminal)** | Helix | Modal editor with built-in LSP and tree-sitter support |
| **Browser** | Floorp | Firefox-based, sidebar tabs, workspaces, high customization |
| **Image viewer** | nomacs | Qt-based, lightweight, basic editing |
| **Screenshot** | Flameshot | Annotation support, works across all profiles |
| **System monitor** | btop | Terminal-based, visually rich, consistent across profiles |
| **Clipboard** | wl-clipboard + cliphist | Lightweight Wayland-native clipboard history |
| **Dev: C/C++** | gcc, clang, make, cmake, gdb | Full C/C++ toolchain |
| **Dev: General** | git, python3, openssh-client | Essential development tools |
| **Calculator** | bc | Terminal calculator |
| **Archive** | tar, unzip, 7z, p7zip | CLI archive tools; oh-my-zsh `extract` plugin wraps all formats |

### 8.3 Profile-Specific Defaults

| Component | KDE Profile | Niri Profile | Bare Profile |
|---|---|---|---|
| **App launcher** | KDE Kickoff | fuzzel | N/A |
| **File manager** | User's choice (selected during first-boot welcome app with visual preview) | User's choice (selected during first-boot welcome app with visual preview) | N/A |
| **Status bar** | KDE Panel | Custom distro bar (see §7.3) | N/A |
| **Notifications** | KDE notification system | Ecosystem-appropriate daemon | N/A |
| **Session lock** | KDE built-in | swaylock-effects | N/A |
| **Terminal** | User's choice (selected during first-boot welcome app, WezTerm default; options include Tilix, Terminator, Alacritty, Kitty, foot, Ghostty) | Same selection | N/A (system console) |
| **PDF viewer** | None preinstalled | None preinstalled | N/A |
| **Media player** | None preinstalled | None preinstalled | N/A |
| **Office suite** | None preinstalled | None preinstalled | N/A |
| **Email client** | None preinstalled | None preinstalled | N/A |

### 8.4 NOT Preinstalled (Explicitly)

The following categories are deliberately excluded from the base install across all profiles:

- Office suite (LibreOffice, OnlyOffice, etc.)
- Media player (VLC, mpv, etc.)
- PDF viewer (Okular, zathura, etc.)
- Email client (Thunderbird, KMail, etc.)
- Gaming tools (Steam, Lutris, Wine, etc.)
- Terminal web browser
- Docker / Podman
- SSH server (client IS preinstalled — see §4.4)
- Bluetooth stack
- Printing stack (CUPS)
- Accessibility tools (screen reader, magnification) — installable from repos

---

## 9. Distro-Specific Tooling

### 9.1 Custom CLI Tool

- **Scope:** Distro-specific features ONLY. This tool does NOT wrap standard system tools (dnf, btrfs, systemctl).
- **Capabilities:**
  - Theme switching (switch between rice presets)
  - Profile management
  - Font wizard re-run (see §10.2)
  - NVIDIA setup tool invocation (see §9.2)
  - Distro version/info display
- **Name:** `lintactl`

### 9.2 NVIDIA Setup Tool

A dedicated, custom tool for NVIDIA GPU configuration:

- Detects NVIDIA GPU model
- Installs appropriate proprietary driver version
- Configures DKMS for kernel module rebuilds
- Sets Wayland compatibility flags (GBM backend, etc.)
- Configures `prime-run` / `prime-offload` for hybrid laptop GPU switching
- Handles Xwayland (on KDE profile) NVIDIA-specific quirks
- Provides a clear status output: driver version, GPU model, Wayland readiness, hybrid GPU status

### 9.3 Flatpak Manager

A custom GUI application for Flatpak management (see §2.3).

### 9.4 Searchable Keybinding Reference

- **Activation:** A dedicated hotkey opens a searchable, filterable overlay/window listing all keybindings for the current environment
- **Data source:** Reads keybindings from KDE's config (on Plasma) or Niri's config (on Niri)
- **Design:** Fast, keyboard-navigable, visually consistent with the active theme

---

## 10. Installation & First-Boot Experience

### 10.1 Installer

- **Type:** TUI (ncurses-based text installer), similar to Devuan's installer
- **Profile selection:** User selects one of four profiles (KDE, Niri, Combined, Bare)
- **Interactive selections during install:**
  - Hostname (auto-generated memorable name suggested, e.g., `silent-pine`, `brave-otter`; user can accept or edit)
  - Locale (English + user's language)
  - Timezone (manual selection, no geolocation)
  - Disk encryption (LUKS2, offered but off by default)
- **NOT in installer:** Font selection, file manager selection, terminal emulator selection, and theme selection are all deferred to the first-boot experience (§10.2), where the user has a graphical environment and can see visual previews of their choices.

### 10.2 First-Boot Experience

On first boot after installation, the user is presented with a **welcome application** (graphical, Qt-based) covering:

#### Terminal Emulator Selection

- **Visual preview:** Screenshots of each terminal emulator in the distro's theme
- **Default recommendation:** WezTerm (highlighted but not forced)
- **Options:** WezTerm, Tilix, Terminator, Alacritty, Kitty, foot, Ghostty
- **Behavior:** Selected terminal is installed from repos; others are not installed

#### File Manager Selection

- **Visual preview:** Screenshots of each file manager in context
- **Options:** Per-profile (graphical options for KDE/Niri/Combined, terminal-only options for Bare)
- **Behavior:** Selected file manager is installed from repos; others are not installed

#### Font Wizard

- **UI:** A dedicated font selection interface with preset tiers:
  - **Preset 0 (Comprehensive):** All fonts commonly shipped by major distributions — Latin, CJK, Arabic, Cyrillic, emoji, monospace. This is the default.
  - **Preset 1 (Standard):** Major Latin families, one CJK set, emoji, one monospace. Covers most use cases.
  - **Preset 2 (Per-Locale):** Fonts relevant to the user's selected locale(s) + emoji + one monospace.
  - **Preset 3 (Bare Minimum):** Only system-critical fonts required for correct UI rendering.
- **Manual override:** User can toggle individual font families on/off within any preset
- **System font lock:** Fonts required for correct system rendering are locked and cannot be deselected regardless of preset
- **Behavior:** Fonts are installed from repos during this wizard, not bundled on the ISO

#### System Configuration Panel

- **Timezone/locale confirmation** (pre-filled from installer, editable)
- **Theme picker** (select from available rice presets / Breeze on KDE)
- **Quick tips** (non-intrusive, dismissable overview of distro-unique features)

---

## 11. Miscellaneous Policies

### 11.1 Multimedia Codecs & Firmware

- **Firmware blobs:** All shipped — hardware must work out of the box
- **Multimedia codecs:** All proprietary codecs (H.264, H.265, AAC, etc.) included
- **Philosophy:** Pragmatism over ideology. Same approach as EndeavourOS / Manjaro.

### 11.2 USB / Removable Media

- **Behavior:** Auto-mount silently via udisks2 when plugged in. No popup notification.
- **Access:** Device appears in file manager / mount point immediately

### 11.3 Timezone & Clock

- **NTP:** systemd-timesyncd enabled by default
- **Timezone:** Set manually during install. No geolocation services.
- **Hardware clock:** UTC

### 11.4 Text Browser

- **None shipped.** Terminal users on Bare/Niri without a graphical browser are assumed to be capable of installing one.

### 11.5 Dotfile Management

- **Distro policy:** None. Dotfiles are the user's business. The distro ships default configs for its tools (zsh, helix, etc.) but does not impose a dotfile management strategy.

### 11.6 Accessibility

- **Default:** No accessibility tools preinstalled
- **Availability:** Screen reader (Orca), magnification, high-contrast themes available in repos
- **Rationale:** Base system stays lean; users who need accessibility install it

---

## 12. Governance & Community

### 12.1 Governance Model

- **Structure:** Benevolent Dictator — one lead maintainer with final decision-making authority
- **Community contributions:** Welcome (packaging, documentation, theme contributions, bug reports)
- **Decision process:** Community input valued; final say rests with the project lead

### 12.2 Documentation

- **Style:** Curated official documentation maintained by the core team
- **Scope:** Polished, focused, authoritative. Not a community wiki — no unvetted contributions in the official docs.
- **Covers:** Installation guide, first-boot walkthrough, NVIDIA setup, Btrfs snapshot management, Flatpak usage, Niri configuration, theme switching, and all distro-specific tooling

### 12.3 Telemetry

- **None. Ever.** See §4.5.

---

## 13. ISO & Distribution

### 13.1 ISO Strategy

Separate ISO images per profile:

| Profile | Estimated Size | Contents |
|---|---|---|
| **Bare** | ~1.0–1.2 GB | Base system, dev toolchain, shell, helix, firmware, codecs |
| **Niri** | ~1.5–2.0 GB | Bare + Niri compositor, custom bar, rices, Floorp, Flameshot, nomacs, fuzzel |
| **KDE** | ~2.0–2.5 GB | Bare + KDE Plasma, SDDM, Floorp, Flameshot, nomacs, KDE apps |
| **Combined** | ~2.5–3.0 GB | Bare + KDE Plasma + Niri + all associated tooling |

### 13.2 Download Page

- Clear descriptions of each profile with screenshots
- Checksum verification (SHA256)
- Torrent + direct download

---

## 14. Target Audience

Developers and technical power users who want:

- A lean, rolling base that doesn't need babysitting — with instant rollback when it does
- A complete C/C++ (and general) development toolchain ready on first boot
- Beautiful, curated visual presentation without hours of manual ricing
- Wayland-native experience with no legacy X11 baggage (on Niri)
- Full control over application-layer choices — the OS provides infrastructure, the user provides workflow
- Transactional safety and easy rollback when things go wrong
- Zero telemetry, zero bloat, zero unsolicited services

---

## 15. Open Items

The following decisions are deferred to the project lead:

| Item | Status |
|---|---|
| Distribution name | **Resolved: Linta** |
| Release codename theme | Pending — Debian-style thematic codenames, theme TBD |
| Distro motto (final) | Direction: "Lean by design." — final wording TBD |
| Automated testing gate | Needs design spec — openQA? Custom CI? What test coverage? |
| Custom status bar implementation for Niri | Needs design spec — recommend forking Waybar and theming heavily |
| Flatpak manager application | Needs design spec — Qt recommended for KDE consistency. Feature scope? |
| NVIDIA tool implementation | Needs design spec — TUI? CLI? RPM Fusion + akmod as backend? |
| Custom SDDM theme | Needs design — part of the broader visual identity work |
| Keybinding reference tool | Needs design spec — overlay? Standalone window? Rofi-style? |
| Font wizard implementation | Needs design spec — part of the first-boot welcome app (Qt) |
| First-boot welcome app | Needs design spec — Qt, hosts font wizard + terminal/file manager chooser + theme picker |
| Niri rice presets | Need 3–4 complete visual designs with all components specified |
| KDE custom theme | Needs complete Plasma global theme, color scheme, icon set, wallpaper |
| File manager options list | Which file managers are offered in the visual chooser? (Dolphin, Thunar, PCManFM, Nautilus, nnn, ranger, yazi, etc.) |
| Memorable hostname word lists | Need curated adjective + noun lists for auto-generation |
| Email client | Final selection between Claws Mail or Geary (or other lightweight option) |

---

## Appendix A: Complete Decision Log

For traceability, every design decision made during the specification process:

| # | Question | Decision |
|---|---|---|
| 1 | Base lineage | Fedora fork |
| 2 | Init system | systemd |
| 3 | C library | glibc (inherited from Fedora, maximum compatibility) |
| 4 | Release model | Gated rolling release with periodic milestone ISOs (6–12 months) |
| 5 | Package format | Traditional binary packages (RPM) |
| 6 | Package manager philosophy | Transactional (atomic operations, rollback on failure) |
| 7 | Default filesystem | Btrfs (conservative config: CoW, snapshots, zstd compression) |
| 8 | Kernel policy | Latest stable, rolling with automated testing gate |
| 9 | Desktop environment | Four profiles: KDE, Niri, Combined, Bare. Wayland-only. |
| 10 | Documentation | Curated official docs, core-team maintained |
| 11 | Security model | SELinux enforcing (upstream Fedora policies inherited) |
| 12 | Network management | NetworkManager |
| 13 | User privileges | sudo |
| 14 | Display server policy | Niri: pure Wayland. KDE: Wayland + Xwayland. |
| 15 | Audio/BT/Printing | PipeWire preinstalled. BT and printing in repos, not default. |
| 16 | Firewall | firewalld, enabled by default |
| 17 | Boot experience | Minimal branded splash (Plymouth) |
| 18 | Fonts | Font Wizard on first boot with 4 preset tiers (0–3) |
| 19 | Locale | English + user's locale, minimal locale data |
| 20 | Shell | zsh + oh-my-zsh + Powerlevel10k |
| 21 | Community packages | Official repos + Flatpak. No AUR-equivalent. |
| 22 | Update UX | CLI only |
| 23 | Snapshots | Auto before every transaction + weekly Monday 00:00 UTC. Last 5 in GRUB. |
| 24 | Developer tooling | Full suite: gcc, clang, make, cmake, gdb, git, python3 |
| 25 | Containers | Neither Podman nor Docker preinstalled. Both in repos. |
| 26 | Flatpak config | Custom distro GUI frontend + Flathub preconfigured |
| 27 | Logging | journald only |
| 28 | Power management | power-profiles-daemon |
| 29 | Accessibility | Post-install. Tools in repos. |
| 30 | First boot | Font wizard + system configuration panel |
| 31 | Encryption | LUKS2 FDE offered, off by default |
| 32 | Maintenance | Automated: TRIM, log rotation, temp cleanup, cache pruning |
| 33 | Theming | Distinctive original identity. 3–4 Niri rices + vanilla. 1 KDE custom + Breeze. |
| 34 | Notifications | DE-native (KDE notifications / ecosystem-appropriate on Niri) |
| 35 | Backup | Btrfs send/receive, documented in official docs |
| 36 | Installer | TUI (ncurses), Devuan-style. Visual choices (terminal, file manager) deferred to first-boot. |
| 37 | Browser | Floorp |
| 38 | Text editor | Helix |
| 39 | File manager | User selects during first-boot welcome app with visual preview/screenshots |
| 40 | Codecs/firmware | Ship everything. Pragmatism over ideology. |
| 41 | Terminal emulator | User selects during first-boot welcome app (WezTerm default). Options: WezTerm, Tilix, Terminator, Alacritty, Kitty, foot, Ghostty. |
| 42 | App launcher | fuzzel (Niri) / Kickoff (KDE) |
| 43 | Screenshot | Flameshot everywhere |
| 44 | Clipboard | wl-clipboard + cliphist everywhere |
| 45 | System monitor | btop everywhere |
| 46 | Niri status bar | Custom distro-built bar |
| 47 | Screen locker | KDE built-in (Plasma) / swaylock-effects (Niri) |
| 48 | Wallpaper | Single distro-branded wallpaper per theme preset |
| 49 | Media player | None preinstalled |
| 50 | Image viewer | nomacs |
| 51 | PDF viewer | None preinstalled |
| 52 | Email client | Lightweight (Claws Mail or Geary) — TBD final selection |
| 53 | Office suite | None preinstalled |
| 54 | Calculator | bc (terminal) |
| 55 | Archive manager | CLI only (tar, unzip, 7z) + oh-my-zsh `extract` plugin |
| 56 | Terminal browser | None |
| 57 | Color scheme coordination | Full coordination: 3–4 Niri rices (bar, terminal, notifications, wallpaper, locker). 1 KDE custom + Breeze. |
| 58 | Display manager | SDDM |
| 59 | Keybinding philosophy | Upstream defaults + searchable keybinding reference tool |
| 60 | Dotfile management | No opinion — user's business |
| 61 | USB/removable media | Auto-mount silently, no popup |
| 62 | Timezone/clock | NTP enabled, manual timezone, no geolocation |
| 63 | Gaming | No gaming tools preinstalled |
| 64 | NVIDIA | Custom NVIDIA setup tool |
| 65 | System recovery | Boot into GRUB snapshot + documented ISO recovery |
| 66 | Hostname | Auto-generated memorable name (editable) |
| 67 | SSH | Client preinstalled. Server NOT preinstalled. |
| 68 | Distro CLI tool | `lintactl` — Linta-specific features only |
| 69 | Governance | Benevolent dictator |
| 70 | Telemetry | Zero. None. Ever. |
| 71 | Target audience | Developers and technical power users |
| 72 | Name | Linta |
| 73 | Release naming | Debian-style thematic codenames + milestone numbers (e.g., 25.1 "Codename") |
| 74 | ISO size | ~1–3 GB depending on profile (see §13.1) |
| 75 | Motto | Direction: "Lean by design." Final wording TBD. |

---

*This specification is version 2.0, generated from a 75-question design questionnaire with post-review architectural corrections (v1.0→v2.0: musl→glibc, AppArmor→SELinux, SSH client added, point release→gated rolling, visual install choices moved to first-boot). All decisions are subject to revision by the project lead.*
