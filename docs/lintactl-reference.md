# lintactl Command Reference

`lintactl` is the main Linta system management tool. It handles distro-specific features only — it does not wrap standard tools like `dnf`, `btrfs`, or `systemctl`.

---

## info

Display Linta system information.

```bash
$ lintactl info
$ lintactl info --json
```

**Output:** Profile, theme, kernel, Btrfs status, SELinux mode, version.

**Options:**

| Option | Description |
|--------|-------------|
| `--json` | Output in JSON format |

---

## profile

Show the current installation profile.

```bash
$ lintactl profile
```

**Output:** One of `kde`, `niri`, `combined`, or `bare` with a short description.

---

## theme list

List available themes.

```bash
$ lintactl theme list
```

Shows all themes in `/usr/share/linta/themes/`. The active theme is marked with `*`.

---

## theme set

Switch the active theme.

```bash
$ lintactl theme set <name>
```

**Arguments:** `name` — theme directory name (e.g. `linta-niri-rice-1`, `linta-kde-default`).

Runs the theme's `apply.sh` script and records the active theme in `/etc/linta/active-theme`.

---

## nvidia

Invoke the NVIDIA setup tool. All arguments are passed through to `linta-nvidia`.

```bash
$ lintactl nvidia setup
$ lintactl nvidia status
$ lintactl nvidia uninstall
```

Requires `linta-nvidia` to be installed. See [nvidia-setup.md](nvidia-setup.md).

---

## font-wizard

Re-run the font selection wizard from the first-boot experience.

```bash
$ lintactl font-wizard
```

Delegates to `linta-welcome --font-wizard-only`. Requires `linta-welcome` to be installed.

---

## snapshot

Invoke the Btrfs snapshot management tool. All arguments are passed through to `linta-snapshots`.

```bash
$ lintactl snapshot list
$ lintactl snapshot create -d "description"
$ lintactl snapshot rollback <number>
$ lintactl snapshot diff <number>
```

Requires `linta-snapshots` to be installed. See [snapshots.md](snapshots.md).

---

## --version

Show version information.

```bash
$ lintactl --version
```

---

## Subcommand Delegation

`lintactl` delegates to dedicated tools for some subcommands:

| lintactl | Delegates to |
|----------|--------------|
| `nvidia [args]` | `linta-nvidia` |
| `font-wizard` | `linta-welcome --font-wizard-only` |
| `snapshot [args]` | `linta-snapshots` |

If the target tool is not installed, `lintactl` prints an error and suggests installing the corresponding package.
