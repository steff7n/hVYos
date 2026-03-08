# Theme Switching

Linta themes are coordinated presets that change the look of your desktop. Switch themes via the CLI.

---

## Commands

**List available themes:**

```bash
$ lintactl theme list
```

The active theme is marked with `*`.

**Set theme:**

```bash
$ lintactl theme set <name>
```

---

## Available Themes

### KDE Profile

| Theme | Description |
|-------|-------------|
| **linta-kde-default** | Linta dark+teal theme ( Plasma global theme, colors, icons, wallpaper) |
| **breeze** | Upstream KDE Breeze |

### Niri Profile

| Theme | Description |
|-------|-------------|
| **linta-niri-rice-1** (Dusk) | Navy base with amber accents |
| **linta-niri-rice-2** (Frost) | Dark base with ice blue accents |
| **linta-niri-rice-3** (Forest) | Green-tinted with emerald accents |
| **linta-niri-rice-4** (Ember) | Charcoal with burnt orange accents |
| **Vanilla** | Stock Niri defaults |

On Combined profile, both KDE and Niri themes are available; the active one depends on which session you use.

---

## What Changes When Switching

- **Niri themes:** Waybar, mako, fuzzel, swaylock configs are copied to `~/.config/` and services are reloaded
- **KDE themes:** Plasma color scheme, icons, wallpaper, and global theme are updated

---

## Theme Files Location

```
/usr/share/linta/themes/<theme-name>/
```

Each theme directory contains:

- `metadata.json` — name, description, profile
- `apply.sh` — script that copies configs and reloads running services
- Component configs (waybar/, mako/, fuzzel/, swaylock/ for Niri rices)

---

## Creating Custom Themes

1. Copy an existing rice directory from `/usr/share/linta/themes/` (e.g. `linta-niri-rice-1`)
2. Rename it and edit `metadata.json` with a new name and description
3. Change colors and styles in waybar, mako, fuzzel, swaylock configs
4. Optionally adjust `apply.sh` for any extra steps
5. Install as a custom package or place in a user theme directory (if supported)
6. Run `lintactl theme set <your-theme-name>`

For package distribution, follow the structure of `linta-theme-niri` and install into `/usr/share/linta/themes/`.
