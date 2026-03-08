# Flatpak Usage

Flatpak is Linta's official mechanism for software not in the base repositories. Flathub is preconfigured and available out of the box.

---

## GUI: linta-flatpak-manager

The distro-branded Flatpak manager provides:

- Browsing and searching Flathub
- Installing, updating, and removing Flatpaks
- Managing application permissions

Launch from your application menu or:

```bash
$ linta-flatpak-manager
```

---

## CLI Basics

**Install an application:**

```bash
$ flatpak install flathub <app-id>
```

Example:

```bash
$ flatpak install flathub org.telegram.desktop
```

**List installed applications:**

```bash
$ flatpak list
```

**Update all Flatpaks:**

```bash
$ flatpak update
```

**Uninstall:**

```bash
$ flatpak uninstall <app-id>
```

---

## Managing Permissions

**View an app's permissions:**

```bash
$ flatpak info --show-permissions <app-id>
```

**Override permissions (advanced):** Use [Flatseal](https://flathub.org/apps/com.github.tchx84.Flatseal) from Flathub for a graphical permission editor:

```bash
$ flatpak install flathub com.github.tchx84.Flatseal
```

---

## Why Flatpak

Linta does not provide an AUR-style community repository. For software not in the official repos, Flatpak is the recommended approach:

- Sandboxed runtimes
- Flathub provides a wide catalog
- Install and update without affecting the base system
- No compilation or manual dependency handling
