# linta-welcome

First-boot welcome wizard for Linta Linux.

## What it does

On first login after installation, this PyQt6 wizard guides the user through:

1. **Terminal emulator selection** — visual list with descriptions; only the chosen terminal is installed. Default: WezTerm. Options: WezTerm, Alacritty, Kitty, foot, Ghostty, Tilix, Terminator.

2. **File manager selection** — graphical and terminal options. Default varies by profile (Dolphin for KDE, nnn for Niri).

3. **Font wizard** — 4 preset tiers:
   - Comprehensive: all major font families (Latin, CJK, Arabic, Cyrillic, emoji, monospace)
   - Standard: major Latin + CJK + emoji + monospace
   - Per-Locale: locale-relevant fonts + emoji + monospace
   - Bare Minimum: system-critical fonts only

4. **Theme picker** — select Niri rice preset or KDE theme.

5. **Timezone/locale confirmation** — pre-filled from installer, editable.

6. **Quick tips** — non-intrusive overview of Linta features.

## Re-running

- Full wizard: `linta-welcome`
- Font wizard only: `linta-welcome --font-wizard-only` (or `lintactl font-wizard`)

## First-boot trigger

Uses XDG autostart (`/etc/xdg/autostart/linta-welcome.desktop`) that checks
for `${XDG_STATE_HOME:-$HOME/.local/state}/linta/first-boot-done`. Once the
wizard completes, this per-user marker file is created and the wizard won't run
again automatically for that account.

## Profiles

Applies to: **[KDE]**, **[Niri]**, **[Combined]**

## Spec Reference

README.md §10.2
