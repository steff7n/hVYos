# lintactl

Linta Linux system management tool. Handles distro-specific features only.

## Commands

| Command | Description |
|---|---|
| `lintactl info` | Display system info (profile, theme, kernel, Btrfs, SELinux) |
| `lintactl info --json` | Same, but JSON output |
| `lintactl profile` | Show current installation profile |
| `lintactl theme list` | List available themes |
| `lintactl theme set <name>` | Switch the active theme |
| `lintactl nvidia [args]` | Invoke NVIDIA setup tool |
| `lintactl font-wizard` | Re-run the font selection wizard |
| `lintactl snapshot [args]` | Invoke snapshot management tool |

## Profiles

Applies to: **[All]**

## Spec Reference

README.md §9.1
