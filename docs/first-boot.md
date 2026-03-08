# First-Boot Welcome Wizard

The welcome wizard runs automatically on first boot for KDE, Niri, and Combined profiles. It configures terminal emulator, file manager, fonts, theme, and system settings.

---

## Wizard Steps

### Terminal Emulator Selection

Choose one of seven terminals. **WezTerm is recommended** (highlighted by default). Only the selected terminal is installed.

| Option | Description |
|--------|-------------|
| **WezTerm** | GPU-accelerated, built-in multiplexer, Lua config *(recommended)* |
| Alacritty | GPU-accelerated, minimal, TOML config |
| Kitty | GPU-accelerated, image support, Python extensions |
| foot | Wayland-native, lightweight, fast startup |
| Ghostty | Native platform UI, GPU-accelerated, Zig-based |
| Tilix | GTK tiling terminal, D-Bus integration |
| Terminator | GTK, multiple panes, layout persistence |

### File Manager Selection

**GUI options (8):** Dolphin (KDE), Nautilus (GNOME), Thunar, Nemo, PCManFM-Qt, Caja, Krusader, SpaceFM  

**Terminal options (4):** nnn, ranger, yazi, Midnight Commander

On KDE profile, Dolphin is the default. On Niri, SpaceFM is default. Only the selected file manager is installed.

### Font Wizard

Four preset tiers control which fonts are installed from repositories (fonts are not bundled on the ISO).

| Tier | Name | Description |
|------|------|-------------|
| **0** | Comprehensive | Latin, CJK, Arabic, Cyrillic, emoji, monospace — broad coverage *(default)* |
| 1 | Standard | Major Latin families, one CJK set, emoji, one monospace — typical use |
| 2 | Per-Locale | Fonts for your locale(s) + emoji + one monospace — minimal for your language |
| 3 | Bare Minimum | Only system-critical fonts for correct UI rendering |

System-critical fonts cannot be deselected. You can toggle individual families within any preset.

### Theme Picker

- **Niri / Combined:** Choose a rice preset (Dusk, Frost, Forest, Ember) or Vanilla.
- **KDE:** Choose Linta (dark+teal) or Breeze (upstream KDE).

### Timezone / Locale Confirmation

Values are pre-filled from the installer. Adjust if needed.

### Quick Tips

A short overview of Linta-specific features: keybindings, snapshots, Flatpak, theme switching.

---

## Re-Running the Wizard

**Full welcome wizard:**

```bash
$ linta-welcome
```

**Font wizard only** (e.g. to add or remove font families later):

```bash
$ lintactl font-wizard
```

Or directly:

```bash
$ linta-welcome --font-wizard-only
```

---

## Profiles

The welcome wizard applies to **KDE**, **Niri**, and **Combined** profiles. The **Bare** profile has no graphical environment and does not run the wizard.
