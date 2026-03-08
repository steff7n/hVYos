# Niri Compositor Guide

Niri is a scrollable tiling Wayland compositor. The Niri profile ships zero Xwayland — it is a pure Wayland environment.

---

## What is Niri

Niri arranges windows in vertical columns that scroll. It is keyboard-driven and highly configurable. Config is written in KDL (KDL Document Language).

---

## Default Keybindings

`Mod` is typically Super (Windows key) or Alt — check `~/.config/niri/config.kdl` for the `modifier` setting.

### General

| Key | Action |
|-----|--------|
| Mod+Return | Open terminal (foot) |
| Mod+D | Application launcher (fuzzel) |
| Mod+Q | Close window |
| Mod+Shift+E | Quit Niri |
| Mod+Shift+/ | Keybinding overlay |

### Focus & Move

| Key | Action |
|-----|--------|
| Mod+Left / Mod+Right | Focus adjacent column |
| Mod+Up / Mod+Down | Focus window up/down |
| Mod+Shift+Left / Right | Move column left/right |
| Mod+Shift+Up / Down | Move window up/down |
| Mod+Home | Focus first column |
| Mod+End | Focus last column |

### Layout

| Key | Action |
|-----|--------|
| Mod+R | Cycle column width presets |
| Mod+F | Maximize column |
| Mod+Shift+F | Fullscreen window |
| Mod+C | Center column |
| Mod+Minus / Mod+Equal | Decrease / increase column width |
| Mod+Shift+Minus / Equal | Decrease / increase window height |

### Workspaces

| Key | Action |
|-----|--------|
| Mod+1 … Mod+5 | Focus workspace 1–5 |
| Mod+Shift+1 … Mod+Shift+5 | Move column to workspace 1–5 |

### Column Management

| Key | Action |
|-----|--------|
| Mod+Comma | Consume window into column |
| Mod+Period | Expel window from column |

### Lock & Screenshot

| Key | Action |
|-----|--------|
| Mod+L | Lock screen (swaylock) |
| Print | Screenshot |
| Ctrl+Print | Screenshot entire screen |
| Alt+Print | Screenshot current window |

### Media

| Key | Action |
|-----|--------|
| XF86AudioRaiseVolume | Volume up |
| XF86AudioLowerVolume | Volume down |
| XF86AudioMute | Toggle mute |

---

## Config File

Main config:

```
~/.config/niri/config.kdl
```

Format is KDL. Basic structure:

```kdl
input {
    keyboard {
        xkb {
            layout "us"
        }
    }
}

layout {
    gaps 8
}

binds {
    Mod+Return { spawn "foot"; }
    Mod+D { spawn "fuzzel"; }
    // ...
}
```

Edit the file and restart Niri (Mod+Shift+E, then log in again) to apply changes. For full syntax and options, see the [upstream Niri documentation](https://niri-project.github.io/niri/).

---

## Status Bar: Waybar

Config:

```
~/.config/waybar/config.jsonc
~/.config/waybar/style.css
```

Theme rices copy their own waybar configs. Reload after editing:

```bash
$ pkill -SIGUSR2 waybar
```

---

## Notifications: mako

Config:

```
~/.config/mako/config
```

Reload:

```bash
$ makoctl reload
```

---

## Launcher: fuzzel

Config:

```
~/.config/fuzzel/fuzzel.ini
```

---

## Lock Screen: swaylock

Config:

```
~/.config/swaylock/config
```

Linta themes provide pre-styled swaylock configs in their rice presets.

---

## Customization

1. Copy the default config from `/etc/skel/.config/niri/config.kdl` if you don't have one
2. Change keybindings in the `binds { }` block
3. Adjust layout (gaps, column widths) in the `layout { }` block
4. Restart Niri to apply

Theme rices modify waybar, mako, fuzzel, and swaylock. Use `lintactl theme set <name>` to switch presets.
