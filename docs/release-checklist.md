# Linta — Release checklist (first milestone ISO)

Use this checklist to decide when the distro is **ready** for the first milestone (e.g. 25.1). The lead is responsible for driving these items and signing off.

---

## 1. Phases 0–8 complete

| Phase | Description | Sign-off |
|-------|-------------|----------|
| 0 | Scaffolding, manifests, roadmap | ✓ |
| 1 | Kickstarts, package lists, ISO build script | ✓ |
| 2 | lintactl, linta-snapshots, config packages | ✓ |
| 3 | linta-nvidia | ✓ |
| 4 | Themes (KDE, Niri rices, SDDM, Plymouth) | ✓ |
| 5 | linta-welcome, first-boot | ✓ |
| 6 | linta-flatpak-manager | ✓ |
| 7 | linta-keybindings | ✓ |
| 8 | TUI installer | ✓ |

---

## 2. Build verification (container)

On a host with **Podman** or **Docker**, from repo root:

```bash
# Build image (one-time)
./scripts/build-with-container.sh help

# Build all Linta RPMs
./scripts/build-with-container.sh build-rpm-all

# Create local repo (required for ISO)
./scripts/build-with-container.sh create-repo

# Build ISO (requires --privileged; use podman/docker directly)
podman run --rm --privileged -v "$(pwd):/workspace:z" linta-builder build-iso kde
```

- [ ] `build-rpm-all` finishes with 0 failed packages
- [ ] `create-repo` creates `build/output/repo/` with `repodata`
- [ ] `build-iso kde` (or niri/bare/combined) produces `build/output/iso/linta-<profile>-42-x86_64-<date>.iso`

If any step fails, fix before declaring "distro ready".

---

## 3. ISO boot and install

- [ ] ISO boots in QEMU or real hardware
- [ ] TUI installer runs: profile selection, hostname, locale, timezone, disk/partition (Btrfs subvolumes)
- [ ] After install, system boots and first-boot welcome (linta-welcome) can run

Optional: document one-liner QEMU test in `build/testing/` or `docs/installation-guide.md`.

---

## 4. CI and tests

- [ ] `make test` passes (all package + installer + build-with-container tests)
- [ ] `make validate` passes **in container** (manifest + kickstart validation)
- [ ] GitHub Actions CI green (validate-and-test + container-build-and-test)

---

## 5. Docs and artifacts

- [ ] `docs/installation-guide.md` reflects actual install path (installer, first-boot)
- [ ] `docs/first-boot.md` matches linta-welcome flow
- [ ] Wallpapers / logos: `themes/wallpapers/` and any Plymouth/SDDM assets filled or explicitly "placeholder"

---

## 6. Sign-off

**Distro ready for first milestone when:**

- All items in §1–§5 are checked, and  
- At least one profile ISO has been built and boot-tested.

Lead (or delegate) dates and signs:

- **Date:** _______________
- **ISO built:** _______________ (e.g. `linta-kde-42-x86_64-20250309.iso`)
- **Boot tested:** _______________

---

*After first milestone: add version tags (e.g. v25.1), release notes, and optional GitHub Release with ISO artifact.*
